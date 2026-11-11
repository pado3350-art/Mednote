"""Stage 4: check the generated note against the source slides/script."""
from __future__ import annotations

import re

from .align_content import _bigrams, _cosine
from ..design.diagrams import diagram_has_exam, diagram_texts
from ..pad.exam import EXAM_BASE
from ..markup import LEAK, PAD_TAGS, runs as _runs, strip as _strip_markup
from ..models import AlignedSlide, Issue, LectureNote, Slide, ValidationReport
from ..template import Template

# number with optional unit, e.g. 5.5 mg/dL, 40%, 2 mm, 1.5x
_NUM = re.compile(r"(?<![A-Za-z0-9])\d+(?:[.,]\d+)?\s*(?:%|mg/dL|mg/kg|mg|mcg|μg|µg|g/dL|g|kg|mL|L|mm|cm|mmHg|mEq/L|IU|U|°C|bpm|x|배|일|주|개월|년|세|시간|분)?")
# English medical terms / acronyms: Capitalised words (len>=3) or ALLCAPS (>=2)
_TERM = re.compile(r"\b(?:[A-Z]{2,}(?:[A-Za-z0-9]|-(?=[A-Za-z0-9]))*|[A-Z][a-z]{3,}(?:\s+[a-z]{3,})?)\b")
_GROUND_MIN = 0.12


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", s).lower()


def _note_text(note: LectureNote) -> str:
    parts = []
    for t in note.topics:
        parts.append(t.heading)
        parts += [_strip_markup(t.tip)] + [_strip_markup(b) for b in t.basics]
        for sts in t.sections.values():
            for s in sts:  # row2 keeps the slide original in `left`, quiz keeps options / answer
                parts += [_strip_markup(x) for x in (s.text, s.left_title, *s.left, *s.options, s.answer, *s.explanations,
                                                     *s.col_titles, *[c for r in s.rows for c in r]) if x]
                if s.kind == "columns" and s.diagram is not None:
                    for g in s.diagram.groups:
                        parts += [_strip_markup(x) for x in (g.title, *g.items) if x]
        for tb in t.tables:
            parts += [" ".join(r) for r in tb.rows]
    return "\n".join(parts)


def validate(
    note: LectureNote,
    slides: list[Slide],
    aligned: list[AlignedSlide],
    template: Template,
) -> ValidationReport:
    rep = ValidationReport()

    def uname(n: int) -> str:
        if n >= EXAM_BASE:
            return note.unit_labels.get(n, f"PAD {n - EXAM_BASE}")
        if n == 0:
            return "검증 참고 문단"
        return f"발화 ¶{n}" if note.ref_style == "para" else f"슬라이드 {n}"

    rep.unit_names = {s.number: uname(s.number) for s in slides}
    full = _norm(_note_text(note))
    by_slide = {s.number: s for s in slides}
    amap = {a.slide_number: a for a in aligned}
    seg_text = {g.id: g.text for a in aligned for g in a.segments}

    # 1. Slide coverage
    covered = {n for t in note.topics for n in t.slide_numbers}
    missing = sorted(set(by_slide) - covered)
    content_total = sum(1 for n in by_slide if n < EXAM_BASE)
    cited_pad = {r for t in note.topics for sts in t.sections.values() for st in sts for r in st.slide_refs if r >= EXAM_BASE}
    cited_pad |= {r for t in note.topics for r in t.basics_refs if r >= EXAM_BASE}
    for n in missing:
        if n >= EXAM_BASE and not template.format.exam_section and n in cited_pad:
            continue  # reflected as blue statements
        if (n >= EXAM_BASE and not template.format.exam_section and note.meta.get("pad_uncovered_mode") == "omit"
                and str(n) in (note.meta.get("pad_uncovered_units") or "").split(",")):
            continue  # --uncovered-pad omit: the handout writer says this was never taught, leaving it out is allowed
        if n >= EXAM_BASE and not template.format.exam_section:
            # PAD is only a colour reference when there is no standalone 기출 section
            rep.issues.append(Issue(severity="warning", code="PAD_UNUSED", slide=n,
                                    message=f"{uname(n)} 문항 내용이 본문에 파랑으로 반영되지 않았습니다 (기출은 빠짐없이 표시해야 함)."))
            continue
        rep.issues.append(Issue(severity="error", code="SLIDE_MISSING", slide=n,
                                message=f"{uname(n)}이(가) 강의록에 반영되지 않았습니다."))
    miss_content = sum(1 for n in missing if n < EXAM_BASE)
    rep.slide_coverage = 1 - miss_content / content_total if content_total else 1.0

    # 2. Numbers/units and key terms preserved (numbers the author dropped on purpose are listed in meta.omitted, "a|b|c")
    omitted = {_norm(x) for x in (note.meta.get("omitted") or "").split("|") if x.strip()}
    # English glosses of the transcript ("스페시멘(Specimen)", "옵티멀(Optimal)") that are not needed to understand or pass:
    # leave them out of the text on purpose instead of forcing a parenthesis into every sentence (meta.omitted_terms "a|b|c")
    omitted_terms = {_norm(x) for x in (note.meta.get("omitted_terms") or "").split("|") if x.strip()}
    for n, s in by_slide.items():
        if n in missing:
            continue
        # a PAD unit's generated title ("기출 2022년 …") is metadata, not content: only its question/answer/commentary count
        src = " ".join(b.text for b in s.body) if n >= EXAM_BASE else s.plain_text()
        for m in sorted({x.group().strip() for x in _NUM.finditer(src)}):
            if len(re.sub(r"\D", "", m)) == 0:
                continue
            if n >= EXAM_BASE and re.fullmatch(r"[1-9]", m):  # PAD answer-option labels (1) 2) 3 ...) are numbering, not content
                continue
            if _norm(m) not in full and _norm(m) in omitted:
                rep.issues.append(Issue(severity="info", code="OMITTED_BY_RULE", slide=n,
                                        message=f"수치 '{m}'은(는) 사소한 내용이라 의도적으로 뺐습니다(meta.omitted)."))
                continue
            if _norm(m) not in full:
                rep.issues.append(Issue(severity="error", code="NUMBER_LOST", slide=n,
                                        message=f"수치 '{m}'이(가) 강의록에서 누락/변형되었습니다."))
        if template.quality.preserve_all_key_concepts and n < EXAM_BASE:  # PAD distractors need not be echoed
            for term in sorted({x.group() for x in _TERM.finditer(src)}):
                if _norm(term) not in full and _norm(term) in omitted_terms:
                    rep.issues.append(Issue(severity="info", code="OMITTED_BY_RULE", slide=n,
                                            message=f"용어 '{term}'은(는) 사소한 영어 병기라 의도적으로 뺐습니다(meta.omitted_terms)."))
                elif _norm(term) not in full:
                    rep.issues.append(Issue(severity="warning", code="TERM_LOST", slide=n,
                                            message=f"용어 '{term}'이(가) 강의록에 없습니다."))
        # 3. Tables / images retained
        topic = next((t for t in note.topics if n in t.slide_numbers), None)
        if topic and template.format.tables_for_comparisons and len(s.tables) > 0:
            if len(topic.tables) < len(s.tables):
                rep.issues.append(Issue(severity="error", code="TABLE_LOST", slide=n,
                                        message="슬라이드의 표가 강의록에서 누락되었습니다."))
        if template.format.preserve_original_images and s.images:
            placed = {img for t in note.topics for img in t.images} | {
                st.image for t in note.topics for sts in t.sections.values() for st in sts if st.kind == "figure"}
            if any(img not in placed for img in s.images):
                rep.issues.append(Issue(severity="error", code="IMAGE_LOST", slide=n,
                                        message="슬라이드의 이미지가 강의록에서 누락되었습니다."))

    # 4. Traceability / grounding of every statement
    for t in note.topics:
        for key, sts in t.sections.items():
            for st in sts:
                if st.kind in ("figure", "diagram"):
                    continue
                if st.kind == "check":
                    if st.answer not in ("O", "X"):
                        rep.issues.append(Issue(severity="error", code="CHECK_BAD_ANSWER", slide=None,
                                                message=f"개념 Check의 정답은 O 또는 X여야 합니다: '{st.text[:30]}…'"))
                    if st.slide_refs and t.slide_numbers and not set(st.slide_refs) <= set(t.slide_numbers):
                        rep.issues.append(Issue(severity="warning", code="CHECK_NOT_GROUNDED", slide=st.slide_refs[0],
                                                message=f"개념 Check는 같은 § 안의 내용으로 풀려야 합니다(출처 {st.slide_refs}가 § 범위 밖): '{st.text[:30]}…'"))
                if st.origin == "author":  # the writer's own addition (analogy / tip): no source needed, still no blue without PAD
                    continue
                if st.kind != "star" and template.quality.require_source_traceability and not st.slide_refs and not st.segment_ids:
                    rep.issues.append(Issue(severity="error", code="NO_SOURCE", slide=None,
                                            message=f"출처 없는 문장: '{st.text[:40]}…'"))
                    continue
                if any(r not in by_slide for r in st.slide_refs):
                    rep.issues.append(Issue(severity="error", code="BAD_REF", slide=None,
                                            message=f"존재하지 않는 출처 참조: {st.slide_refs}"))
                    continue
                if st.kind == "star":  # short sub-headings carry no claim
                    continue
                source = " ".join(
                    [by_slide[r].plain_text() for r in st.slide_refs]
                    + [seg_text.get(i, "") for i in st.segment_ids]
                )
                claim = st.text if st.kind not in ("rows", "qa") else " ".join([st.text, *st.left, *[c for r in st.rows for c in r]])
                if not claim.strip():
                    continue
                if _cosine(_bigrams(_strip_markup(claim)), _bigrams(source)) < _GROUND_MIN:
                    rep.issues.append(Issue(severity="warning", code="UNGROUNDED",
                                            slide=st.slide_refs[0] if st.slide_refs else None,
                                            message=f"원본과 유사도가 낮은 문장(근거 확인 필요): '{_strip_markup(claim)[:40]}…'"))

    # 4b. Colour rule (NON-NEGOTIABLE): BLUE = content that appeared in the PAD (기출) - nothing else.
    #     * blue text must cite a PAD unit;  * a statement citing a PAD unit must be blue
    #       (unless it is purely gray/purple meta commentary);  * the 기본정석 box follows the same rule.
    def _is_blue(text: str, tag: str = "normal") -> bool:
        return tag in PAD_TAGS or any(c in PAD_TAGS for _, c, _ in _runs(text))

    def _all_text(st) -> str:  # row2 / quiz keep text in several fields
        return " ".join([st.text, *st.left, *st.options, st.answer, *st.explanations, *st.col_titles, *[c for r in st.rows for c in r]])

    two_blues = any(i.tag == "exam_other" for i in template.format.legend)  # template declares the 2nd blue
    cur_prof = (note.meta.get("professor") or "").replace("교수님", "").strip()

    def _same_prof(p: str) -> bool:
        p = p.replace("교수님", "").strip()
        return bool(cur_prof) and bool(p) and (cur_prof in p or p in cur_prof)

    for t in note.topics:
        for sts in t.sections.values():
            for st in sts:
                if st.kind in ("diagram", "figure_side", "concept") and st.diagram is not None:
                    if diagram_has_exam(st.diagram) and not any(r >= EXAM_BASE for r in st.slide_refs):
                        rep.issues.append(Issue(severity="error", code="BLUE_WITHOUT_PAD",
                                                slide=st.slide_refs[0] if st.slide_refs else None,
                                                message=f"도식의 파랑에 PAD 출처가 없습니다: '{st.text[:30]}…'"))
                if st.kind in ("figure", "diagram"):
                    continue
                has_pad = any(r >= EXAM_BASE for r in st.slide_refs)
                blue = _is_blue(_all_text(st), st.tag)
                if two_blues and cur_prof and has_pad:
                    profs = [note.pad_professors.get(r, "") for r in st.slide_refs if r >= EXAM_BASE]
                    tags = {c for _, c, _ in _runs(_all_text(st)) if c}
                    if "exam" in tags and profs and not any(_same_prof(p) for p in profs):
                        rep.issues.append(Issue(severity="error", code="BLUE_WRONG_PROFESSOR", slide=st.slide_refs[0],
                                                message=f"진한 파랑은 담당 교수님({cur_prof}) 파드 전용인데 다른 교수님 파드만 인용했습니다: '{_strip_markup(st.text)[:36]}…'"))
                    if "exam_other" in tags and profs and all(_same_prof(p) for p in profs):
                        rep.issues.append(Issue(severity="error", code="BLUE_WRONG_PROFESSOR", slide=st.slide_refs[0],
                                                message=f"하늘색은 다른 교수님 파드 전용인데 담당 교수님 파드를 인용했습니다: '{_strip_markup(st.text)[:36]}…'"))
                if blue and not has_pad:
                    rep.issues.append(Issue(severity="error", code="BLUE_WITHOUT_PAD",
                                            slide=st.slide_refs[0] if st.slide_refs else None,
                                            message=f"파랑은 기출(PAD) 내용 전용인데 PAD 출처가 없습니다: '{_strip_markup(st.text)[:40]}…'"))
                meta_only = st.tag in ("minor", "verify") or all(
                    c in ("minor", "verify") for _, c, _ in _runs(st.text) if c)  and any(c for _, c, _ in _runs(st.text))
                if has_pad and not blue and st.kind != "star" and not meta_only:
                    rep.issues.append(Issue(severity="error", code="PAD_NOT_BLUE",
                                            slide=st.slide_refs[0],
                                            message=f"기출(PAD)에 나온 내용은 반드시 파랑이어야 합니다: '{_strip_markup(st.text)[:40]}…'"))
        has_pad_box = any(r >= EXAM_BASE for r in t.basics_refs)
        for line in t.basics:
            if _is_blue(line) and not has_pad_box:
                rep.issues.append(Issue(severity="error", code="BLUE_WITHOUT_PAD",
                                        slide=t.slide_numbers[0] if t.slide_numbers else None,
                                        message=f"기본정석 박스의 파랑에 PAD 출처(basics_refs)가 없습니다: '{_strip_markup(line)[:40]}…'"))

    # 4c. Unrendered markup (stray '*' or '{x|') would show up literally in the document
    for t in note.topics:
        dia_texts = [tx for sts in t.sections.values() for x in sts if x.kind in ("diagram", "figure_side", "concept") and x.diagram
                     for tx in diagram_texts(x.diagram)]
        for text in [_all_text(x) for sts in t.sections.values() for x in sts if x.kind not in ("figure", "diagram")] + list(t.basics) + [t.tip] + dia_texts:
            left = _strip_markup(text)
            if "*" in left or LEAK.search(left):
                rep.issues.append(Issue(severity="warning", code="MARKUP_LEAK",
                                        slide=None, message=f"렌더링되지 않는 서식 기호가 남아 있습니다: '{left[:40]}…'"))

    # 4c-2. One fact per line (approved rule L1): a long line glued together with dashes / middle dots is too dense
    for t in note.topics:
        for sts in t.sections.values():
            for st in sts:
                lines = [st.text, *st.left] + ([i for g in st.diagram.groups for i in g.items] if st.kind == "columns" and st.diagram else []) \
                    + [ln for r in st.rows for c in r for ln in c.split("\n")]
                for line in lines:
                    plain = _strip_markup(line)
                    if len(plain) > 60 and plain.count("—") + plain.count("·") >= 2:
                        rep.issues.append(Issue(severity="warning", code="LINE_TOO_DENSE", slide=st.slide_refs[0] if st.slide_refs else None,
                                                message=f"한 줄에 사실을 몰아넣었습니다(—/· 연결, {len(plain)}자): '{plain[:40]}…'"))

    # 4c-3. Mixed style (default, approved rule L10): explain § vs list § conventions
    if template.format.mixed:
        from .mixed import mixed_issues, table_orphan_issues, table_style_issues

        for sev, code, msg in mixed_issues(note) + table_orphan_issues(note) + table_style_issues(note):
            rep.issues.append(Issue(severity=sev, code=code, slide=None, message=msg))

    # 4c-3b. Uncommon Korean terms need English (approved rule L25)
    from .storyline import heading_form_issues, keyword_heading_issues
    from .terms import term_issues

    for sev, code, msg in term_issues(note) + keyword_heading_issues(note) + heading_form_issues(note):
        rep.issues.append(Issue(severity=sev, code=code, slide=None, message=msg))

    # 4c-4. Concept boxes are drawn, not only written (L15): slide picture first, else a program schematic
    if template.format.mixed:
        for t in note.topics:
            for sts in t.sections.values():
                for st in sts:
                    if st.kind == "concept" and not st.image and st.diagram is None:
                        rep.issues.append(Issue(severity="warning", code="CONCEPT_NO_VISUAL", slide=st.slide_refs[0] if st.slide_refs else None,
                                                message=f"개념 정리 '{_strip_markup(st.left_title)[:30]}'에 그림이 없습니다. 강의자료 그림(image)을 우선 붙이고, "
                                                        "없으면 도식(diagram: pyramid/flow/cycle/compare/tree)을 넣습니다."))

    # 4d. The 요약 정리 page must carry a visual (schematic or figure)
    for t in note.topics:
        if t.role == "front" and "요약" in t.heading:
            if not any(x.kind in ("diagram", "figure") for sts in t.sections.values() for x in sts):
                rep.issues.append(Issue(severity="warning", code="SUMMARY_NO_VISUAL", slide=None,
                                        message="요약 정리에 도식이나 그림이 없습니다 (핵심 요약은 시각 자료를 포함해야 함)."))

    # 5. Alignment confidence & script segments dropped
    placed_ids = {i for t in note.topics for sts in t.sections.values() for s in sts for i in s.segment_ids}
    for a in aligned:
        for g in a.segments:
            if g.id not in placed_ids:
                rep.issues.append(Issue(severity="error", code="SEGMENT_LOST", slide=a.slide_number,
                                        message=f"교수 설명(발화 {g.id})이 강의록에 반영되지 않았습니다."))
        if a.low_confidence_segment_ids and not note.meta.get("alignment_reviewed"):
            rep.issues.append(Issue(severity="warning", code="LOW_ALIGNMENT", slide=a.slide_number,
                                    message=f"발화 {a.low_confidence_segment_ids} 정렬 신뢰도 낮음"))
    for f in note.review_flags:
        rep.issues.append(Issue(severity="info", code="REVIEW_FLAG", message=f))
    for t in note.topics:
        for f in t.review_flags:
            rep.issues.append(Issue(severity="info", code="REVIEW_FLAG",
                                    slide=t.slide_numbers[0] if t.slide_numbers else None, message=f))
    return rep


def report_markdown(rep: ValidationReport) -> str:
    icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}
    lines = [f"# 검증 리포트", "",
             f"- 슬라이드 커버리지: {rep.slide_coverage:.0%}",
             f"- 오류 {len(rep.errors)} / 경고 {sum(i.severity=='warning' for i in rep.issues)}"
             f" / 참고 {sum(i.severity=='info' for i in rep.issues)}", ""]
    for i in sorted(rep.issues, key=lambda x: (x.slide or 0, x.severity)):
        where = f"[{rep.unit_names.get(i.slide, f'슬라이드 {i.slide}')}] " if i.slide else ""
        lines.append(f"- {icon[i.severity]} `{i.code}` {where}{i.message}")
    return "\n".join(lines) + "\n"

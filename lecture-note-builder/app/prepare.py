"""`prepare`: build a work packet so Claude Code (a normal Claude Code session - no API key, no extra cost
beyond the user's own plan) can author the note itself with the `make-lecture-note` skill.

Writes  <out>/brief/ :  TASK.md  paragraphs.md  exam_items.md  figures.md  outline_proposal.json
                        note_skeleton.json  note_schema.json  build_command.sh
"""
from __future__ import annotations

import json
import shlex
from pathlib import Path

from .exam import EXAM_BASE, parse_exam_pdf
from .figures import collect_figures, save_figures
from .models import Topic
from .outline import heuristic_outline, normalize_outline
from .pipeline import _units_from_segments
from .transcript import parse_flow_script, read_script_text


# Lecturer cues about how much effort a passage deserves -> suggested `effort` tag (a human/Claude decides).
EFFORT_CUES: list[tuple[str, str]] = [
    (r"외울\s*필요\s*(?:는\s*)?없|외우(?:지|실)\s*(?:않아도|필요\s*없)|몰라도|안\s*외워|들어만|가볍게|넘어가|그렇다\s*수준|이름\s*정도만|참고(?:로|만)|상식\s*(?:차원|수준)|굳이", "참고"),
    (r"꼭\s*(?:외|기억|보)|반드시|맨날\s*나|시험에\s*(?:도\s*)?(?:많이\s*)?나|출제|무조건|중요(?:합니다|한 것|해요)|핵심(?:이다|입니다)|기억해\s*(?:두|놓)", "필수"),
    (r"이해(?:해|하)(?:\s*(?:보|두)|야)|원리|왜\s", "이해"),
]


def effort_cues(segs) -> list[tuple[int, str, str, str]]:
    """-> [(paragraph id, suggested effort, matched cue, sentence)] for paragraphs where the lecturer signals importance."""
    import re

    out = []
    for g in segs:
        if g.kind != "speech":
            continue
        for sent in re.split(r"(?<=[.?!])\s+", g.text):
            for pat, eff in EFFORT_CUES:
                m = re.search(pat, sent)
                if m:
                    out.append((g.id, eff, m.group(0).strip(), sent.strip()[:160]))
                    break
    return out


def prepare_brief(script: str | Path, out_dir: str | Path, template: str | Path, exam_pdf: str | Path | None = None,
                  figures: list[str | Path] | None = None, extra_args: str = "") -> Path:
    out = Path(out_dir)
    brief = out / "brief"
    brief.mkdir(parents=True, exist_ok=True)
    meta, segs = parse_flow_script(read_script_text(script))
    units = _units_from_segments(segs)
    notes = [g.id for g in segs if g.kind == "note"]
    speech = [g.id for g in segs if g.kind == "speech"]

    # paragraphs
    L = [f"# 강의 발화 단락 ({len(segs)}개)", "", "번호 ¶n 은 note의 `slide_refs`에 그대로 쓴다. `[검증참고]`는 부록 재료.", ""]
    for g in segs:
        L.append(f"**¶{g.id}**{' [검증참고]' if g.kind == 'note' else ''} {g.text}\n")
    (brief / "paragraphs.md").write_text("\n".join(L), encoding="utf-8")

    # PAD
    items = parse_exam_pdf(exam_pdf) if exam_pdf else []
    E = [f"# 기출(PAD) {len(items)}문항", "",
         "⛔ 파랑(`{b|...}`)은 여기 나온 내용에만. 해당 내용은 빠짐없이 파랑 + `slide_refs`에 아래 unit 번호를 넣는다.", ""]
    for it in items:
        E.append(f"## unit {it.number} — {it.label} ({it.professor})\n- 문제: {it.question}\n- 정답: {it.answer}\n- 해설: {it.commentary or '(없음)'}\n")
    (brief / "exam_items.md").write_text("\n".join(E) if items else "# 기출(PAD) 없음\n\n파랑 글씨를 쓰지 않는다.\n", encoding="utf-8")

    # figures
    figs = collect_figures(figures, out / "figures") if figures else []
    F = [f"# 그림·사진 자료 {len(figs)}개", "",
         "이미지 파일은 Read 도구로 직접 볼 수 있다. 배치는 `build`가 자동으로 하고 `figures.json`으로 고친다 "
         "(`topic_heading`, `anchor`(★ 소제목 일부), `caption`, `skip`). `text_like`=글자뿐인 슬라이드(기본 제외).", ""]
    for f in figs:
        F.append(f"- id {f.id} · {f.source} p.{f.page} · {f.width}x{f.height}{' · TEXT-ONLY' if f.text_like else ''}\n  - 파일: {f.path}\n  - 근처 글: {f.near[:140] or '(없음)'}")
    (brief / "figures.md").write_text("\n".join(F), encoding="utf-8")
    if figs:
        save_figures(figs, brief / "figures_extracted.json")

    # outline proposal + skeleton
    ol = normalize_outline(heuristic_outline([u for u in units if u.number in set(speech)]), speech, notes)
    (brief / "outline_proposal.json").write_text(json.dumps(ol.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    skel = {"topics": [Topic(heading=i.heading, chapter=i.chapter, slide_numbers=i.unit_numbers,
                             sections={"body": []}).model_dump() for i in ol.items]}
    (brief / "note_skeleton.json").write_text(json.dumps(skel, ensure_ascii=False, indent=2), encoding="utf-8")
    (brief / "note_schema.json").write_text(json.dumps(Topic.model_json_schema(), ensure_ascii=False, indent=2), encoding="utf-8")

    # effort cues (필수 / 이해 / 참고) found in the lecturer's own words
    cues = effort_cues(segs)
    EC = [f"# 노력 수준 단서 {len(cues)}개 (제안일 뿐 — 문맥을 보고 `effort`를 정한다)", "",
          "교수 발언에서 ‘외워라/안 외워도 된다/참고만/시험에 나온다’ 같은 신호가 있는 문장. 노트에는 해당 문장 끝에 `effort`(필수/이해/참고)로 표시한다. "
          "⛔ 파랑은 기출(PAD) 전용이므로 노력 수준을 파랑으로 표시하지 않는다.", ""]
    EC += [f"- ¶{i} [{e}] “{cue}” — {sent}" for i, e, cue, sent in cues]
    (brief / "effort_cues.md").write_text("\n".join(EC) + "\n", encoding="utf-8")

    # rules the user approved from their own edits (none approved -> short notice)
    from .feedback import approved_rules_markdown

    (brief / "learned_rules.md").write_text(
        approved_rules_markdown() or "# 승인된 학습 규칙 없음\n\n`/learn-mednote-style`로 수정본을 비교해 승인하면 여기에 나타난다.\n",
        encoding="utf-8")

    # build command
    args = ["python", "-m", "app.cli", "build", "--script", str(script), "--template", str(template),
            "--note-json", str(out / "note_authored.json"), "--out", str(out)]
    if exam_pdf:
        args += ["--exam-pdf", str(exam_pdf)]
    if figures:
        args += ["--figures", *map(str, figures)]
    cmd = " ".join(shlex.quote(a) for a in args) + (" " + extra_args if extra_args else "")
    (brief / "build_command.sh").write_text(cmd + "\n", encoding="utf-8")

    (brief / "TASK.md").write_text(f"""# 작업: 강의록 작성 (API 없이, Claude Code가 직접)

입력: 발화 단락 {len(segs)}개(검증참고 {len(notes)}개), 기출 {len(items)}문항, 그림 {len(figs)}개. 메타: {json.dumps(meta, ensure_ascii=False)}

## 순서
0. `brief/learned_rules.md`(사용자가 승인한 학습 규칙)를 읽고 따른다. 강의 유형에 맞는 규칙만 적용한다.
1. `.claude/skills/readable-note-organizer/SKILL.md`를 읽는다. **맨 위 ⛔ 파랑 = PAD 기출 ONLY 규칙은 무조건 지킨다.**
2. `brief/effort_cues.md`(교수가 말한 노력 수준 단서)도 읽는다. `brief/paragraphs.md`(모든 발화), `brief/exam_items.md`(기출), `brief/figures.md`(그림; 이미지는 Read로 직접 본다)를 읽는다.
3. 목차를 판단한다: 챕터 2~4개 × § 소절 2~4개. `outline_proposal.json`은 기계적 초안일 뿐이다. 모든 발화 단락(검증참고 제외)이 정확히 한 소절에 들어가야 하고, 검증참고는 마지막 `부록 & 검증 참고`.
4. `{out}/note_authored.json`을 작성한다 (스키마: `brief/note_schema.json`, 예: `examples/limbic_note.py` 의 헬퍼 P·B·STAR·ADV·REF·T 로 Python 스크립트를 쓰는 방식 권장).
   - 소절마다 기본정석 박스(`basics`, `basics_refs`), 설명 순서로 재구성한 본문, Advice/Reference, 비교표.
   - 앞쪽에 `role: "front"` 두 장: 핵심 어휘, 요약 정리.
   - 모든 문장에 `slide_refs`(¶번호, PAD는 unit 번호).
   - **표지 정보** `{out}/meta.json`도 쓴다: `comment`(노트 소개·강의 성격·주의), `tips`(공부 전략 2~4줄, 노란 형광펜: 무엇을 먼저/가볍게, 기출 집중 구간), `objectives`(학습목표 3~6줄). 빌드 때 `--meta-json {out}/meta.json`을 붙인다.
   - 소절마다 `tip`(공부 우선순위 한 줄), 슬라이드 원문은 `row2`(영문 | 한글 설명) 표, 강의 중 퀴즈는 `quiz`. 말투는 스킬의 3절(문장 기능별 어미)을 따른다.
5. 빌드: `bash {brief / 'build_command.sh'}`  (그림은 자동 배치됨)
6. `{out}/validation_report.md`를 읽고 **오류 0, 경고 최소**가 될 때까지 고친다 (BLUE_WITHOUT_PAD, PAD_NOT_BLUE, SLIDE_MISSING, NUMBER_LOST, MARKUP_LEAK ...).
7. PDF 페이지를 이미지로 열어 그림 위치를 확인하고, 어긋난 그림은 `{out}/figures.json`을 고쳐 `--figures-json`으로 재적용한다.
""", encoding="utf-8")
    return brief

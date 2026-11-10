"""Feedback learning, steps 2-4: classify the user's edits, propose rule candidates, and keep the APPROVED rules.

    original.docx + edited.docx --diff--> report (JSON + Markdown) with candidates, all `pending`
                                  --approve (user decision only)--> style_rules/approved_rules.json

Approval gate: `build_report` never writes the rule store. Generation reads only rules whose status is
"approved" (see `approved_rules_markdown`); with no store the generator behaves exactly as before.
Medical-fact edits are never generalised into style rules: they become lecture-specific correction records.
"""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from typing import Literal, Optional

from pydantic import BaseModel, Field

from .docx_diff import Change, diff_docs, extract_docx

ROOT = Path(__file__).resolve().parent.parent
RULE_STORE = ROOT / "style_rules" / "approved_rules.json"

CATEGORIES = {
    "style": "문체",
    "structure": "구성",
    "depth": "설명 깊이",
    "terminology": "용어",
    "format": "서식",
    "medical_fact": "의학적 사실",
}
LECTURE_TYPES = {
    "all": "모든 강의",
    "concept_chain": "개념·기전 연쇄형 (mom.yaml, 스토리 서술)",
    "list_intro": "나열형·인트로 (mom_compact.yaml, 개조식)",
    "clinical": "임상 강의 (mom_clinical.yaml)",
}

_NUM = re.compile(r"\d+(?:[.,]\d+)*\s*(?:%|mg|g|kg|mL|ml|L|mmHg|mm|cm|회|배|명|세|년|개월|주|일|시간|분|번)?")
_LATIN = re.compile(r"[A-Za-z][A-Za-z0-9\-]{1,}")
_NEG = ("않", "없", "아니", "못", "불가", "금기", "not ", "no ")
_ATTRIB = ("교수님", "하셨", "말씀", "강조하")
_FORMAL = re.compile(r"(습니다|입니다|됩니다|합니다|세요|어요|아요|예요|이에요|죠)[.!?]?\s*$")
_PLAIN = re.compile(r"(한다|이다|된다|있다|없다|는다|았다|었다|하자|보자)[.!?]?\s*$")


def _nums(text: str) -> list[str]:
    return sorted(re.sub(r"\s+", "", m) for m in _NUM.findall(text))


def _latin(text: str) -> set[str]:
    return {m.lower() for m in _LATIN.findall(text)}


def classify(c: Change) -> None:
    """Fill c.categories (all that apply), c.category (primary) and c.signals (pattern keys)."""
    cats: list[str] = []
    sig: list[str] = []
    a, b = c.before, c.after

    if c.type == "table_shape":
        cats.append("structure"); sig.append("table_shape")
    elif c.type == "moved":
        cats.append("structure"); sig.append("moved")
    elif c.type == "format":
        cats.append("format")
    elif c.type in ("inserted", "deleted"):
        if c.kind == "heading":
            cats.append("structure"); sig.append(f"heading_{c.type}")
        else:
            cats.append("depth"); sig.append(f"{c.kind}_{c.type}")

    if c.bold_added:
        sig.append("bold_added")
    if c.bold_removed:
        sig.append("bold_removed")
    for ch in c.color_changes:
        sig.append("color:" + ch.rsplit(": ", 1)[-1])
    if (c.bold_added or c.bold_removed or c.color_changes) and "format" not in cats:
        cats.append("format")

    if c.type in ("modified", "moved") and a != b:
        if "heading" in c.kind:
            cats.append("structure"); sig.append("heading_renamed")
        na, nb = _nums(a), _nums(b)
        la, lb = _latin(a), _latin(b)
        neg_a, neg_b = sum(a.count(w) for w in _NEG), sum(b.count(w) for w in _NEG)
        if na != nb:
            cats.append("medical_fact"); sig.append("number_changed")
        elif neg_a != neg_b and c.similarity >= 0.6:
            cats.append("medical_fact"); sig.append("negation_changed")
        gone, came = la - lb, lb - la
        if gone and came:  # an English term replaced by another one: wording or fact - a person must look
            cats.append("terminology"); sig.append("term_swapped")
            if "medical_fact" not in cats and c.similarity >= 0.8:
                cats.append("medical_fact"); sig.append("term_swapped_check")
        elif gone or came:
            cats.append("terminology"); sig.append("term_english_removed" if gone else "term_english_added")
        ratio = len(b) / max(len(a), 1)
        if ratio >= 1.35:
            cats.append("depth"); sig.append("expanded")
        elif ratio <= 0.7:
            cats.append("depth"); sig.append("shortened")
        if any(w in a for w in _ATTRIB) and not any(w in b for w in _ATTRIB):
            cats.append("style"); sig.append("attribution_removed")
        if _FORMAL.search(a) and _PLAIN.search(b):
            cats.append("style"); sig.append("ending_formal_to_plain")
        elif _PLAIN.search(a) and _FORMAL.search(b):
            cats.append("style"); sig.append("ending_plain_to_formal")
        if not [x for x in cats if x != "format"]:
            cats.append("style"); sig.append("reworded")

    order = ["medical_fact", "structure", "terminology", "depth", "style", "format"]
    c.categories = sorted(dict.fromkeys(cats), key=order.index)
    c.category = c.categories[0] if c.categories else "style"
    c.signals = list(dict.fromkeys(sig))


# ------------------------------------------------------------------ candidates
SIGNAL_RULES: dict[str, tuple[str, str]] = {  # signal -> (category, rule sentence)
    "attribution_removed": ("style", "교수님 인용(“교수님은 ~라고 하셨다”) 없이 노트 자체의 서술로 쓴다."),
    "ending_formal_to_plain": ("style", "문장 끝은 합니다체 대신 한다체(~한다/~이다/~하자)로 쓴다."),
    "ending_plain_to_formal": ("style", "문장 끝은 한다체 대신 합니다체로 쓴다."),
    "reworded": ("style", "사용자가 고친 표현 방식(아래 예시)을 따른다."),
    "shortened": ("depth", "설명을 더 짧게 쓴다 — 예시처럼 군더더기 문장·수식어를 뺀다."),
    "expanded": ("depth", "설명을 더 자세히 쓴다 — 예시처럼 이유·결과·예를 덧붙인다."),
    "paragraph_deleted": ("depth", "예시와 같은 종류의 문단은 넣지 않는다."),
    "paragraph_inserted": ("depth", "예시와 같은 종류의 문단을 추가한다."),
    "cell_deleted": ("depth", "표 칸에서 예시와 같은 줄은 뺀다."),
    "cell_inserted": ("depth", "표 칸에 예시와 같은 줄을 추가한다."),
    "moved": ("structure", "예시처럼 내용의 순서를 재배치한다."),
    "heading_renamed": ("structure", "소제목은 예시와 같은 방식으로 이름 붙인다."),
    "heading_inserted": ("structure", "예시처럼 소제목을 더 세분해서 넣는다."),
    "heading_deleted": ("structure", "예시와 같은 소제목은 두지 않는다(구획을 합친다)."),
    "table_shape": ("structure", "표의 행·열 구성을 예시처럼 바꾼다."),
    "term_swapped": ("terminology", "용어는 사용자가 고친 표기를 쓴다."),
    "term_english_removed": ("terminology", "예시의 용어는 영어 병기 없이 한글로 쓴다."),
    "term_english_added": ("terminology", "예시의 용어는 영어(원어)로 쓰거나 병기한다."),
    "bold_added": ("format", "예시와 같은 종류의 말에 굵게를 쓴다."),
    "bold_removed": ("format", "예시와 같은 종류의 말에는 굵게를 쓰지 않는다."),
    "number_changed": ("medical_fact", "수치 정정 — 이 강의의 사실 수정 기록(문체 규칙 아님). 원자료로 확인 필요."),
    "negation_changed": ("medical_fact", "긍정/부정이 바뀐 사실 정정 — 이 강의의 수정 기록. 원자료로 확인 필요."),
    "term_swapped_check": ("medical_fact", "용어가 다른 용어로 바뀜 — 표기 통일인지 사실 정정인지 확인 필요."),
}


class Example(BaseModel):
    before: str = ""
    after: str = ""
    change_id: str = ""


class Candidate(BaseModel):
    id: str
    category: str
    signal: str
    rule: str
    support: int
    change_ids: list[str] = Field(default_factory=list)
    examples: list[Example] = Field(default_factory=list)
    needs_verification: bool = False
    status: Literal["pending", "approved", "rejected"] = "pending"


class Report(BaseModel):
    original: str
    edited: str
    created: str
    lecture_type_hint: str = ""
    counts: dict[str, int] = Field(default_factory=dict)
    changes: list[Change] = Field(default_factory=list)
    candidates: list[Candidate] = Field(default_factory=list)


def _clip(s: str, n: int = 220) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def make_candidates(changes: list[Change], max_examples: int = 3) -> list[Candidate]:
    groups: dict[str, list[Change]] = {}
    for c in changes:
        for s in c.signals:
            key = "color" if s.startswith("color:") else s
            groups.setdefault(key, []).append(c)
    out: list[Candidate] = []
    for sig, cs in sorted(groups.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        if sig == "color":
            pairs = sorted({s.split(":", 1)[1] for c in cs for s in c.signals if s.startswith("color:")})
            cat, rule = "format", "글자색을 예시처럼 쓴다 (변경: " + ", ".join(pairs) + "). 파랑 = 기출(PAD) 전용 규칙은 유지."
        else:
            cat, rule = SIGNAL_RULES.get(sig, ("style", sig))
        ex = []
        for c in cs[:max_examples]:
            after = c.after
            if c.type == "format":
                after = (f"[굵게 추가: {', '.join(c.bold_added)}] " if c.bold_added else "") + \
                        (f"[굵게 제거: {', '.join(c.bold_removed)}] " if c.bold_removed else "") + \
                        (f"[색: {'; '.join(c.color_changes)}]" if c.color_changes else "")
            ex.append(Example(before=_clip(c.before), after=_clip(after), change_id=c.id))
        out.append(Candidate(id=f"R{len(out) + 1}", category=cat, signal=sig, rule=rule, support=len(cs),
                             change_ids=[c.id for c in cs], examples=ex, needs_verification=cat == "medical_fact"))
    return out


def build_report(original: str | Path, edited: str | Path, lecture_type: str = "") -> Report:
    """Compare the two notes. Read-only with respect to the rule store: every candidate is `pending`."""
    changes = diff_docs(extract_docx(original), extract_docx(edited))
    for c in changes:
        classify(c)
    counts = {k: 0 for k in CATEGORIES}
    for c in changes:
        for k in c.categories:
            counts[k] += 1
    return Report(original=Path(original).name, edited=Path(edited).name,
                  created=dt.datetime.now().isoformat(timespec="seconds"), lecture_type_hint=lecture_type,
                  counts=counts, changes=changes, candidates=make_candidates(changes))


def report_markdown(rep: Report) -> str:
    L = [f"# 수정 피드백 리포트", "",
         f"- 원본: `{rep.original}` / 수정본: `{rep.edited}` / 작성: {rep.created}",
         f"- 변경 {len(rep.changes)}건, 규칙 후보 {len(rep.candidates)}개",
         "- **아래 후보는 모두 미승인(pending)입니다. 승인하기 전에는 어떤 규칙도 생성에 적용되지 않습니다.**", "",
         "## 분류별 건수 (한 변경이 여러 분류에 들 수 있음)", "", "| 분류 | 건수 |", "|---|---|"]
    L += [f"| {CATEGORIES[k]} | {v} |" for k, v in rep.counts.items()]
    L += ["", "## 규칙 후보", ""]
    for cd in rep.candidates:
        flag = " ⚠️ 검증 필요(문체 규칙으로 일반화하지 않음)" if cd.needs_verification else ""
        L += [f"### {cd.id} · [{CATEGORIES.get(cd.category, cd.category)}] {cd.rule}{flag}",
              f"- 근거: {cd.support}건 ({', '.join(cd.change_ids[:12])}{' …' if len(cd.change_ids) > 12 else ''}) · 상태: {cd.status}"]
        for e in cd.examples:
            L += [f"  - 전: {e.before or '(없음)'}", f"    후: {e.after or '(삭제)'}"]
        L.append("")
    L += ["## 변경 목록", ""]
    names = {"modified": "수정", "inserted": "추가", "deleted": "삭제", "moved": "이동", "format": "서식", "table_shape": "표 모양"}
    for c in rep.changes:
        cats = " · ".join(CATEGORIES[k] for k in c.categories)
        L.append(f"**{c.id}** [{names[c.type]}] {c.where} — {cats}")
        if c.before:
            L.append(f"- 전: {_clip(c.before, 400)}")
        if c.after:
            L.append(f"- 후: {_clip(c.after, 400)}")
        if c.bold_added:
            L.append(f"- 굵게 추가: {', '.join(c.bold_added)}")
        if c.bold_removed:
            L.append(f"- 굵게 제거: {', '.join(c.bold_removed)}")
        if c.color_changes:
            L.append(f"- 색 변경: {'; '.join(c.color_changes)}")
        L.append("")
    return "\n".join(L)


def save_report(rep: Report, out_dir: str | Path) -> tuple[Path, Path]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stem = "feedback_" + re.sub(r"[^0-9A-Za-z가-힣_-]+", "_", Path(rep.edited).stem)[:60]
    jp, mp = out / f"{stem}.json", out / f"{stem}.md"
    jp.write_text(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    mp.write_text(report_markdown(rep), encoding="utf-8")
    return jp, mp


def load_report(path: str | Path) -> Report:
    return Report.model_validate_json(Path(path).read_text(encoding="utf-8"))


# ------------------------------------------------------------------ approved rule store
class Evidence(BaseModel):
    report: str
    original: str
    edited: str
    change_ids: list[str] = Field(default_factory=list)
    support: int = 0
    date: str = ""


class Rule(BaseModel):
    id: str
    version: int = 1
    status: Literal["approved", "retired"] = "approved"
    kind: Literal["rule", "fact_correction"] = "rule"
    category: str
    rule: str
    lecture_types: list[str] = Field(default_factory=lambda: ["all"])
    examples: list[Example] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    signal: str = ""
    note: str = ""
    approved_at: str = ""
    history: list[str] = Field(default_factory=list)


class RuleStore(BaseModel):
    store_version: int = 0
    updated: str = ""
    rules: list[Rule] = Field(default_factory=list)


def load_store(path: str | Path | None = None) -> RuleStore:
    p = Path(path) if path else RULE_STORE
    if not p.exists():
        return RuleStore()
    return RuleStore.model_validate_json(p.read_text(encoding="utf-8"))


def save_store(store: RuleStore, path: str | Path | None = None) -> Path:
    p = Path(path) if path else RULE_STORE
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(store.model_dump(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


def approve(report_path: str | Path, candidate_ids: list[str], lecture_types: list[str],
            store_path: str | Path | None = None, note: str = "", rule_text: str = "") -> list[Rule]:
    """The ONLY function that writes rules. Call it only for candidates the user explicitly approved."""
    bad = [t for t in lecture_types if t not in LECTURE_TYPES]
    if bad or not lecture_types:
        raise ValueError(f"강의 유형이 올바르지 않습니다: {bad or '(없음)'} — 가능: {', '.join(LECTURE_TYPES)}")
    rep = load_report(report_path)
    by_id = {c.id: c for c in rep.candidates}
    missing = [i for i in candidate_ids if i not in by_id]
    if missing:
        raise ValueError(f"리포트에 없는 후보: {missing}")
    store = load_store(store_path)
    now = dt.datetime.now().isoformat(timespec="seconds")
    done: list[Rule] = []
    for cid in candidate_ids:
        cd = by_id[cid]
        ev = Evidence(report=Path(report_path).name, original=rep.original, edited=rep.edited,
                      change_ids=cd.change_ids, support=cd.support, date=rep.created)
        fact = cd.category == "medical_fact"
        text = rule_text if (rule_text and len(candidate_ids) == 1) else cd.rule
        same = None if fact else next((r for r in store.rules if r.status == "approved" and r.kind == "rule"
                                       and r.signal == cd.signal and r.category == cd.category
                                       and sorted(r.lecture_types) == sorted(lecture_types)), None)
        if same:  # the same pattern approved again: new version with more evidence
            same.version += 1
            same.rule = text
            same.examples = (same.examples + cd.examples)[-6:]
            same.evidence.append(ev)
            same.history.append(f"v{same.version} {now}: 근거 추가 ({rep.edited}, {cd.support}건)")
            same.approved_at = now
            if note:
                same.note = note
            done.append(same)
        else:
            n = 1 + max([int(r.id[1:]) for r in store.rules if r.id[1:].isdigit()], default=0)
            r = Rule(id=f"L{n}", kind="fact_correction" if fact else "rule", category=cd.category, rule=text,
                     lecture_types=lecture_types, examples=cd.examples, evidence=[ev], signal=cd.signal, note=note,
                     approved_at=now, history=[f"v1 {now}: 승인 ({rep.edited}, {cd.support}건)"])
            store.rules.append(r)
            done.append(r)
        cd.status = "approved"
    store.store_version += 1
    store.updated = now
    save_store(store, store_path)
    Path(report_path).write_text(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")
    return done


def approve_manual(rule: str, category: str, lecture_types: list[str], evidence_doc: str, examples: list[Example] = (),
                   note: str = "", signal: str = "", store_path: str | Path | None = None,
                   original: str = "", edited: str = "") -> Rule:
    """Store a rule the user approved from an ANALYSIS (e.g. comparing a human-written note) rather than from a
    DOCX diff report. Same gate as `approve`: call it only for rules the user explicitly chose."""
    if category not in CATEGORIES:
        raise ValueError(f"분류가 올바르지 않습니다: {category}")
    bad = [t for t in lecture_types if t not in LECTURE_TYPES]
    if bad or not lecture_types:
        raise ValueError(f"강의 유형이 올바르지 않습니다: {bad or '(없음)'}")
    store = load_store(store_path)
    now = dt.datetime.now().isoformat(timespec="seconds")
    ev = Evidence(report=evidence_doc, original=original, edited=edited, date=now)
    same = next((r for r in store.rules if r.status == "approved" and signal and r.signal == signal), None)
    if same:
        same.version += 1
        same.rule, same.examples, same.note = rule, list(examples) or same.examples, note or same.note
        same.evidence.append(ev)
        same.history.append(f"v{same.version} {now}: 다시 승인 ({evidence_doc})")
        same.approved_at = now
        r = same
    else:
        n = 1 + max([int(x.id[1:]) for x in store.rules if x.id[1:].isdigit()], default=0)
        r = Rule(id=f"L{n}", category=category, rule=rule, lecture_types=list(lecture_types), examples=list(examples),
                 evidence=[ev], signal=signal, note=note, approved_at=now, history=[f"v1 {now}: 승인 ({evidence_doc})"])
        store.rules.append(r)
    store.store_version += 1
    store.updated = now
    save_store(store, store_path)
    return r


def reject(report_path: str | Path, candidate_ids: list[str]) -> None:
    rep = load_report(report_path)
    for c in rep.candidates:
        if c.id in candidate_ids:
            c.status = "rejected"
    Path(report_path).write_text(json.dumps(rep.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")


def retire(rule_id: str, store_path: str | Path | None = None, reason: str = "") -> Rule:
    store = load_store(store_path)
    r = next((x for x in store.rules if x.id == rule_id), None)
    if r is None:
        raise ValueError(f"규칙 없음: {rule_id}")
    now = dt.datetime.now().isoformat(timespec="seconds")
    r.status = "retired"
    r.version += 1
    r.history.append(f"v{r.version} {now}: 사용 중지 {reason}".rstrip())
    store.store_version += 1
    store.updated = now
    save_store(store, store_path)
    return r


def active_rules(lecture_type: str = "", store_path: str | Path | None = None) -> list[Rule]:
    """Approved style rules for a lecture type ("" = every approved rule). Fact corrections are excluded:
    they belong to one lecture, not to how notes are written."""
    out = []
    for r in load_store(store_path).rules:
        if r.status != "approved" or r.kind != "rule":
            continue
        if not lecture_type or "all" in r.lecture_types or lecture_type in r.lecture_types:
            out.append(r)
    return out


def approved_rules_markdown(lecture_type: str = "", store_path: str | Path | None = None) -> str:
    """Text handed to the generator / to Claude Code. Empty string when nothing is approved."""
    store = load_store(store_path)
    rules = active_rules(lecture_type, store_path)
    if not rules:
        return ""
    L = [f"## 사용자가 승인한 학습 규칙 (저장소 v{store.store_version})",
         "사용자가 직접 고친 강의록에서 뽑아 **승인한** 규칙이다. 다른 문체 규칙과 충돌하면 이쪽이 우선한다. "
         "단, 파랑 = 기출(PAD) 전용 규칙과 내용 보존(수치·용어·출처) 규칙은 그대로 지킨다.", ""]
    for r in rules:
        types = ", ".join(LECTURE_TYPES.get(t, t).split(" (")[0] for t in r.lecture_types)
        L.append(f"- **{r.id} v{r.version}** [{CATEGORIES.get(r.category, r.category)} · 적용: {types}] {r.rule}"
                 + (f" ({r.note})" if r.note else ""))
        for e in r.examples[:2]:
            L.append(f"  - 전: {e.before or '(없음)'}")
            L.append(f"    후: {e.after or '(삭제)'}")
    return "\n".join(L) + "\n"


def store_markdown(store_path: str | Path | None = None) -> str:
    store = load_store(store_path)
    L = [f"# 승인된 학습 규칙 (저장소 v{store.store_version}, {store.updated or '비어 있음'})", ""]
    if not store.rules:
        L.append("승인된 규칙이 없습니다.")
    for r in store.rules:
        kind = "사실 정정 기록" if r.kind == "fact_correction" else "규칙"
        L += [f"## {r.id} v{r.version} · {kind} · {CATEGORIES.get(r.category, r.category)} · {r.status}",
              f"- 내용: {r.rule}", f"- 적용 강의 유형: {', '.join(LECTURE_TYPES.get(t, t) for t in r.lecture_types)}"]
        if r.note:
            L.append(f"- 메모: {r.note}")
        for e in r.examples:
            L += [f"- 전: {e.before or '(없음)'}", f"  후: {e.after or '(삭제)'}"]
        for ev in r.evidence:
            L.append(f"- 근거: {ev.edited} ← {ev.original} · {ev.support}건 ({', '.join(ev.change_ids[:10])}) · {ev.date}")
        L += [f"- 이력: {h}" for h in r.history]
        L.append("")
    return "\n".join(L)

import json
import subprocess
from pathlib import Path

import pytest
from docx import Document
from docx.shared import RGBColor

from app import feedback as fb
from app.cli import main
from app.docx_diff import diff_docs, extract_docx
from app.generate_notes import learned_rules, load_style_guide

ROOT = Path(__file__).resolve().parent.parent


def _doc(path, paras, table=None):
    """paras: list of (text | [(text, bold, color)], style)"""
    d = Document()
    for item, style in paras:
        p = d.add_paragraph(style=style) if style else d.add_paragraph()
        for text, bold, color in ([(item, False, None)] if isinstance(item, str) else item):
            r = p.add_run(text)
            r.bold = bold
            if color:
                r.font.color.rgb = RGBColor.from_string(color)
    if table:
        t = d.add_table(rows=len(table), cols=len(table[0]))
        for ri, row in enumerate(table):
            for ci, v in enumerate(row):
                t.cell(ri, ci).text = v
    d.save(path)
    return path


@pytest.fixture
def pair(tmp_path):
    orig = _doc(tmp_path / "orig.docx", [
        ("1. 다형성", "Heading 1"),
        ("교수님은 다형성이 집단 수준의 다양성이라고 하셨습니다.", None),
        ([("핵심 용어는 ", False, None), ("haplotype", True, None), ("이다.", False, None)], None),
        ("alloreactive T cell은 전체 T세포의 약 1~10%이다.", None),
        ("첫 번째로 유전자 영역을 본다.", None),
        ("두 번째로 MHC restriction을 본다.", None),
        ("이 문단은 군더더기 안내라서 지워질 것이다.", None),
        ("대립유전자의 종류가 다양하다.", None),
    ], table=[["약", "표적"], ["imatinib", "BCR-ABL"]])
    edit = _doc(tmp_path / "edit.docx", [
        ("1. 다형성과 polygeny", "Heading 1"),
        ("다형성은 집단 수준의 다양성이다.", None),
        ([("핵심 용어는 haplotype이다.", False, "FF0000")], None),
        ("alloreactive T cell은 전체 T세포의 약 5~10%이다.", None),
        ("두 번째로 MHC restriction을 본다.", None),
        ("첫 번째로 유전자 영역을 본다.", None),
        ("allele의 종류가 다양하다.", None),
        ("새로 덧붙인 설명 문단이다. 결과적으로 사람마다 조합이 달라진다.", None),
    ], table=[["약", "표적"], ["imatinib", "BCR-ABL"], ["gefitinib", "EGFR"]])
    return orig, edit


def test_extract_blocks_runs_and_tables(pair):
    ex = extract_docx(pair[0])
    assert ex.blocks[0].kind == "heading" and ex.blocks[0].level == 1
    bold = [s.text for b in ex.blocks for s in b.spans if s.bold]
    assert "haplotype" in bold
    cells = [b for b in ex.blocks if b.kind == "cell"]
    assert cells[-1].text == "BCR-ABL" and (cells[-1].row, cells[-1].col) == (1, 1)
    assert (ex.tables[0].rows, ex.tables[0].cols) == (2, 2)
    red = [s.color for b in extract_docx(pair[1]).blocks for s in b.spans if s.color]
    assert red == ["FF0000"]


def test_diff_finds_every_kind_of_change(pair):
    changes = diff_docs(extract_docx(pair[0]), extract_docx(pair[1]))
    by = {}
    for c in changes:
        by.setdefault(c.type, []).append(c)
    assert any("heading" in c.kind for c in by["modified"])  # heading renamed
    assert any(c.before.startswith("이 문단은 군더더기") for c in by["deleted"])
    assert any(c.after.startswith("새로 덧붙인") for c in by["inserted"])
    assert any(c.after == "gefitinib" and c.kind == "cell" for c in by["inserted"])  # new table cell
    assert by["moved"]  # two sentences swapped = order change
    assert by["table_shape"][0].before == "2행 × 2열" and by["table_shape"][0].after == "3행 × 2열"
    fmt = next(c for c in by["format"] if "haplotype" in c.before)
    assert fmt.bold_removed == ["haplotype"] and any("FF0000" in x for x in fmt.color_changes)


def test_classification_six_categories(pair):
    rep = fb.build_report(*pair)
    cat = {c.before[:12] or c.after[:12]: c for c in rep.changes}
    prof = next(c for c in rep.changes if c.before.startswith("교수님은"))
    assert "style" in prof.categories and {"attribution_removed", "ending_formal_to_plain"} <= set(prof.signals)
    num = next(c for c in rep.changes if "1~10%" in c.before)
    assert num.category == "medical_fact" and "number_changed" in num.signals
    term = next(c for c in rep.changes if c.before.startswith("대립유전자"))
    assert "terminology" in term.categories
    assert next(c for c in rep.changes if c.type == "moved").category == "structure"
    assert next(c for c in rep.changes if c.type == "format").category == "format"
    assert "depth" in next(c for c in rep.changes if c.type == "deleted").categories
    assert all(v > 0 for v in rep.counts.values()), rep.counts  # all six categories seen
    assert cat


def test_reports_saved_as_json_and_markdown(pair, tmp_path):
    rep = fb.build_report(*pair)
    jp, mp = fb.save_report(rep, tmp_path / "reports")
    data = json.loads(jp.read_text(encoding="utf-8"))
    assert data["changes"] and data["candidates"]
    md = mp.read_text(encoding="utf-8")
    assert "미승인" in md and "의학적 사실" in md and "규칙 후보" in md


def test_nothing_is_applied_before_approval(pair, tmp_path, monkeypatch):
    store = tmp_path / "rules.json"
    monkeypatch.setattr(fb, "RULE_STORE", store)
    before = load_style_guide()
    rep = fb.build_report(*pair)
    jp, _ = fb.save_report(rep, tmp_path / "reports")
    assert not store.exists()  # diff never writes the rule store
    assert all(c.status == "pending" for c in rep.candidates)
    assert fb.active_rules() == [] and learned_rules() == ""
    assert load_style_guide() == before  # generator prompt unchanged

    cand = next(c for c in fb.load_report(jp).candidates if c.signal == "attribution_removed")
    fb.approve(jp, [cand.id], ["concept_chain"])
    assert "교수님 인용" in learned_rules("concept_chain")
    assert learned_rules("list_intro") == ""  # scoped to the approved lecture type
    assert "승인한 학습 규칙" in load_style_guide()
    others = [c for c in fb.load_report(jp).candidates if c.id != cand.id]
    assert all(c.status == "pending" for c in others)  # the rest stays unapproved


def test_approved_rule_has_scope_examples_evidence_version(pair, tmp_path):
    store = tmp_path / "rules.json"
    jp, _ = fb.save_report(fb.build_report(*pair), tmp_path / "reports")
    cand = next(c for c in fb.load_report(jp).candidates if c.signal == "attribution_removed")
    r = fb.approve(jp, [cand.id], ["concept_chain"], store, note="스토리형 본문")[0]
    assert (r.version, r.lecture_types, r.kind) == (1, ["concept_chain"], "rule")
    assert r.examples[0].before.startswith("교수님은") and r.examples[0].after
    assert r.evidence[0].edited == "edit.docx" and r.evidence[0].change_ids and r.evidence[0].support >= 1
    assert fb.load_store(store).store_version == 1
    r2 = fb.approve(jp, [cand.id], ["concept_chain"], store)[0]  # approved again -> version bump, not a duplicate
    s = fb.load_store(store)
    assert r2.id == r.id and r2.version == 2 and len(s.rules) == 1 and s.store_version == 2 and len(r2.evidence) == 2
    fb.retire(r.id, store, "테스트")
    assert fb.active_rules("concept_chain", store) == []


def test_medical_fact_is_recorded_not_generalised(pair, tmp_path):
    store = tmp_path / "rules.json"
    jp, _ = fb.save_report(fb.build_report(*pair), tmp_path / "reports")
    cand = next(c for c in fb.load_report(jp).candidates if c.signal == "number_changed")
    assert cand.needs_verification
    r = fb.approve(jp, [cand.id], ["all"], store)[0]
    assert r.kind == "fact_correction"
    assert fb.active_rules("", store) == []  # never handed to the generator as a style rule
    assert "사실 정정 기록" in fb.store_markdown(store)


def test_approve_rejects_bad_input(pair, tmp_path):
    jp, _ = fb.save_report(fb.build_report(*pair), tmp_path / "reports")
    with pytest.raises(ValueError):
        fb.approve(jp, ["R1"], ["unknown_type"], tmp_path / "r.json")
    with pytest.raises(ValueError):
        fb.approve(jp, ["R999"], ["all"], tmp_path / "r.json")
    assert not (tmp_path / "r.json").exists()


def test_cli_feedback_flow(pair, tmp_path, capsys):
    out, store = tmp_path / "rep", tmp_path / "rules.json"
    assert main(["feedback", "diff", str(pair[0]), str(pair[1]), "--out", str(out)]) == 0
    assert "미승인" in capsys.readouterr().out and not store.exists()
    jp = next(out.glob("*.json"))
    cid = next(c.id for c in fb.load_report(jp).candidates if c.signal == "attribution_removed")
    assert main(["feedback", "approve", str(jp), "--ids", cid, "--lecture-type", "all", "--store", str(store)]) == 0
    assert main(["feedback", "rules", "--store", str(store)]) == 0
    assert "교수님 인용" in capsys.readouterr().out
    assert main(["feedback", "reject", str(jp), "--ids", "R1"]) == 0
    assert main(["feedback", "export", "--store", str(store), "--out", str(tmp_path / "r.md")]) == 0
    assert (tmp_path / "r.md").read_text(encoding="utf-8").startswith("# 승인된 학습 규칙")
    assert main(["feedback", "approve", str(jp), "--ids", "R1", "--lecture-type", "nope", "--store", str(store)]) == 2


def test_private_material_is_gitignored():
    paths = ["feedback/originals/note.docx", "feedback/edited/note_edited.docx", "feedback/reports/feedback_x.json",
             "inputs/lecture.pptx", "inputs/script.docx", "outputs/x/note.docx", "anything/recording.m4a"]
    res = subprocess.run(["git", "check-ignore", *paths], cwd=ROOT, capture_output=True, text=True)
    assert sorted(res.stdout.split()) == sorted(paths)
    keep = subprocess.run(["git", "check-ignore", "style_rules/approved_rules.json"], cwd=ROOT, capture_output=True, text=True)
    assert keep.stdout.strip() == ""  # the approved rules stay versioned

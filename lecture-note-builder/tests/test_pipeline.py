import json
from pathlib import Path
from types import SimpleNamespace

from docx import Document

from app.align_content import align
from app.cli import main
from app.export_docx import export_docx
from app.extract_slides import extract_pptx
from app.generate_notes import AnthropicBackend, generate_note
from app.template import load_template
from app.transcript import parse_script
from app.validate_notes import validate

TPL = Path(__file__).resolve().parent.parent / "templates" / "medical.yaml"


def _slides(sample_pptx, tmp_path):
    return extract_pptx(sample_pptx, tmp_path / "img")


def test_extract(sample_pptx, tmp_path):
    s = _slides(sample_pptx, tmp_path)
    assert [x.number for x in s] == [1, 2, 3]
    assert s[0].title.startswith("Ulcerative")
    assert s[0].body[1].level == 1
    assert "젊은 성인" in s[0].speaker_notes
    assert s[1].tables[0].rows[1] == ["2", "뚜렷한 발적, 점막 취약성"]
    assert len(s[2].images) == 1 and Path(s[2].images[0]).exists()


def test_parse_script_markers_and_times(marked_script):
    segs = parse_script(marked_script.read_text(encoding="utf-8"))
    assert [g.slide_hint for g in segs] == [1, 2, 3]
    assert segs[1].start == 40 and segs[1].end == 70
    assert segs[0].end == 40 or segs[0].end is None  # inferred only when next start exists


def test_align_marker(sample_pptx, marked_script, tmp_path):
    slides = _slides(sample_pptx, tmp_path)
    al = align(parse_script(marked_script.read_text(encoding="utf-8")), slides)
    assert [len(a.segments) for a in al] == [1, 1, 1]
    assert all(a.method == "marker" and a.confidence == 1.0 for a in al)


def test_align_similarity_monotonic(sample_pptx, unmarked_script, tmp_path):
    slides = _slides(sample_pptx, tmp_path)
    al = align(parse_script(unmarked_script.read_text(encoding="utf-8")), slides)
    assert [a.segments[0].id for a in al] == [0, 1, 2]
    assert all(a.method == "similarity" for a in al)


def test_low_confidence_is_reported(sample_pptx, tmp_path):
    slides = _slides(sample_pptx, tmp_path)
    segs = parse_script("전혀 관련 없는 잡담입니다 오늘 날씨가 좋네요")
    al = align(segs, slides, min_confidence=0.15)
    assert any(a.low_confidence_segment_ids for a in al)


def test_validation_passes_offline(sample_pptx, marked_script, tmp_path):
    tpl = load_template(TPL)
    slides = _slides(sample_pptx, tmp_path)
    al = align(parse_script(marked_script.read_text(encoding="utf-8")), slides)
    note = generate_note("T", slides, al, tpl)
    rep = validate(note, slides, al, tpl)
    assert rep.ok, rep.errors
    assert rep.slide_coverage == 1.0
    assert note.topics[1].sections["professor_emphasis"][0].emphasis
    assert note.exam_points


def test_validation_catches_loss(sample_pptx, marked_script, tmp_path):
    tpl = load_template(TPL)
    slides = _slides(sample_pptx, tmp_path)
    al = align(parse_script(marked_script.read_text(encoding="utf-8")), slides)
    note = generate_note("T", slides, al, tpl)
    # corrupt: drop slide 3 number, slide 2 table, slide 2's lecturer segment
    note.topics[2].sections["core_concepts"] = [
        s.model_copy(update={"text": s.text.replace("4.8", "x")})
        for s in note.topics[2].sections["core_concepts"]
    ]
    note.topics[1].tables = []
    note.topics[1].sections.pop("professor_emphasis")
    note.topics.pop(0)
    codes = {i.code for i in validate(note, slides, al, tpl).errors}
    assert {"SLIDE_MISSING", "NUMBER_LOST", "TABLE_LOST", "SEGMENT_LOST"} <= codes


def test_docx_export(sample_pptx, marked_script, tmp_path):
    tpl = load_template(TPL)
    slides = _slides(sample_pptx, tmp_path)
    al = align(parse_script(marked_script.read_text(encoding="utf-8")), slides)
    note = generate_note("궤양성 대장염", slides, al, tpl)
    out = export_docx(note, tpl, tmp_path / "o.docx", validate(note, slides, al, tpl))
    d = Document(str(out))
    text = "\n".join(p.text for p in d.paragraphs)
    assert "궤양성 대장염" in text and "PPT p.2" in text and "음성 00:40-01:10" in text
    assert len(d.tables) == 1 and len(d.inline_shapes) == 1


class _FakeClient:
    """Mimics anthropic.Anthropic().messages.create with a forced tool call."""
    def __init__(self):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        payload = json.loads(kw["messages"][0]["content"])
        topics = []
        for s in payload["slides"]:
            n = s["slide"]["number"]
            topics.append({
                "heading": s["slide"]["title"], "slide_numbers": [n],
                "sections": {
                    "core_concepts": [{"text": s["slide"]["title"], "origin": "slide", "slide_refs": [n]}],
                    "bogus_section": [{"text": "x", "slide_refs": [n]}],
                },
            })
        return SimpleNamespace(content=[SimpleNamespace(type="tool_use", input={"topics": topics})])


def test_anthropic_backend_with_fake_client(sample_pptx, marked_script, tmp_path):
    tpl = load_template(TPL)
    slides = _slides(sample_pptx, tmp_path)
    al = align(parse_script(marked_script.read_text(encoding="utf-8")), slides)
    fake = _FakeClient()
    note = generate_note("T", slides, al, tpl, AnthropicBackend(client=fake, chunk_size=2))
    assert len(fake.calls) == 2  # 3 slides / chunks of 2
    assert fake.calls[0]["tool_choice"] == {"type": "tool", "name": "emit_topics"}
    assert all("bogus_section" not in t.sections for t in note.topics)  # filtered
    assert note.topics[1].tables and note.topics[2].images  # attached by code


def test_cli_end_to_end(sample_pptx, marked_script, tmp_path):
    out = tmp_path / "out"
    rc = main(["build", str(sample_pptx), "--script", str(marked_script), "--out", str(out), "--no-pdf"])
    assert rc == 0
    for f in ("lec_강의록.docx", "lec_강의록.md", "validation_report.md", "note.json", "slides.json"):
        assert (out / f).exists(), f


STRUCT = """T림프구 테스트
기준 자료: 「2023.04.26 면역학 — 테스트」
[00:00–02:00] 도입  |  원본 2쪽
MHC는 6번 염색체에 있습니다. 중요합니다.
[02:00–04:00] 용어  |  원본 2–3쪽
Polygenic과 polymorphic은 다릅니다. 1~10% 정도입니다.
[04:00–06:00] 마무리  |  원본 4쪽
CD1은 lipid를 제시합니다.
재구성 및 검증 참고
• 가상 발화이며 실제 강의가 아닙니다.
"""

MOM = Path(__file__).resolve().parent.parent / "templates" / "mom.yaml"


def test_flow_script_drops_time_blocks():
    from app.transcript import is_structured, parse_flow_script

    assert is_structured(STRUCT)
    meta, segs = parse_flow_script(STRUCT)
    assert meta["date"] == "2023-04-26" and meta["subject"] == "면역학"
    assert [g.id for g in segs] == [1, 2, 3, 4]  # one continuous paragraph flow
    assert [g.kind for g in segs] == ["speech"] * 3 + ["note"]
    assert not any("00:00" in g.text or "원본" in g.text for g in segs)  # headers are not content
    assert all(g.start is None for g in segs)


def test_normalize_outline_covers_everything_once():
    from app.models import Outline, OutlineItem
    from app.outline import APPENDIX, normalize_outline

    raw = Outline(items=[OutlineItem(heading="A", unit_numbers=[1, 2, 99]),
                         OutlineItem(heading="B", unit_numbers=[2, 4])])  # 99 unknown, 2 dup, 3 & 5 skipped
    out = normalize_outline(raw, speech=[1, 2, 3, 4, 5], notes=[6])
    flat = [n for it in out.items for n in it.unit_numbers]
    assert sorted(flat) == [1, 2, 3, 4, 5, 6] and len(flat) == len(set(flat))
    assert out.items[-1].heading == APPENDIX and out.items[-1].unit_numbers == [6]


def test_heuristic_outline_splits_on_topic_shift():
    from app.models import BodyLine, Slide
    from app.outline import heuristic_outline

    a = "항원 처리 proteasome TAP peptide loading 과정"
    b = "이식 거부반응 allograft MLR alloreactive 림프구 증식"
    units = [Slide(number=i + 1, body=[BodyLine(text=(a if i < 5 else b) + f" {i}")]) for i in range(10)]
    o = heuristic_outline(units, target=2)
    assert [it.unit_numbers for it in o.items] == [[1, 2, 3, 4, 5], [6, 7, 8, 9, 10]]


def _write(tmp_path, text=STRUCT):
    s = tmp_path / "s.txt"; s.write_text(text, encoding="utf-8"); return s


def test_script_only_auto_toc_and_outline_json(tmp_path):
    from app.pipeline import run_pipeline

    rep, paths = run_pipeline(None, tmp_path / "o", MOM, script=_write(tmp_path), pdf=False, toc="heuristic")
    assert rep.ok, rep.errors
    outline = json.loads(paths["outline"].read_text(encoding="utf-8"))
    nums = [n for it in outline["items"] for n in it["unit_numbers"]]
    assert sorted(nums) == [1, 2, 3, 4]
    d = Document(str(paths["docx"]))
    text = "\n".join(p.text for p in d.paragraphs)
    assert "발화 ¶" in text and "00:00" not in text and "원본 2쪽" not in text
    # edit the TOC by hand and re-apply it
    outline["items"] = [{"heading": "전부 한 섹션", "unit_numbers": [1, 2, 3], "summary": ""}]
    edited = tmp_path / "edited.json"; edited.write_text(json.dumps(outline, ensure_ascii=False), encoding="utf-8")
    rep2, p2 = run_pipeline(None, tmp_path / "o2", MOM, script=_write(tmp_path), pdf=False, outline_json=edited)
    assert [it["heading"] for it in json.loads(p2["outline"].read_text(encoding="utf-8"))["items"]] == ["전부 한 섹션", "부록 & 검증 참고"]


class _FakeOutlineClient:
    def __init__(self):
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    def _create(self, **kw):
        self.calls.append(kw)
        if kw["tool_choice"]["name"] == "emit_outline":
            payload = json.loads(kw["messages"][0]["content"])
            assert [p["n"] for p in payload["paragraphs"]] == [1, 2, 3]  # note paragraph is not sent
            inp = {"items": [{"heading": "용어와 기본 개념", "unit_numbers": [1, 2], "summary": "s"},
                             {"heading": "CD1", "unit_numbers": [3]}]}
        else:
            payload = json.loads(kw["messages"][0]["content"])
            n = payload["slides"][0]["slide"]["number"]
            inp = {"topics": [{"heading": "모델이 바꾼 제목", "slide_numbers": [n],
                               "sections": {"body": [{"text": "요약 문장", "slide_refs": [n]}]}}]}
        return SimpleNamespace(content=[SimpleNamespace(type="tool_use", input=inp)])


def test_ai_outline_then_one_topic_per_section(tmp_path):
    from app.generate_notes import AnthropicBackend
    from app.pipeline import run_pipeline

    fake = _FakeOutlineClient()
    rep, paths = run_pipeline(None, tmp_path / "o", MOM, script=_write(tmp_path), pdf=False,
                              backend=AnthropicBackend(client=fake), toc="ai")
    kinds = [c["tool_choice"]["name"] for c in fake.calls]
    assert kinds == ["emit_outline"] + ["emit_topics"] * 3  # outline + one call per section (2 + appendix)
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    heads = [t["heading"] for t in note["topics"]]
    assert heads == ["용어와 기본 개념", "CD1", "부록 & 검증 참고"]  # topics follow the AI outline, not the model's own heading
    assert [t["slide_numbers"] for t in note["topics"][:2]] == [[1, 2], [3]]


PAD = """2023년 4월 26일 수요일 <면역학>
                        기출문제
  20학번 (2022년) 김태규 교수님.
  다른 교수님이다.

  1. 다음 중 다형성이 가장 높은 유전자좌는?
   ① HLA-A ② HLA-B ③ HLA-C
                                  정답 : 2번
  Class I의 polymorphism은 B>A>C 순이다.

  19학번 (2021년) 김태규 교수님. (감염과 면역)
  1. CD1c가 활성화 시키는 것은?
  1) NK cell 2) NKT cell
                                  정답 : 2번
  CD1c는 lipid를 제시한다.
  2. MHC class 2에 해당하는 것은?
  1) HLA-A 2) HLA-DR
                                  정답 : 2번
  2글자는 class II.
  07학번 (2009년) 김태규 교수님. (감염과 면역)
  정답 3번. 짤입니다.
  수고하셨습니다~
"""
BODY = "MHC는 6번 염색체. Polygenic polymorphic 1~10% CD1 lipid"


def test_exam_parse():
    from app.exam import EXAM_BASE, parse_exam_text

    items = parse_exam_text(PAD)
    assert [i.number for i in items] == [EXAM_BASE + k for k in range(1, 5)]
    assert items[0].year == 2022 and items[0].answer == "2번" and "B>A>C" in items[0].commentary
    assert "HLA-C" in items[0].question  # choices stay with the question
    assert items[1].course == "감염과 면역" and items[2].q_no == 2  # choice lines "1)" are not questions
    assert "스캔" in items[3].question


def _exam_run(tmp_path, monkeypatch, topics=None, backend=None):
    import app.exam as exam
    from app.generate_notes import PrecomputedBackend
    from app.pipeline import run_pipeline

    monkeypatch.setattr(exam, "pdf_text", lambda p: PAD)
    backend = backend or PrecomputedBackend(topics)
    return run_pipeline(None, tmp_path / "o", MOM, script=_write(tmp_path), backend=backend, pdf=False,
                        exam_pdf=tmp_path / "pad.pdf", toc="heuristic")


def test_blue_only_for_exam(tmp_path, monkeypatch):
    from app.exam import EXAM_BASE as X
    from app.models import Statement, Topic

    base = Statement(text=BODY, slide_refs=[1, 2, 3, 4])
    ok = Statement(text="{b|기출: 다형성 최대 HLA-B}", slide_refs=[2, X + 1])
    bad = Statement(text="{b|그냥 중요한 용어}", slide_refs=[2])
    unmarked = Statement(text="PAD 문항 내용을 파랑 없이 서술", slide_refs=[2, X + 2])
    units = [1, 2, 3, 4, X + 1, X + 2, X + 3, X + 4]
    rep, _ = _exam_run(tmp_path, monkeypatch,
                       [Topic(heading="0. t", slide_numbers=units, sections={"body": [base, ok, bad, unmarked]})])
    codes = [(i.code, i.severity) for i in rep.issues]
    assert ("BLUE_WITHOUT_PAD", "error") in codes and ("PAD_NOT_BLUE", "warning") in codes
    assert sum(1 for c, _ in codes if c == "BLUE_WITHOUT_PAD") == 1  # the PAD-cited blue statement is fine


def test_exam_units_must_be_covered(tmp_path, monkeypatch):
    from app.exam import EXAM_BASE as X
    from app.models import Statement, Topic

    t = Topic(heading="0. t", slide_numbers=[1, 2, 3, 4, X + 1],
              sections={"body": [Statement(text=BODY, slide_refs=[1, 2, 3, 4])]})
    rep, _ = _exam_run(tmp_path, monkeypatch, [t])
    assert {i.slide for i in rep.errors if i.code == "SLIDE_MISSING"} == {X + 2, X + 3, X + 4}
    assert any("PAD 2021(19학번) Q1" in m for m in [i.message for i in rep.errors])  # readable names


def test_offline_backend_builds_blue_exam_section(tmp_path, monkeypatch):
    from app.generate_notes import OfflineBackend

    rep, paths = _exam_run(tmp_path, monkeypatch, backend=OfflineBackend())
    assert not [i for i in rep.errors], rep.errors
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    assert note["topics"][0]["heading"].startswith("0. 기출")
    assert "{b|" in note["topics"][0]["sections"]["body"][0]["text"]
    assert all(r >= 1000 for st in note["topics"][0]["sections"]["body"] for r in st["slide_refs"])
    assert note["unit_labels"]["1001"] == "PAD 2022(20학번) Q1"


def test_heat_table_and_col_widths(tmp_path):
    from app.export_mom import export_mom
    from app.models import LectureNote, SlideTable, Topic

    tpl = load_template(MOM)
    tb = SlideTable(rows=[["주제", "총"], ["a", "4"], ["b", "0"]], heat_cols=[1], col_widths_cm=[8, 2])
    note = LectureNote(title="t", topics=[Topic(heading="0. x", slide_numbers=[], tables=[tb])])
    xml = Document(str(export_mom(note, tpl, tmp_path / "h.docx"))).element.xml
    assert 'w:fill="7BC47F"' in xml and 'w:fill="FF' in xml  # zero -> green, max -> strong red

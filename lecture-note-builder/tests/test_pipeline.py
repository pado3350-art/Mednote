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
            inp = {"items": [{"heading": "용어와 기본 개념", "unit_numbers": [1, 2], "summary": "s", "chapter": "MHC"},
                             {"heading": "CD1", "unit_numbers": [3], "chapter": "Unconventional T cell"}]}
        elif kw["tool_choice"]["name"] == "emit_front":
            assert "기본정석" in kw["system"]  # the readable-note-organizer skill is part of the prompt
            inp = {"topics": [{"heading": "핵심 어휘", "slide_numbers": [], "sections": {"body": [
                       {"text": "**MHC** : 정의", "slide_refs": [1]}]}},
                              {"heading": "요약 정리", "slide_numbers": [], "sections": {"body": [
                       {"text": "요약", "slide_refs": [2]}]}}]}
        else:
            payload = json.loads(kw["messages"][0]["content"])
            n = payload["slides"][0]["slide"]["number"]
            inp = {"topics": [{"heading": "모델이 바꾼 제목", "slide_numbers": [n], "basics_title": "기본", "basics": ["a", "b"],
                               "sections": {"body": [{"text": "요약 문장", "slide_refs": [n]}]}}]}
        return SimpleNamespace(content=[SimpleNamespace(type="tool_use", input=inp)])


def test_ai_outline_then_one_topic_per_section(tmp_path):
    from app.generate_notes import AnthropicBackend
    from app.pipeline import run_pipeline

    fake = _FakeOutlineClient()
    rep, paths = run_pipeline(None, tmp_path / "o", MOM, script=_write(tmp_path), pdf=False,
                              backend=AnthropicBackend(client=fake), toc="ai")
    kinds = [c["tool_choice"]["name"] for c in fake.calls]
    assert kinds == ["emit_outline"] + ["emit_topics"] * 3 + ["emit_front"]  # outline + per section (2 + appendix) + front pages
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    topics = note["topics"]
    assert [t["heading"] for t in topics] == ["핵심 어휘", "요약 정리", "용어와 기본 개념", "CD1", "부록 & 검증 참고"]
    assert [t["role"] for t in topics[:2]] == ["front", "front"]
    body = topics[2:]  # follow the AI outline, not the model's own heading
    assert [t["slide_numbers"] for t in body[:2]] == [[1, 2], [3]]
    assert [t["chapter"] for t in body] == ["MHC", "Unconventional T cell", ""]
    assert body[0]["basics"] == ["a", "b"]


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


def _exam_tpl(tmp_path):
    p = tmp_path / "exam.yaml"
    p.write_text(MOM.read_text(encoding="utf-8").replace("exam_section: false", "exam_section: true"), encoding="utf-8")
    return p


def _exam_run(tmp_path, monkeypatch, topics=None, backend=None, tpl=None):
    import app.exam as exam
    from app.generate_notes import PrecomputedBackend
    from app.pipeline import run_pipeline

    monkeypatch.setattr(exam, "pdf_text", lambda p: PAD)
    backend = backend or PrecomputedBackend(topics)
    return run_pipeline(None, tmp_path / "o", tpl or _exam_tpl(tmp_path), script=_write(tmp_path), backend=backend,
                        pdf=False, exam_pdf=tmp_path / "pad.pdf", toc="heuristic")


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
    assert ("BLUE_WITHOUT_PAD", "error") in codes and ("PAD_NOT_BLUE", "error") in codes
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
    exam = next(t for t in note["topics"] if t["heading"].startswith("0. 기출"))  # front pages may come first
    assert "{b|" in exam["sections"]["body"][0]["text"]
    assert all(r >= 1000 for st in exam["sections"]["body"] for r in st["slide_refs"])
    assert note["unit_labels"]["1001"] == "PAD 2022(20학번) Q1"


def test_heat_table_and_col_widths(tmp_path):
    from app.export_mom import export_mom
    from app.models import LectureNote, SlideTable, Topic

    tpl = load_template(MOM)
    tb = SlideTable(rows=[["주제", "총"], ["a", "4"], ["b", "0"]], heat_cols=[1], col_widths_cm=[8, 2])
    note = LectureNote(title="t", topics=[Topic(heading="0. x", slide_numbers=[], tables=[tb])])
    xml = Document(str(export_mom(note, tpl, tmp_path / "h.docx"))).element.xml
    assert 'w:fill="7BC47F"' in xml and 'w:fill="FF' in xml  # zero -> green, max -> strong red


def test_no_exam_section_by_default_but_blue_still_checked(tmp_path, monkeypatch):
    from app.generate_notes import OfflineBackend
    from app.exam import EXAM_BASE as X
    from app.models import Statement, Topic

    rep, paths = _exam_run(tmp_path, monkeypatch, backend=OfflineBackend(), tpl=MOM)  # mom.yaml: exam_section false
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    assert not any(t["heading"].startswith("0. 기출") for t in note["topics"])
    assert not rep.errors and rep.slide_coverage == 1.0
    assert {i.code for i in rep.issues if i.severity == "warning"} >= {"PAD_UNUSED"}  # PAD not echoed: warning, not an error
    bad = Statement(text="{b|파랑인데 기출 아님}", slide_refs=[1])
    rep2, _ = _exam_run(tmp_path / "x" if (tmp_path / "x").mkdir() is None else tmp_path, monkeypatch,
                        [Topic(heading="t", slide_numbers=[1, 2, 3, 4], sections={"body": [
                            Statement(text=BODY, slide_refs=[1, 2, 3, 4]), bad]})], tpl=MOM)
    assert "BLUE_WITHOUT_PAD" in {i.code for i in rep2.errors}


def test_numbering_chapters_and_front():
    from app.export_mom import numbering
    from app.models import LectureNote, Topic

    note = LectureNote(title="t", topics=[
        Topic(heading="핵심 어휘", role="front", slide_numbers=[]),
        Topic(heading="a", chapter="C1", slide_numbers=[1]), Topic(heading="b", chapter="C1", slide_numbers=[2]),
        Topic(heading="c", chapter="C2", slide_numbers=[3]), Topic(heading="부록", slide_numbers=[4])])
    n = numbering(note)
    assert n[0]["toc"] is None and n[0]["banner"] == "핵심 어휘"
    assert [x["section"] for x in n[1:4]] == ["§ 1. a", "§ 2. b", "§ 1. c"]
    assert [x["banner"] for x in n[1:4]] == ["1. C1", "1. C1", "2. C2"]
    assert n[4]["section"] == "부록" and n[4]["chapter"] == ""


def test_mom_layout_banner_toc_basics_callouts(tmp_path):
    from app.export_mom import export_mom
    from app.models import LectureNote, Statement, Topic

    tpl = load_template(MOM)
    st = lambda t, k="para": Statement(text=t, slide_refs=[1], kind=k)
    note = LectureNote(title="강의 제목", ref_style="para", meta={"date": "2023-04-26", "subject": "면역학", "professor": "홍길동"},
                       topics=[Topic(heading="요약 정리", role="front", slide_numbers=[1], sections={"body": [st("x")]}),
                               Topic(heading="유전자 구성", chapter="MHC and its function", slide_numbers=[1],
                                     basics_title="구조", basics=["핵심1", "핵심2"],
                                     sections={"body": [st("본문"), st("주의", "advice"), st("참고", "reference")]})])
    out = export_mom(note, tpl, tmp_path / "m.docx", page_map={1: 5})
    d = Document(str(out))
    body = "\n".join(p.text for p in d.paragraphs) + "\n".join(c.text for t in d.tables for r in t.rows for c in r.cells)
    assert "1. MHC and its function" in body and "§ 1. 유전자 구성" in body and "기본정석" in body and "핵심1" in body
    assert "Advice" in body and "Reference" in body and "차 례" in body
    assert len(d.sections) == 3  # cover + 2 topics, each topic with its own banner header
    hdr = "\n".join(p.text for p in d.sections[2].header.paragraphs)
    assert "1. MHC and its function" in hdr and "§ 1. 유전자 구성" in hdr
    assert "요약 정리" in "\n".join(p.text for p in d.sections[1].header.paragraphs)
    toc = [p.text for p in d.paragraphs if p.text.startswith("§ 1. 유전자 구성")]
    assert toc and toc[0].endswith("5p")  # page number from page_map


def test_style_guide_skill_is_loadable():
    from app.generate_notes import load_style_guide

    g = load_style_guide()
    assert "기본정석" in g and "dictation" in g and "{b|" in g


STRUCT2 = """Limbic 테스트 — 40분 강의 스크립트 역구성
자료: 「2022.11.02 신경과학1 Limbic system」 13쪽 강의 정리본 | 추정 시간: 40분
주의: 가상 스크립트입니다.
강의 진행표
00:00–02:00 | 도입: 오늘 강의의 범위
자료 기준: 3쪽
오늘은 세 가지 구조를 봅니다. 편도체는 공포와 관련됩니다.
02:00–04:00 | 편도체의 위치
자료 기준: 3쪽
편도체는 uncus 안쪽에 있습니다.
04:00–06:00 | 정리
자료 기준: 3–12쪽
정리하면 편도체는 fear입니다.
자료 충실도 및 제한
원본에 반복적으로 나타나는 지점을 중심으로 재구성했습니다.
"""


def test_second_header_format_without_brackets():
    from app.transcript import is_structured, parse_flow_script, parse_structured_script

    assert is_structured(STRUCT2)
    meta, segs = parse_flow_script(STRUCT2)
    assert meta["date"] == "2022-11-02" and meta["subject"] == "신경과학1" and meta["title"] == "Limbic system"
    assert [g.kind for g in segs] == ["speech", "speech", "speech", "note"]
    assert not any("자료 기준" in g.text or "00:00" in g.text for g in segs)
    _, units = parse_structured_script(STRUCT2)
    assert [u.pages for u in units[:3]] == ["3", "3", "3–12"]


def test_long_speech_line_with_time_range_is_not_a_header():
    from app.transcript import is_structured

    speech = "\n".join(f"[0{i}:00–0{i}:30] " + "아주 긴 발화 문장입니다 " * 12 for i in range(1, 5))
    assert not is_structured(speech)


def test_markup_leak_warning(tmp_path):
    from app.generate_notes import PrecomputedBackend
    from app.models import Statement, Topic
    from app.pipeline import run_pipeline

    t = Topic(heading="x", slide_numbers=[1, 2, 3, 4], sections={"body": [
        Statement(text=BODY + " *이탤릭 시도* 와 {x|잘못된}", slide_refs=[1, 2, 3, 4])]})
    rep, _ = run_pipeline(None, tmp_path / "o", MOM, script=_write(tmp_path), backend=PrecomputedBackend([t]), pdf=False)
    assert "MARKUP_LEAK" in {i.code for i in rep.issues}


def test_example_notes_have_no_markup_leaks():
    import re as _re
    from pathlib import Path as _P

    for f in ("tcell_note.py", "limbic_note.py"):
        src = (_P(__file__).resolve().parent.parent / "examples" / f).read_text(encoding="utf-8")
        assert not _re.search(r'(?<!\*)\*(?!\*)[^*\n"]+?(?<!\*)\*(?!\*)', src), f


def test_pad_cited_statement_must_be_blue_and_box_rule(tmp_path, monkeypatch):
    from app.exam import EXAM_BASE as X
    from app.models import Statement, Topic

    units = [1, 2, 3, 4, X + 1, X + 2, X + 3, X + 4]
    base = Statement(text=BODY, slide_refs=[1, 2, 3, 4])
    red_only = Statement(text="{r|PAD 내용인데 파랑이 아님}", slide_refs=[2, X + 1])
    gray_meta = Statement(text="{g|PAD 해설은 작성자 코멘트}", slide_refs=[X + 1])
    t = Topic(heading="t", slide_numbers=units, basics=["{b|박스 파랑}"], sections={"body": [base, red_only, gray_meta]})
    rep, _ = _exam_run(tmp_path, monkeypatch, [t], tpl=MOM)
    errs = [(i.code, i.message) for i in rep.errors]
    assert any(c == "PAD_NOT_BLUE" and "PAD 내용인데" in m for c, m in errs)      # red-only PAD statement: error
    assert not any("작성자 코멘트" in m for _, m in errs)                          # gray meta is allowed
    assert any(c == "BLUE_WITHOUT_PAD" and "기본정석" in m for c, m in errs)        # blue box line without basics_refs

    t.basics_refs = [X + 1]
    rep2, _ = _exam_run(tmp_path / "b" if (tmp_path / "b").mkdir() is None else tmp_path, monkeypatch, [t], tpl=MOM)
    assert not any("기본정석" in i.message for i in rep2.errors)


def test_skill_has_non_negotiable_blue_rule():
    from pathlib import Path as _P

    txt = (_P(__file__).resolve().parent.parent / ".claude/skills/readable-note-organizer/SKILL.md").read_text(encoding="utf-8")
    head = txt[: txt.index("## 1.")]
    assert "NON-NEGOTIABLE" in head and "BLUE = PAD" in head and "PAD_NOT_BLUE" in head


def test_exam_parser_limbic_style():
    from app.exam import EXAM_BASE, parse_exam_text

    txt = """- 1 -
 20학번 김인범교수님
 (작성자 코멘트 : x)
53. 편도핵과 고위감각겉질영역 사이의 연결이 비정상일 때 문제는?
① 중심핵 ② 바닥가쪽핵

답: 5
 해설: basolateral 은 고위 연합 입력

서술형 9. 시상과의 연결통로를 서술하시오.
Septal nucleus
답 :

Amygdala : ventral amygdalofugal pathway
- 2 -
 18학번 김인범교수님
21. Septal area와 연결되는 신경을 모두 고르시오.
1) fornix
2) medial lemniscus
    정답 : 1, 3
    해설
 1. Papez 회로
 2. 다른 설명
"""
    it = parse_exam_text(txt)
    assert [(i.cohort, i.year, i.q_no) for i in it] == [("20학번", 0, 53), ("20학번", 0, 9), ("18학번", 0, 21)]
    assert it[0].answer == "5" and "basolateral" in it[0].commentary
    assert it[1].question.startswith("[서술형]") and it[1].answer.startswith("Amygdala")
    assert it[2].answer == "1, 3" and "Papez" in it[2].commentary  # numbered commentary is not a new question
    assert it[0].label == "PAD 20학번 Q53" and it[0].number == EXAM_BASE + 1


# ----------------------------------------------------------------------------- figures / offline / prepare
def _make_pdf(path, pages):
    """pages: list of (text, [(color, rect)]) -> a PDF with coloured 'pictures' (real embedded images)."""
    import pymupdf
    from PIL import Image
    import io

    doc = pymupdf.open()
    for text, pics in pages:
        page = doc.new_page(width=540, height=780)
        page.insert_text((40, 60), text, fontsize=11)
        for color, rect in pics:
            im = Image.new("RGB", (300, 220), color)
            for x in range(0, 300, 20):  # structure so it is not a flat colour
                for y in range(0, 220, 20):
                    if (x // 20 + y // 20) % 2:
                        im.putpixel((x, y), (255, 255, 255))
            buf = io.BytesIO(); im.save(buf, "PNG")
            page.insert_image(pymupdf.Rect(*rect), stream=buf.getvalue())
    doc.save(str(path))


def test_pdf_figures_extracted_with_decoration_filter(tmp_path):
    pytest = __import__("pytest"); pytest.importorskip("pymupdf")
    from app.figures import extract_pdf_figures

    pdf = tmp_path / "h.pdf"
    logo = ((200, 30, 30), (10, 10, 40, 30))  # tiny logo on every page -> decoration
    _make_pdf(pdf, [("MHC class I structure", [((30, 90, 200), (60, 200, 360, 420)), logo]),
                    ("Superantigen binds TCR", [((200, 90, 30), (60, 200, 360, 420)), logo]),
                    ("Anchor residues", [((30, 160, 90), (60, 200, 360, 420)), logo])])
    figs = extract_pdf_figures(pdf, tmp_path / "f")
    assert len(figs) == 3 and [f.page for f in figs] == [1, 2, 3]  # logos dropped (tiny / repeated)
    assert "Superantigen" in figs[1].context and all(Path(f.path).exists() for f in figs)


def test_text_like_image_detection(tmp_path):
    from PIL import Image, ImageDraw

    from app.figures import looks_like_text_image

    t = Image.new("RGB", (400, 300), "white"); d = ImageDraw.Draw(t)
    for y in range(20, 280, 18):
        d.text((20, y), "bullet point text line here", fill="black")
    t.save(tmp_path / "t.png")
    c = Image.new("RGB", (400, 300), (240, 235, 220)); ImageDraw.Draw(c).ellipse((60, 40, 340, 260), fill=(210, 150, 140))
    c.save(tmp_path / "c.png")
    assert looks_like_text_image(tmp_path / "t.png") and not looks_like_text_image(tmp_path / "c.png")


def _note_for_figures():
    from app.models import LectureNote, Statement, Topic

    st = lambda t, k="para": Statement(text=t, kind=k, slide_refs=[1])
    t1 = Topic(heading="MHC 구조", slide_numbers=[1], sections={"body": [
        st("★ HLA 구조", "star"), st("MHC class I 유전자는 6번 염색체에 있다 HLA-A HLA-B HLA-C"),
        st("★ 기타", "star"), st("기타 설명 문장")]})
    t2 = Topic(heading="Superantigen", slide_numbers=[2], sections={"body": [
        st("★ 초항원", "star"), st("Superantigen은 TCR과 MHC class II에 동시에 결합한다 enterotoxin TSST-1")]})
    return LectureNote(title="t", topics=[t1, t2])


def test_figures_placed_by_text_and_order_and_overrides(tmp_path):
    pytest = __import__("pytest"); pytest.importorskip("pymupdf")
    from app.figures import apply_overrides, extract_pdf_figures, place_figures

    pdf = tmp_path / "h.pdf"
    _make_pdf(pdf, [("MHC class I HLA-A HLA-B HLA-C chromosome structure", [((30, 90, 200), (60, 200, 360, 420))]),
                    ("Superantigen TCR MHC class II enterotoxin TSST-1", [((200, 90, 30), (60, 200, 360, 420))])])
    tpl = load_template(MOM)
    note = _note_for_figures()
    figs = extract_pdf_figures(pdf, tmp_path / "f")
    place_figures(note, figs, tpl)
    assert [f.topic for f in figs] == [0, 1]
    kinds = [s.kind for s in note.topics[0].sections["body"]]
    assert kinds.index("figure") == 2  # after the matching ★ block's first paragraph, not after the other block
    assert [s.kind for s in note.topics[1].sections["body"]].count("figure") == 1
    # manual override: move figure 1 to the Superantigen section and rename it
    note2 = _note_for_figures()
    figs2 = extract_pdf_figures(pdf, tmp_path / "f2")
    ov = tmp_path / "o.json"
    ov.write_text(json.dumps([{"id": 1, "topic_heading": "Superantigen", "anchor": "초항원", "caption": "수정된 캡션"},
                              {"id": 2, "skip": True}], ensure_ascii=False), encoding="utf-8")
    apply_overrides(figs2, ov)
    place_figures(note2, figs2, tpl)
    assert [s.kind for s in note2.topics[0].sections["body"]].count("figure") == 0
    fig = [s for s in note2.topics[1].sections["body"] if s.kind == "figure"]
    assert len(fig) == 1 and fig[0].text.startswith("수정된 캡션")


def test_figure_rendered_in_docx_with_caption(tmp_path):
    from PIL import Image

    from app.export_mom import export_mom
    from app.models import LectureNote, Statement, Topic

    Image.new("RGB", (300, 200), (40, 90, 200)).save(tmp_path / "x.png")
    note = LectureNote(title="t", ref_style="para", topics=[Topic(heading="a", slide_numbers=[1], sections={"body": [
        Statement(text="본문", slide_refs=[1]),
        Statement(text="MHC 구조 도식", kind="figure", image=str(tmp_path / "x.png"), slide_refs=[1])]})])
    d = Document(str(export_mom(note, load_template(MOM), tmp_path / "f.docx")))
    assert len(d.inline_shapes) == 1 and any(p.text.startswith("그림 1. MHC 구조 도식") for p in d.paragraphs)


def test_slide_pdf_input_places_images_with_their_slide(tmp_path):
    pytest = __import__("pytest"); pytest.importorskip("pymupdf")
    from app.pipeline import run_pipeline

    pdf = tmp_path / "slides.pdf"
    _make_pdf(pdf, [("Slide one title\nMHC structure", [((30, 90, 200), (60, 200, 360, 420))]),
                    ("Slide two title\nSuperantigen", [])])
    tpl = tmp_path / "plain.yaml"
    tpl.write_text(MOM.read_text(encoding="utf-8").replace("layout: mom", "layout: plain"), encoding="utf-8")
    rep, paths = run_pipeline(pdf, tmp_path / "o", tpl, pdf=False)
    assert not [i for i in rep.errors if i.code == "IMAGE_LOST"], rep.errors
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    figs = [s for t in note["topics"] for sts in t["sections"].values() for s in sts if s["kind"] == "figure"]
    assert len(figs) == 1 and note["topics"][0]["images"] == []


def test_study_voice_conversion():
    from app.offline_organizer import clean_sentences, to_study_voice

    assert [to_study_voice(x) for x in ("합니다.", "봅니다.", "됩니다.", "입니다.", "있습니다.", "보세요.", "배웠죠.", "할 겁니다.")] == \
        ["한다.", "본다.", "된다.", "이다.", "있다.", "보자.", "배웠다.", "할 것이다."]
    out = clean_sentences("자, 이제 그림을 보겠습니다. MHC는 6번 염색체에 있습니다. 꼭 기억하세요.")
    assert out == ["MHC는 6번 염색체에 있다.", "꼭 기억하자."]  # pure speech noise dropped, content (6번) kept


def test_pad_matcher_blue_only_on_real_overlap():
    from app.exam import parse_exam_text
    from app.pad_match import PadMatcher

    m = PadMatcher(parse_exam_text(PAD))
    assert m.match("Class I의 polymorphism은 HLA-B > HLA-A > HLA-C 순서이다 B>A>C")  # shares informative terms
    assert m.match("오늘은 날씨가 좋다") == []
    assert m.match("lipid 항원은 CD1c가 제시한다 NKT cell") == [1002]


def test_offline_backend_organizes_flow_and_colours_pad(tmp_path, monkeypatch):
    import app.exam as exam
    from app.generate_notes import OfflineBackend
    from app.pipeline import run_pipeline

    monkeypatch.setattr(exam, "pdf_text", lambda p: PAD)
    script = tmp_path / "s.txt"
    script.write_text("""자, 오늘은 MHC를 봅니다. Class I의 polymorphism은 HLA-B, HLA-A, HLA-C 순서입니다. 꼭 기억하세요.

CD1c는 lipid 항원을 제시하고 NKT cell을 활성화합니다. 이제 다음으로 넘어가겠습니다.

그림을 보면 구조가 보입니다. FcRn은 IgG를 전달합니다.

재구성 및 검증 참고
가상 40분 강의입니다.
""", encoding="utf-8")
    # make it look like a structured doc is not needed: plain paragraphs are fine
    rep, paths = run_pipeline(None, tmp_path / "o", MOM, script=script, backend=OfflineBackend(), pdf=False,
                              exam_pdf=tmp_path / "pad.pdf", toc="heuristic")
    assert not rep.errors, rep.errors
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    text = json.dumps(note["topics"], ensure_ascii=False)
    assert "습니다" not in text.replace("재구성", "")  # spoken endings converted
    assert note["meta"]["objectives"] and "파랑" in note["meta"]["tips"]  # offline cover: 학습목표 + 공부 전략 filled
    assert "{b|" in text and "{r|" in text
    assert any(t["role"] == "front" for t in note["topics"])  # 핵심 어휘 / 요약 정리 built offline
    assert all(t["basics"] for t in note["topics"] if t["role"] == "body")
    # blue only where a PAD unit is cited (validator would have errored otherwise)
    off = run_pipeline(None, tmp_path / "o2", MOM, script=script, backend=OfflineBackend(auto_blue=False), pdf=False,
                       exam_pdf=tmp_path / "pad.pdf", toc="heuristic")[1]
    assert "{b|" not in off["note"].read_text(encoding="utf-8")


def test_prepare_writes_work_packet(tmp_path, monkeypatch):
    import app.exam as exam
    from app.prepare import prepare_brief

    monkeypatch.setattr(exam, "pdf_text", lambda p: PAD)
    brief = prepare_brief(_write(tmp_path, STRUCT2), tmp_path / "w", MOM, exam_pdf=tmp_path / "pad.pdf")
    names = {p.name for p in brief.iterdir()}
    assert {"TASK.md", "paragraphs.md", "exam_items.md", "outline_proposal.json", "note_skeleton.json",
            "note_schema.json", "build_command.sh"} <= names
    assert "¶1" in (brief / "paragraphs.md").read_text(encoding="utf-8")
    assert "unit 1001" in (brief / "exam_items.md").read_text(encoding="utf-8")
    assert "--note-json" in (brief / "build_command.sh").read_text(encoding="utf-8")
    assert "PAD 기출 ONLY" in (brief / "TASK.md").read_text(encoding="utf-8") or "파랑 = PAD" in (brief / "TASK.md").read_text(encoding="utf-8")


# ----------------------------------------------------------------------------- diagrams / summary visuals
def _specs():
    from app.models import Arrow, Diagram, Group

    tree = Diagram(kind="tree", title="T", root="루트", groups=[Group(title=f"g{i}", items=["항목 {r|빨강}", "{b|파랑}"]) for i in range(5)])
    flow = Diagram(kind="flow", groups=[Group(title="A", items=["a"]), Group(title="B", items=["b"]), Group(title="C", items=["c"])],
                   arrows=[Arrow(src=0, dst=1, label="입력"), Arrow(src=0, dst=2, label="건너뜀", both=True)])
    comp = Diagram(kind="compare", row_labels=["r1", "r2"], groups=[Group(title="X", items=["1", "2"]), Group(title="Y", items=["3", "4"])])
    return tree, flow, comp


def test_diagrams_render_with_note_colours(tmp_path):
    from PIL import Image

    from app.diagrams import diagram_has_exam, render_diagram

    for i, spec in enumerate(_specs()):
        p = render_diagram(spec, tmp_path / f"d{i}.png")
        with Image.open(p) as im:
            assert im.width == 1700 and im.height > 150
            px = list(im.convert("RGB").getdata())
        if i == 0:  # BLUE text and red text are really drawn (same colours as the body text)
            assert any(abs(r - 31) < 25 and abs(g - 78) < 25 and abs(b - 200) < 25 for r, g, b in px[::7])
            assert any(r > 170 and g < 40 and b < 40 for r, g, b in px[::7])
    assert diagram_has_exam(_specs()[0]) and not diagram_has_exam(_specs()[2])


def test_diagram_blue_requires_pad_and_summary_needs_visual(tmp_path, monkeypatch):
    from app.exam import EXAM_BASE as X
    from app.generate_notes import PrecomputedBackend
    from app.models import Statement, Topic

    tree, _, comp = _specs()
    body = Topic(heading="b", slide_numbers=[1, 2, 3, 4], sections={"body": [Statement(text=BODY, slide_refs=[1, 2, 3, 4])]})
    bad = Topic(heading="요약 정리", role="front", slide_numbers=[1], sections={"body": [
        Statement(text="도식", kind="diagram", diagram=tree, slide_refs=[1])]})  # blue node, no PAD ref
    rep, _ = _exam_run(tmp_path, monkeypatch, [bad, body], tpl=MOM)
    assert any(i.code == "BLUE_WITHOUT_PAD" and "도식" in i.message for i in rep.errors)
    ok = Topic(heading="요약 정리", role="front", slide_numbers=[1], sections={"body": [
        Statement(text="도식", kind="diagram", diagram=tree, slide_refs=[1, X + 1])]})
    rep2, _ = _exam_run(tmp_path / "ok" if (tmp_path / "ok").mkdir() is None else tmp_path, monkeypatch, [ok, body], tpl=MOM)
    assert not any(i.code in ("BLUE_WITHOUT_PAD", "SUMMARY_NO_VISUAL") and "도식" in i.message or i.code == "SUMMARY_NO_VISUAL"
                   for i in rep2.issues)
    plain = Topic(heading="요약 정리", role="front", slide_numbers=[1], sections={"body": [Statement(text="글만", slide_refs=[1])]})
    rep3, _ = _exam_run(tmp_path / "p" if (tmp_path / "p").mkdir() is None else tmp_path, monkeypatch, [plain, body], tpl=MOM)
    assert "SUMMARY_NO_VISUAL" in {i.code for i in rep3.issues}


def test_pipeline_renders_diagrams_into_docx(tmp_path):
    from app.generate_notes import PrecomputedBackend
    from app.models import Statement, Topic
    from app.pipeline import run_pipeline

    tree, flow, comp = _specs()
    tree.groups = tree.groups[:2]
    for g in tree.groups:
        g.items = ["항목 {r|빨강}"]  # no blue -> no PAD needed
    t = Topic(heading="요약 정리", role="front", slide_numbers=[1, 2, 3, 4], sections={"body": [
        Statement(text=BODY, slide_refs=[1, 2, 3, 4]),
        Statement(text="개념 지도", kind="diagram", diagram=tree, slide_refs=[1]),
        Statement(text="흐름", kind="diagram", diagram=comp, slide_refs=[1])]})
    rep, paths = run_pipeline(None, tmp_path / "o", MOM, script=_write(tmp_path), backend=PrecomputedBackend([t]), pdf=False)
    assert not rep.errors, rep.errors
    assert sorted(p.name for p in (tmp_path / "o" / "diagrams").iterdir()) == ["diagram_01.png", "diagram_02.png"]
    d = Document(str(paths["docx"]))
    caps = [p.text for p in d.paragraphs if p.text.startswith("도식 ")]
    assert caps == ["도식 1. 개념 지도", "도식 2. 흐름"] and len(d.inline_shapes) == 2


def test_summary_page_gets_best_figure_thumbnails(tmp_path):
    from PIL import Image

    from app.figures import add_summary_figures
    from app.models import Figure, LectureNote, Statement, Topic

    for n, col in (("a", (200, 40, 40)), ("b", (40, 40, 200))):
        Image.new("RGB", (300, 200), col).save(tmp_path / f"{n}.png")
    summary = Topic(heading="요약 정리", role="front", slide_numbers=[1], sections={"body": [Statement(text="x", slide_refs=[1])]})
    t1 = Topic(heading="A절", slide_numbers=[1]); t2 = Topic(heading="B절", slide_numbers=[2])
    note = LectureNote(title="t", topics=[summary, t1, t2])
    figs = [Figure(id=1, path=str(tmp_path / "a.png"), topic=1, score=0.5, caption="A 그림"),
            Figure(id=2, path=str(tmp_path / "b.png"), topic=1, score=0.9, caption="A 더 좋은 그림"),
            Figure(id=3, path=str(tmp_path / "b.png"), topic=2, score=0.4, caption="B 그림"),
            Figure(id=4, path=str(tmp_path / "a.png"), topic=2, score=0.99, caption="글자뿐", text_like=True)]
    add_summary_figures(note, figs, load_template(MOM), limit=4)
    sts = summary.sections["body"]
    thumbs = [s for s in sts if s.kind == "figure"]
    assert sts[1].text == "핵심 그림 모아보기" and [s.level for s in thumbs] == [1, 1]  # best per section, text-only skipped
    assert thumbs[0].text.startswith("A 더 좋은 그림") and thumbs[1].text.startswith("B 그림")
    add_summary_figures(note, figs, load_template(MOM), limit=0)  # disabled: nothing more added
    assert len([s for s in summary.sections["body"] if s.kind == "figure"]) == 2


def test_offline_summary_has_auto_concept_map(tmp_path):
    from app.generate_notes import OfflineBackend
    from app.pipeline import run_pipeline

    script = tmp_path / "s.txt"
    script.write_text("\n\n".join(f"MHC polymorphism{i} allele{i} haplotype{i} 설명입니다. 중요합니다.\n"
                                    f"Superantigen{i} TCR{i} enterotoxin{i} 을 봅니다." for i in range(8)), encoding="utf-8")
    rep, paths = run_pipeline(None, tmp_path / "o", MOM, script=script, backend=OfflineBackend(), pdf=False, toc="heuristic")
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    summ = next(t for t in note["topics"] if t["heading"] == "요약 정리")
    dia = [s for s in summ["sections"]["body"] if s["kind"] == "diagram"]
    assert len(dia) == 1 and dia[0]["diagram"]["kind"] == "tree" and dia[0]["diagram"]["groups"]
    assert "SUMMARY_NO_VISUAL" not in {i.code for i in rep.issues}
    assert (tmp_path / "o" / "diagrams" / "diagram_01.png").exists()


# ----------------------------------------------------------------------------- design strengthening (clinical example notes)
CLIN = Path(__file__).resolve().parent.parent / "templates" / "mom_clinical.yaml"


def test_markup_highlight_underline_and_second_blue():
    from app.markup import LEAK, PAD_TAGS, runs, strip, tags_used

    t = "a {y|팁} b {u|밑줄} c {c|하늘} d {b|파랑} **굵게**"
    assert strip(t) == "a 팁 b 밑줄 c 하늘 d 파랑 굵게"
    assert tags_used(t) == {"highlight", "underline", "exam_other", "exam"}
    assert set(PAD_TAGS) == {"exam", "exam_other"} and not LEAK.search(strip(t)) and LEAK.search("남은 {y|")


def _meta_note(**kw):
    from app.models import LectureNote, Statement, Topic

    st = lambda t, **k: Statement(text=t, slide_refs=[1], **k)
    body = [st("★ 소제목", kind="star"), st("{y|형광펜} 과 {u|밑줄} 과 {c|하늘색}"),
            st("- 고령\n설명 문장", kind="row2", left_title="Risk", left=["- Advanced age", "{r|TIMI}"]),
            st("두번째 행", kind="row2", left=["Row 2"]),
            st("사례: 67세 남성 흉통", kind="quiz", options=["Stable angina", "2. NSTEMI"], answer="2번 NSTEMI")]
    t = Topic(heading="Risk Stratification", slide_numbers=[1], basics_title="요약", basics=["핵심 한 줄"],
              tip="이건 다 외울 필요 없습니다.", sections={"body": body})
    return LectureNote(title="비ST분절 상승 ACS", ref_style="para", topics=[t],
                       meta={"date": "2025-10-30", "professor": "허성호", "comment": "코멘트\n둘째 줄",
                             "tips": "{y|가장 먼저 2쪽 진단}\n치료는 파랑 위주", "objectives": "진단을 설명할 수 있다.\n치료를 설명할 수 있다.",
                             "numbering_start": "4"}, **kw)


def test_clinical_layout_row2_quiz_tip_cover_and_roman_numbering(tmp_path):
    from app.export_mom import export_mom, numbering

    note = _meta_note()
    assert numbering(note, roman=True)[0]["section"] == "IV. Risk Stratification"  # continues from the previous period
    d = Document(str(export_mom(note, load_template(CLIN), tmp_path / "c.docx")))
    xml = d.element.xml
    assert 'w:val="double"' in xml  # double-line title box
    cells = [c.text for t in d.tables for r in t.rows for c in r.cells]
    text = "\n".join(p.text for p in d.paragraphs) + "\n".join(cells)
    assert "작성자 코멘트" in text and "가장 먼저 2쪽 진단" in text and "학습목표" in text and "1. 진단을 설명할 수 있다." in text
    assert "공부 팁" in text and "이건 다 외울 필요 없습니다." in text
    assert "IV. Risk Stratification" in text  # plain heading in the body (header = page number only)
    row_tables = [t for t in d.tables if len(t.columns) == 2]
    assert len(row_tables) == 1 and len(row_tables[0].rows) == 2  # consecutive row2 -> ONE table with 2 rows
    assert "Risk" in row_tables[0].cell(0, 0).text and "설명 문장" in row_tables[0].cell(0, 1).text
    assert "QUIZ 1." in text and "→ 정답: 2번 NSTEMI" in text and "1. Stable angina" in text and "2. NSTEMI" in text
    assert 'w:fill="DCE9F7"' in xml  # light-blue sub-heading band
    assert 'w:highlight w:val="yellow"' in xml and "<w:u " in xml


def test_two_blues_follow_the_professor(tmp_path, monkeypatch):
    from app.exam import EXAM_BASE as X
    from app.models import Statement, Topic

    cl = tmp_path / "clin.yaml"
    cl.write_text(CLIN.read_text(encoding="utf-8"), encoding="utf-8")
    pad_prof = PAD.replace("김태규", "허성호")  # PAD 2021 + 2022 + 2009 by the lecturer in charge
    import app.exam as exam

    monkeypatch.setattr(exam, "pdf_text", lambda p: pad_prof)
    from app.generate_notes import PrecomputedBackend
    from app.pipeline import run_pipeline

    def run(topics, sub="r"):
        s = _write(tmp_path)
        return run_pipeline(None, tmp_path / sub, cl, script=s, backend=PrecomputedBackend(topics), pdf=False,
                            exam_pdf=tmp_path / "pad.pdf", toc="heuristic", meta={"professor": "허성호"})[0]

    base = Statement(text=BODY, slide_refs=[1, 2, 3, 4])
    units = [1, 2, 3, 4]
    good = [base, Statement(text="{b|담당 교수님 파드}", slide_refs=[2, X + 1])]
    assert not [i for i in run([Topic(heading="t", slide_numbers=units, sections={"body": good})], "ok").errors]
    # PAD of the lecturer in charge cited from a sky-blue span -> error ; other-professor PAD in dark blue -> error
    bad = [base, Statement(text="{c|하늘색인데 담당 교수님 파드}", slide_refs=[2, X + 1])]
    rep = run([Topic(heading="t", slide_numbers=units, sections={"body": bad})], "bad")
    assert "BLUE_WRONG_PROFESSOR" in {i.code for i in rep.errors}
    other = PAD.replace("20학번 (2022년) 김태규 교수님", "20학번 (2022년) 이문용 교수님")
    monkeypatch.setattr(exam, "pdf_text", lambda p: other)
    bad2 = [base, Statement(text="{b|다른 교수님 파드인데 진한 파랑}", slide_refs=[2, X + 1])]
    rep2 = run([Topic(heading="t", slide_numbers=units, sections={"body": bad2})], "bad2")
    assert "BLUE_WRONG_PROFESSOR" in {i.code for i in rep2.errors}
    ok2 = [base, Statement(text="{c|다른 교수님 파드}", slide_refs=[2, X + 1])]
    assert "BLUE_WRONG_PROFESSOR" not in {i.code for i in run([Topic(heading="t", slide_numbers=units, sections={"body": ok2})], "ok2").errors}


def test_pad_colour_rule_covers_row2_and_quiz_fields(tmp_path, monkeypatch):
    from app.exam import EXAM_BASE as X
    from app.models import Statement, Topic

    base = Statement(text=BODY, slide_refs=[1, 2, 3, 4])
    row = Statement(text="설명", kind="row2", left=["{b|왼쪽 파랑}"], slide_refs=[2])  # blue, no PAD
    quiz = Statement(text="사례", kind="quiz", options=["{b|선지 파랑}"], answer="1", slide_refs=[2, X + 1])  # blue + PAD: ok
    units = [1, 2, 3, 4, X + 1, X + 2, X + 3, X + 4]
    rep, _ = _exam_run(tmp_path, monkeypatch, [Topic(heading="t", slide_numbers=units, sections={"body": [base, row, quiz]})], tpl=MOM)
    errs = [i for i in rep.errors if i.code == "BLUE_WITHOUT_PAD"]
    assert len(errs) == 1 and "왼쪽 파랑" in errs[0].message or len(errs) == 1


def test_cli_meta_json_and_cover_stays_on_one_page(tmp_path):
    from app.cli import main

    s = _write(tmp_path)
    mj = tmp_path / "m.json"
    mj.write_text(json.dumps({"tips": ["팁 하나", "팁 둘"], "objectives": ["목표 하나", "목표 둘"], "comment": "간단"}, ensure_ascii=False), encoding="utf-8")
    rc = main(["build", "--script", str(s), "--template", str(MOM), "--toc", "heuristic", "--out", str(tmp_path / "o"),
               "--no-pdf", "--meta-json", str(mj)])
    assert rc == 0
    d = Document(str(tmp_path / "o" / "s_강의록.docx"))
    text = "\n".join(p.text for p in d.paragraphs)
    assert "팁 둘" in text and "1. 목표 하나" in text


def test_offline_slide_table_mode_groups_slides_into_two_column_rows(sample_pptx, marked_script, tmp_path):
    from app.pipeline import run_pipeline

    rep, paths = run_pipeline(sample_pptx, tmp_path / "o", CLIN, script=marked_script, pdf=False, toc="heuristic")
    assert not [i for i in rep.errors if i.code in ("SLIDE_MISSING", "SEGMENT_LOST")], rep.errors
    note = json.loads(paths["note"].read_text(encoding="utf-8"))
    rows = [s for t in note["topics"] for sts in t["sections"].values() for s in sts if s["kind"] == "row2"]
    assert len(rows) == 3 and rows[0]["left_title"].startswith("Ulcerative")
    assert "직장에서 시작합니다" in rows[0]["text"] or "직장에서 시작한다" in rows[0]["text"]  # lecturer explanation on the right
    d = Document(str(paths["docx"]))
    two_col = [t for t in d.tables if len(t.columns) == 2]
    assert two_col and sum(len(t.rows) for t in two_col) >= 3

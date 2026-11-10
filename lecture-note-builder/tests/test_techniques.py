from docx import Document
from PIL import Image

from app.export_mom import export_mom
from app.markup import runs
from app.models import AlignedSlide, LectureNote, Segment, Slide, Statement, Topic
from app.prepare import effort_cues
from app.template import load_template
from app.validate_notes import validate


def _tpl():
    return load_template("templates/mom_compact.yaml")


def _note(extra=None):
    sts = [
        Statement(text="RR은 NDP를 dNDP로 바꾼다.", slide_refs=[1], effort="필수"),
        Statement(text="항암제 5-FU는 효소를 속이는 스파이 같은 존재다", origin="author"),
        Statement(text="이름만 알아 두면 된다.", slide_refs=[1], effort="참고"),
        Statement(text="RR은 ATP에는 결합하지만 GDP에는 결합하지 않는다.", kind="check", answer="X", slide_refs=[1],
                  left_title="RR은 염기 종류를 가리지 않는다", explanations=["ADP·GDP·CDP·UDP 모두 결합"]),
        Statement(text="RR은 NDP를 환원한다.", kind="check", answer="O", slide_refs=[1]),
        Statement(text="", kind="concept", left_title="Uracil vs Thymine", left=["- Thymine = 5-methyl-uracil"], slide_refs=[1]),
        Statement(text="가장 알맞은 것은?", kind="quiz", options=["① a", "② b"], answer="② b",
                  explanations=["① a는 틀림", "② b가 맞다 (정답)"], slide_refs=[1]),
    ] + (extra or [])
    return LectureNote(title="t", ref_style="para", topics=[Topic(heading="§a", chapter="장", slide_numbers=[1], sections={"body": sts})])


def _slides():
    sl = Slide(number=1, title="u", body=[])
    return [sl], [AlignedSlide(slide_number=1, segments=[Segment(id=1, text="RR은 NDP를 dNDP로 바꾼다. 이름만 알아 두면 된다.")])]


def test_renders_check_effort_author_concept_explanations(tmp_path):
    doc = Document(str(export_mom(_note(), _tpl(), tmp_path / "n.docx")))
    text = "\n".join(p.text for p in doc.paragraphs)
    cells = "\n".join(c.text for t in doc.tables for r in t.rows for c in r.cells)
    assert "[필수]" in text and "[참고]" in text
    assert "(항암제 5-FU는 효소를 속이는 스파이 같은 존재다)" in text  # author addition in grey ( )
    assert "개념 Check!" in cells and "1. RR은 ATP에는" in cells and "(O, X)" in cells
    assert "정답" in cells and "1. X" in cells and "2. O" in cells  # answers collected at the end of the topic
    assert "ADP·GDP·CDP·UDP 모두 결합" in cells
    assert "개념 정리" in cells and "Thymine = 5-methyl-uracil" in cells
    assert "해설" in text and "② b가 맞다 (정답)" in text


def test_new_features_never_produce_blue(tmp_path):
    doc = Document(str(export_mom(_note(), _tpl(), tmp_path / "n.docx")))
    blue = [r.font.color.rgb for p in doc.paragraphs for r in p.runs if r.font.color and r.font.color.rgb and
            str(r.font.color.rgb) in ("0000FF", "2F5FB3", "0070C0")]
    assert blue == []
    sl, al = _slides()
    rep = validate(_note(), sl, al, _tpl())
    assert not [i for i in rep.issues if "BLUE" in i.code]


def test_blue_rule_still_enforced_on_new_kinds():
    sl, al = _slides()
    bad = Statement(text="{b|파랑 개념 확인}", kind="check", answer="O", slide_refs=[1])
    rep = validate(_note([bad]), sl, al, _tpl())
    assert any(i.code == "BLUE_WITHOUT_PAD" for i in rep.issues)  # blue without a PAD citation is an error here too
    author_blue = Statement(text="{b|비유}", origin="author")
    rep = validate(_note([author_blue]), sl, al, _tpl())
    assert any(i.code == "BLUE_WITHOUT_PAD" for i in rep.issues)  # author additions cannot be blue either


def test_check_validation_and_author_exemption():
    sl, al = _slides()
    rep = validate(_note([Statement(text="x", kind="check", answer="maybe", slide_refs=[1])]), sl, al, _tpl())
    assert any(i.code == "CHECK_BAD_ANSWER" for i in rep.issues)
    rep = validate(_note([Statement(text="n", kind="check", answer="O", slide_refs=[9])]), sl, al, _tpl())
    assert any(i.code in ("CHECK_NOT_GROUNDED", "BAD_REF") for i in rep.issues)
    rep = validate(_note(), sl, al, _tpl())  # the author statement has no source and still raises no NO_SOURCE
    assert not [i for i in rep.issues if i.code == "NO_SOURCE"]


def test_effort_cues_from_lecture_speech():
    segs = [Segment(id=1, text="이거는 외우실 필요 없어요. 진짜 이거 맨날 나와요."),
            Segment(id=2, text="평범한 문장이다."),
            Segment(id=3, text="이름 정도만 알아두라고 하시네요.", kind="speech")]
    out = effort_cues(segs)
    assert (1, "참고") in [(i, e) for i, e, _, _ in out] and (1, "필수") in [(i, e) for i, e, _, _ in out]
    assert 2 not in [i for i, *_ in out] and (3, "참고") in [(i, e) for i, e, *_ in out]


def test_markdown_keeps_new_fields(tmp_path):
    from app.export_docx import export_markdown

    md = export_markdown(_note(), _tpl(), tmp_path / "n.md").read_text(encoding="utf-8")
    assert "[필수]" in md and "(항암제 5-FU" in md and "개념 Check" in md and "개념 정리" in md


def test_parse_pad_docx(tmp_path):
    from app.exam import EXAM_BASE, parse_exam_pdf

    d = Document()
    for line in ["2025년 주지현 교수님", "(세포치료) 줄기세포 – 주지현 교수님", "27. 임상시험용으로 받는 허가는?", "IND 허가", "NDA 승인",
                 "답 | 1", "해설 | IND는 초기 허가임.", "작년 출제예고입니다.", "아래로는 전부 주지현 교수님입니다.",
                 "2022년 주지현 교수님", "1. iPSC가 만들어지는 과정은?", "1) reproduction", "3) reprogramming", "답: 3)",
                 "공식해설: 체세포를 Yamanaka factor로 …"]:
        d.add_paragraph(line)
    f = tmp_path / "pad.docx"
    d.save(f)
    items = parse_exam_pdf(f)  # .docx goes through the Word parser
    assert [(i.number, i.year, i.q_no, i.answer) for i in items] == [(EXAM_BASE + 1, 2025, 27, "1"), (EXAM_BASE + 2, 2022, 1, "3)")]
    assert "NDA 승인" in items[0].question and "IND는 초기 허가임" in items[0].commentary
    assert items[0].label == "PAD 2025 Q27" and "2022" in items[1].title


def test_pad_title_year_is_not_a_lost_number():
    from app.exam import ExamItem
    from app.models import BodyLine

    it = ExamItem(number=1001, cohort="", year=2022, professor="주지현 교수님", course="", q_no=1, question="q", answer="3", commentary="")
    sl = Slide(number=1001, title=it.title, body=[BodyLine(text=it.question), BodyLine(text="정답: 3")])
    note = LectureNote(title="t", ref_style="para", topics=[Topic(heading="h", chapter="c", slide_numbers=[1001], sections={"body": [
        Statement(text="{b|정답은 3번} q", slide_refs=[1001])]})])
    rep = validate(note, [sl], [AlignedSlide(slide_number=1001, segments=[])], _tpl())
    assert not [i for i in rep.issues if i.code == "NUMBER_LOST" and "2022" in i.message]


def test_exam_signals_and_history():
    from app.exam import ExamItem, exam_history, exam_signals

    assert exam_signals("작년 출제예고, 이번에 강조한 부분은 아닙니다.") == ["출제예고", "강조안함"]
    assert exam_signals("작년과 올해 모두 강조한 내용 아닙니다.") == ["강조안함"]
    assert "미수업" in exam_signals("저희는 신장 오가노이드에 대해 안 배웠습니다.")
    assert "족보반복" in exam_signals("최근들어 각광을 받는 구조물은? (2019년 짤)")
    assert exam_signals("체세포를 Yamanaka factor로 만드는 과정은 reprogramming이다.") == []
    items = [ExamItem(1001, "", 2025, "주지현 교수님", "", 27, "q", "1", "작년 출제예고, 이번에 강조한 부분은 아닙니다.", signals=["출제예고", "강조안함"]),
             ExamItem(1002, "", 2023, "김용균 교수님", "", 1, "q", "3", "")]
    h = exam_history(items, "주지현")
    assert "주지현 교수님 1문항(2025년 1)" in h and "다른 교수님 1문항(2023년 1)" in h and "출제예고: 2025 Q27" in h


def test_pad_tags_and_only_pad(tmp_path):
    note = _note([Statement(text="{b|Ryoncil은 골수 유래 MSC이다}", slide_refs=[1002], origin="both"),
                  Statement(text="{b|Ryoncil은 GVHD에 처음 허가되었다}", slide_refs=[1, 1002], origin="both")])
    note.unit_labels = {1002: "PAD 2025 Q28"}
    doc = Document(str(export_mom(note, _tpl(), tmp_path / "n.docx")))
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "[Only PAD 2025 Q28]" in text and "[PAD 2025 Q28]" in text
    plain = load_template("templates/mom.yaml")  # pad_tags is opt-in: the default template prints nothing extra
    text2 = "\n".join(p.text for p in Document(str(export_mom(note, plain, tmp_path / "m.docx"))).paragraphs)
    assert "Only PAD" not in text2


def test_uncovered_pad_omit_option():
    sl = Slide(number=1001, title="x", body=[])
    base = _note()
    base.meta = {"pad_uncovered_units": "1001", "pad_uncovered_mode": "reference"}
    base.topics[0].slide_numbers.append(1001) if False else None
    al = [AlignedSlide(slide_number=1001, segments=[])]
    sl1, al1 = _slides()
    rep = validate(base, sl1 + [sl], al1 + al, _tpl())
    assert any(i.code == "PAD_UNUSED" for i in rep.issues)
    base.meta["pad_uncovered_mode"] = "omit"
    rep = validate(base, sl1 + [sl], al1 + al, _tpl())
    assert not any(i.code == "PAD_UNUSED" for i in rep.issues)


def test_line_density_and_omitted_numbers():
    sl, al = _slides()
    dense = Statement(text="ECM은 연골 기질이다 — 세포를 오래 살게 하고 · 기능을 촉진하며 · 규제 부담이 작고 · 이미 제품이 있고 · 수입도 한다", slide_refs=[1])
    rep = validate(_note([dense]), sl, al, _tpl())
    assert any(i.code == "LINE_TOO_DENSE" for i in rep.issues)
    sl2 = [Slide(number=1, title="u", body=[]), ]
    from app.models import BodyLine
    sl2 = [Slide(number=1, title="u", body=[BodyLine(text="주가가 10분의 1, 2주일 전 일")])]
    n = _note()
    rep = validate(n, sl2, al, _tpl())
    assert any(i.code == "NUMBER_LOST" for i in rep.issues)
    n.meta = {"omitted": "2주|10분|1"}
    rep = validate(n, sl2, al, _tpl())
    assert not any(i.code == "NUMBER_LOST" for i in rep.issues) and any(i.code == "OMITTED_BY_RULE" for i in rep.issues)


def test_omitted_terms_turn_term_lost_into_info():
    """Trivial English glosses of the transcript can be left out on purpose (meta.omitted_terms) instead of forcing parentheses."""
    from app.models import BodyLine

    sl = [Slide(number=1, title="u", body=[BodyLine(text="검체 스페시멘(Specimen)과 감수성 검사 Susceptibility test")])]
    _, al = _slides()
    n = _note([Statement(text="검체로 감수성 검사를 한다.", slide_refs=[1])])
    rep = validate(n, sl, al, _tpl())
    assert any(i.code == "TERM_LOST" and "Specimen" in i.message for i in rep.issues)
    n.meta = {"omitted_terms": "specimen|susceptibility test"}
    rep = validate(n, sl, al, _tpl())
    assert not any(i.code == "TERM_LOST" for i in rep.issues)
    assert any(i.code == "OMITTED_BY_RULE" and "Specimen" in i.message for i in rep.issues)

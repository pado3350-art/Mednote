"""Layout v2 (rule L16): rows tables, the lecturer's QA box, 핵심 답 band, checks at chapter end, page breaks."""
from docx import Document

from app.export_mom import export_mom
from app.mixed import mixed_issues
from app.models import LectureNote, Statement, Topic
from app.template import load_template


def _tpl(**fmt):
    tpl = load_template("templates/mom_mixed.yaml")
    tpl.format = tpl.format.model_copy(update=fmt)
    return tpl


def _topic(h, chapter, body, style="explain", basics=(), new_page=False):
    return Topic(heading=h, chapter=chapter, slide_numbers=[1], style=style, basics=list(basics), new_page=new_page,
                 sections={"body": body})


def _check(text, ans="O"):
    return Statement(text=text, kind="check", answer=ans, slide_refs=[1])


def _doc(tmp_path, topics, tpl):
    return Document(str(export_mom(LectureNote(title="t", topics=topics, ref_style="para"), tpl, tmp_path / "n.docx")))


def _cells(doc):
    return [c.text for tb in doc.tables for r in tb.rows for c in r.cells]


def test_mixed_template_is_layout_v2():
    f = load_template("templates/mom_mixed.yaml").format
    assert f.font_size_pt == 10.5 and f.basics_style == "band" and f.checks_where == "chapter" and f.chapter_page_break


def test_rows_table_and_qa_box(tmp_path):
    rows = Statement(text="", kind="rows", slide_refs=[1], col_titles=["", "정균제", "살균제"],
                     rows=[["작용", "증식 억제", "세균 사멸"], ["치유", "면역에 기댄다\n→ 면역이 약하면 어렵다", "중증 감염에 선택"]])
    qa = Statement(text="항균제를 쓰는 목적이 무엇인가?", kind="qa", left_title="역질문1", left=["목적은 네 가지로 나눈다."], slide_refs=[1])
    doc = _doc(tmp_path, [_topic("목적은?", "장", [qa, rows], style="list")], _tpl())
    cells = _cells(doc)
    assert "정균제" in cells and "살균제" in cells and "작용" in cells and "세균 사멸" in cells
    assert any("면역에 기댄다" in c and "→ 면역이 약하면 어렵다" in c for c in cells)  # "\n" = two lines in one cell
    paras = [p.text for p in doc.paragraphs]
    assert any(p.startswith("역질문1") and "목적이 무엇인가?" in p for p in paras)  # yellow question box (a paragraph)
    assert any(p.startswith("A.") and "네 가지" in p for p in paras)
    xml = doc.element.xml
    assert "FFC000" in xml and 'w:tblHeader' in xml
    first = doc.tables[-1].rows[1].cells[1].paragraphs[0]
    assert first.paragraph_format.keep_with_next  # a small table stays on one page


def test_basics_band_is_a_light_line_not_a_box(tmp_path):
    t = _topic("왜?", "장", [Statement(text="본문이다.", slide_refs=[1])], basics=["이것이 답이다."])
    band = _doc(tmp_path, [t], _tpl(basics_style="band"))
    assert any(p.text.startswith("핵심 답") and "이것이 답이다." in p.text for p in band.paragraphs)
    assert not any("핵심 답" in c for c in _cells(band))
    box = _doc(tmp_path, [t], _tpl(basics_style="box"))
    assert any("핵심 답" in c for c in _cells(box))


def test_checks_collected_at_chapter_end(tmp_path):
    t1 = _topic("가", "장1", [Statement(text="a", slide_refs=[1]), _check("첫째 문장이다.", "O")])
    t2 = _topic("나", "장1", [Statement(text="b", slide_refs=[1]), _check("둘째 문장이다.", "X")])
    t3 = _topic("다", "장2", [Statement(text="c", slide_refs=[1]), _check("셋째 문장이다.", "O")])
    chap = _cells(_doc(tmp_path, [t1, t2, t3], _tpl(checks_where="chapter")))
    boxes = [c for c in chap if "개념 Check!" in c]
    assert len(boxes) == 2  # one box per chapter
    assert "1. 첫째 문장이다." in boxes[0] and "2. 둘째 문장이다." in boxes[0] and "셋째" in boxes[1] and "1. 셋째" in boxes[1]
    assert sum("정답" in c for c in chap) == 2
    per_topic = _cells(_doc(tmp_path, [t1, t2, t3], _tpl(checks_where="topic")))
    assert sum("개념 Check!" in c for c in per_topic) == 3
    assert not any("개념 Check!" in c for c in _cells(_doc(tmp_path, [t1, t2, t3], _tpl(checks_where="off"))))


def test_chapter_and_section_page_breaks(tmp_path):
    body = [Statement(text="x", slide_refs=[1])]
    topics = [_topic("가", "장1", body, new_page=True), _topic("나", "장1", body, new_page=True), _topic("다", "장2", body)]
    assert len(_doc(tmp_path, topics, _tpl(chapter_page_break=True)).sections) == 4  # cover + 가 + 나 + 다(chapter 2)
    plain = [_topic("가", "장1", body), _topic("나", "장1", body), _topic("다", "장2", body)]
    assert len(_doc(tmp_path, plain, _tpl(chapter_page_break=False)).sections) == 2  # cover + one flowing body section


def test_mixed_checks_know_qa_and_tables():
    qa = Statement(text="질문?", kind="qa", left_title="질문1", left=["답"], slide_refs=[1])
    para = Statement(text="본문. 그럼 결론.", slide_refs=[1])
    ok = _topic("왜 그런가?", "장", [qa, para])  # no basics, but the lecturer's question box answers it
    bullets = _topic("결과", "장", [Statement(text=f"항목 {i}", kind="bullet", slide_refs=[1]) for i in range(4)]
                     + [Statement(text="즉 끝", kind="bullet", slide_refs=[1])], style="list")
    codes = {c for _, c, _ in mixed_issues(LectureNote(title="t", topics=[ok, bullets]))}
    assert "EXPLAIN_NO_ANSWER" not in codes and "LIST_NOT_TABLE" in codes
    table = _topic("결과", "장", [Statement(text="", kind="rows", rows=[["a", "b"]], slide_refs=[1]),
                                 Statement(text="즉 끝", kind="bullet", slide_refs=[1])], style="list")
    assert "LIST_NOT_TABLE" not in {c for _, c, _ in mixed_issues(LectureNote(title="t", topics=[table]))}


def test_markdown_export_has_tables_and_qa(tmp_path):
    from app.export_docx import export_markdown

    rows = Statement(text="", kind="rows", slide_refs=[1], col_titles=["", "A", "B"], rows=[["x", "1\n2", "3"]])
    qa = Statement(text="질문입니까?", kind="qa", left_title="질문1", left=["답입니다."], slide_refs=[1])
    note = LectureNote(title="t", topics=[_topic("가", "장", [qa, rows], style="list")], ref_style="para")
    md = export_markdown(note, _tpl(), tmp_path / "n.md")
    text = open(md, encoding="utf-8").read() if not isinstance(md, str) else md
    assert "> **질문1** 질문입니까?" in text and "- A. 답입니다." in text and "| x | 1<br>2 | 3 |" in text

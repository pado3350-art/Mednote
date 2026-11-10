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
    assert f.font_size_pt == 10.5 and f.basics_style == "band" and f.checks_where == "chapter" and not f.chapter_page_break


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
    assert "1. [§1] 첫째 문장이다." in boxes[0] and "2. [§2] 둘째 문장이다." in boxes[0]  # each check says which § it belongs to
    assert "1. [§1] 셋째 문장이다." in boxes[1]
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


def test_readability_checks():
    """Findings of review_vs_MOM.md section 10 become checks: long headings / paragraphs / bands, colour inside a paragraph."""
    from app.storyline import heading_issues

    long_h = _topic("항균제 선택에서 획득 경로(community acquired, nosocomial)와 면역 상태(competent, compromised)는 어떻게 작용하나?",
                    "경험적 치료에서 표적 치료로: 치료 과정, 정균제와 살균제, 환자 인자", [Statement(text="x", slide_refs=[1])])
    codes = [c for _, c, _ in heading_issues(LectureNote(title="t", topics=[long_h]))]
    assert codes.count("HEADING_TOO_LONG") == 2  # chapter and §
    paras = [Statement(text="가" * 200, slide_refs=[1]),
             Statement(text="앞 문장이 길게 이어진다 열아홉 자 넘게. {g|뒤에 회색 문장이 이어서 스무 자를 넘기도록 적는다.}", slide_refs=[1]),
             Statement(text="{b|파랑 한 문장이 전체 문단이면 길어도 된다. " + "나" * 190 + "}", slide_refs=[1])]
    t = _topic("제목", "장", paras, basics=["핵" * 70])
    got = {c for _, c, _ in mixed_issues(LectureNote(title="t", topics=[t]))}
    assert {"PARAGRAPH_TOO_LONG", "COLOUR_IN_PARAGRAPH", "BASICS_TOO_LONG"} <= got
    msgs = [m for _, c, m in mixed_issues(LectureNote(title="t", topics=[t])) if c == "PARAGRAPH_TOO_LONG"]
    assert len(msgs) == 1  # the all-blue PAD paragraph is exempt
    many = [_topic("가", "장", [_check(f"문장 {i}") for i in range(3)])]
    assert "CHECK_TOO_MANY" in {c for _, c, _ in mixed_issues(LectureNote(title="t", topics=many))}


def test_quiz_is_not_a_numbered_section_and_box_cover(tmp_path):
    body = [Statement(text="x", slide_refs=[1])]
    doc = _doc(tmp_path, [_topic("가", "장", body), _topic("QUIZ", "장", body)], _tpl())
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "§ 1. 가" in text and "§ 2. QUIZ" not in text
    assert load_template("templates/mom_mixed.yaml").format.cover_style == "box"


def test_table_orphan_check_and_thin_gap(tmp_path):
    from app.mixed import table_orphan_issues

    # 3.8 cm column holds ~9 Korean characters: 11 characters overflow by 2 -> a lone character would wrap
    bad = Statement(text="", kind="rows", slide_refs=[1], col_widths=[3.8, 13.6], rows=[["수술 전 예방적 항균제", "ok"]])
    fine = Statement(text="", kind="rows", slide_refs=[1], col_widths=[3.8, 13.6], rows=[["수술 전 예방", "ok"]])
    latin = Statement(text="", kind="rows", slide_refs=[1], col_widths=[3.8, 13.6], rows=[["community acquired", "ok"]])  # Latin wraps at spaces
    wide = Statement(text="", kind="rows", slide_refs=[1], rows=[["가" * 12, "나" * 30]])
    note = lambda st: LectureNote(title="t", topics=[_topic("가", "장", [st], style="list")])
    assert [c for _, c, _ in table_orphan_issues(note(bad))] == ["TABLE_ORPHAN"]
    assert table_orphan_issues(note(fine)) == [] and table_orphan_issues(note(latin)) == []
    from app.export_mom import rows_widths
    assert rows_widths(wide)[0] == 4.4 and abs(sum(rows_widths(wide)) - 17.4) < 1e-6


def test_chapter_end_does_not_leave_an_empty_page(tmp_path):
    """The spacer after the last box of a chapter is a thin exact-height paragraph (it cannot spill onto an empty page)."""
    t1 = _topic("가", "장1", [Statement(text="a", slide_refs=[1]), _check("첫째 문장이다.")])
    doc = _doc(tmp_path, [t1], _tpl())
    thin = [p for p in doc.paragraphs if hasattr(p.paragraph_format.line_spacing, "pt") and p.paragraph_format.line_spacing.pt <= 4]
    assert thin  # _gap() paragraphs exist after tables / boxes


def test_heading_exam_mark(tmp_path):
    t = _topic("획득 경로와 면역 상태", "장", [Statement(text="x", slide_refs=[1])])
    t.mark = "출제예고 · 기출"
    doc = _doc(tmp_path, [t], _tpl())
    assert any("획득 경로와 면역 상태" in p.text and "[출제예고 · 기출]" in p.text for p in doc.paragraphs)


def test_checks_only_with_pad_and_table_cells_in_gaejosik():
    from app.mixed import table_style_issues

    plain = _topic("가", "장", [Statement(text="본문. 그럼 결론.", slide_refs=[1]), _check("문장이다.")])
    pad = _topic("나", "장", [Statement(text="{b|PAD 문장}", slide_refs=[1, 1001]), _check("문장이다.")])
    codes = [(c, m) for _, c, m in mixed_issues(LectureNote(title="t", topics=[plain, pad]))]
    assert [m for c, m in codes if c == "CHECK_NO_PAD"] == ["'가': 기출(PAD)이 없는 소절에는 개념 Check를 두지 않는다."]  # only the section without a PAD item
    sent = Statement(text="", kind="rows", slide_refs=[1], rows=[["라벨", "외래는 경구가 기본이다.\n주사 필요 시 고려\n효과를 기대하기 어려움"]])
    got = table_style_issues(LectureNote(title="t", topics=[_topic("가", "장", [sent], style="list")]))
    assert [c for _, c, _ in got] == ["TABLE_CELL_STYLE"] and "1줄" in got[0][2]  # '-다' sentence flagged, 개조식 lines are not
    ok = Statement(text="", kind="rows", slide_refs=[1], rows=[["라벨 다", "외래는 경구가 기본\n사용 가능"]])
    assert table_style_issues(LectureNote(title="t", topics=[_topic("가", "장", [ok], style="list")])) == []

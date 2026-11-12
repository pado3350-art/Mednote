"""사시 정리본의 고정 구성과 콜아웃 박스 (L30-L34)."""
from docx import Document

from app.design.export_mom import export_mom
from app.models import LectureNote, Statement, Topic
from app.template import load_template
from app.write.mom_format import format_issues


def _tpl():
    return load_template("templates/mom_mixed.yaml")


def _note(**meta):
    body = Topic(heading="양안시", chapter="정상 시각 발달", slide_numbers=[1], style="explain", basics=["두 눈이 하나로 봄"], sections={"body": [
        Statement(text="(1) 정상 안구 정렬 = bifoveal fixation★", kind="sub", slide_refs=[1]),
        Statement(text="x", kind="callout", left_title="작성자 추가설명", left=["망막대응점은 ‘짝꿍이 되는 점’입니다.", "- 두 눈이 같은 방향가"], slide_refs=[1]),
        Statement(text="x", kind="callout", left_title="잠깐 정리하고 가기", left=["1. 안경 치료★"], slide_refs=[1]),
    ]})
    close = Topic(heading="Take home messages", role="closing", slide_numbers=[1], sections={"body": [
        Statement(text="1. 정상 시기능 = bifoveal fixation + NRC★", kind="sub", slide_refs=[1])]})
    return LectureNote(title="t", topics=[body, close], ref_style="para", meta=meta)


def test_points_callouts_sub_line_and_closing_chapter_render(tmp_path):
    note = _note(points="눈이 몰린 내사시 → **빠른 치료**\n- 굴절이상: 안경 치료\n자세를 기울인 사시 = 4번 뇌신경 마비")
    doc = Document(str(export_mom(note, _tpl(), tmp_path / "n.docx")))
    text = "\n".join(p.text for p in doc.paragraphs) + "\n" + "\n".join(c.text for tb in doc.tables for r in tb.rows for c in r.cells)
    assert "[강조점 두가지]" in text and "[작성자 추가설명]" in text and "[잠깐 정리하고 가기]" in text
    assert "(1) 정상 안구 정렬" in text and "짝꿍이 되는 점" in text
    assert "Ⅱ. Take home messages" in text and "[2] Take home" not in text  # the closing chapter has no [n] heading


def test_format_checks():
    codes = {c for _, c, _ in format_issues(_note())}
    assert {"POINTS_MISSING"} <= codes and "CLOSING_MISSING" not in codes
    bad = _note(points="a")
    bad.topics[0].sections["body"].append(Statement(text="그냥 문장", kind="sub", slide_refs=[1]))
    bad.topics[0].sections["body"].append(Statement(text="x", kind="callout", left_title="아무 상자", left=["a"], slide_refs=[1]))
    codes = {c for _, c, _ in format_issues(bad)}
    assert {"SUB_LINE_FORMAT", "CALLOUT_TITLE_UNKNOWN"} <= codes and "POINTS_MISSING" not in codes


def test_mom_heading_system_has_no_coloured_title_bands(tmp_path):
    """L27: front titles, chapter, [n] headings and (1) lines are plain bold text - no green / teal shading in the body."""
    import zipfile

    note = _note(points="a\n- b")
    note.topics.insert(0, Topic(heading="요약 ① 시각 경로", role="front", slide_numbers=[1], sections={"body": [Statement(text="x", slide_refs=[1])]}))
    for tpl in (_tpl(), load_template("templates/mom_compact.yaml")):
        if tpl.format.heading_system != "mom":
            tpl.format = tpl.format.model_copy(update={"heading_system": "mom"})
        out = export_mom(note, tpl, tmp_path / f"n_{tpl.template_name}.docx")
        xml = zipfile.ZipFile(out).read("word/document.xml").decode("utf-8")
        for fill in ("1F8A7A", "C6E0B4", "DCEFEA", "8FBFB8"):
            # table header rows may be teal; paragraph/run shading (titles) must not be
            import re
            bad = re.findall(r"<w:(?:pPr|rPr)>(?:(?!</w:pPr>|</w:rPr>).)*?<w:shd [^>]*w:fill=\"%s\"" % fill, xml)
            assert not bad, (tpl.template_name, fill)
        hdr = [zipfile.ZipFile(out).read(n).decode("utf-8") for n in zipfile.ZipFile(out).namelist() if n.startswith("word/header")]
        assert not any("1F8A7A" in h for h in hdr)


def test_emphasis_dots_and_key_words_render(tmp_path):
    """L40: **x** = bold, {k|..} = red + bold; no 강조점 dots."""
    from app.markup import runs

    assert [(t, c) for t, c, _ in runs("가 {e|나} {k|다} **라**")][:4] == [("가 ", None), ("나", "dots"), (" ", None), ("다", "key")]
    t = Topic(heading="양안시", chapter="정상 시각 발달", slide_numbers=[1], style="explain", basics=["x"], sections={"body": [
        Statement(text="시사 수술은 **8세까지** {k|최대 효과}를 내고 {e|가소성}이 남습니다.", kind="para", slide_refs=[1])]})
    note = LectureNote(title="t", topics=[t], ref_style="para", meta={"points": "a"})
    doc = Document(str(export_mom(note, _tpl(), tmp_path / "e.docx")))
    xml = "".join(p._p.xml for p in doc.paragraphs)
    assert '<w:em ' not in xml and "C00000" in xml  # no dots above letters


def test_rhythm_and_key_ration_checks():
    from app.write.mom_format import emphasis_issues, rhythm_issues

    long_s = "이 문장은 사실을 하나가 아니라 둘 이상 한꺼번에 담아서 예순 글자를 넘기도록 일부러 길게 늘여 쓴 문장이며 읽기가 무겁습니다."
    sts = [Statement(text=long_s, kind="para", slide_refs=[1]) for _ in range(12)]
    n = LectureNote(title="t", topics=[Topic(heading="h", slide_numbers=[1], sections={"body": sts})])
    assert [c for _, c, _ in rhythm_issues(n)] == ["SENTENCE_TOO_LONG"]
    many = Statement(text=" ".join("{k|단어%d}" % i for i in range(9)), kind="para", slide_refs=[1])
    n2 = LectureNote(title="t", topics=[Topic(heading="h", slide_numbers=[1], sections={"body": [many]})])
    assert [c for _, c, _ in emphasis_issues(n2)] == ["KEY_EMPHASIS_TOO_MANY"]


def test_table_only_for_comparison_and_marked_inside():
    """L41: '구분 | 내용' lists are not tables; L42: comparison tables mark their contrasts."""
    from app.write.mom_format import table_issues

    listing = Statement(text="", kind="rows", rows=[["유형", "a"], ["가해자", "b"]], col_titles=["구분", "내용"], slide_refs=[1])
    compare = Statement(text="", kind="rows", rows=[["경과", "줄어듦", "안 줄어듦"]], col_titles=["구분", "정상 애도", "우울장애"], slide_refs=[1])
    marked = Statement(text="", kind="rows", rows=[["경과", "**줄어듦**", "{k|안 줄어듦}"]], col_titles=["구분", "정상 애도", "우울장애"], slide_refs=[1])

    def codes(st):
        return [c for _, c, _ in table_issues(LectureNote(title="t", topics=[Topic(heading="h", slide_numbers=[1], sections={"body": [st]})]))]

    assert codes(listing) == ["TABLE_NOT_COMPARISON"]
    assert codes(compare) == ["TABLE_NO_EMPHASIS"]
    assert codes(marked) == []


def test_section_order_follows_script():
    from app.write.mom_format import order_issues

    def t(h, r):
        return Topic(heading=h, slide_numbers=[r], sections={"body": [Statement(text="x", kind="para", slide_refs=[r])]})

    assert order_issues(LectureNote(title="t", topics=[t("a", 1), t("b", 5), t("c", 9)])) == []
    assert [c for _, c, _ in order_issues(LectureNote(title="t", topics=[t("a", 1), t("b", 30), t("c", 20)]))] == ["SECTION_ORDER"]


def test_one_sentence_hook_checks_and_render(tmp_path):
    """L50: a confusable pair gets ONE short sentence in a [한 줄 구분] box."""
    from app.write.mom_format import hook_issues

    pair = Statement(text="", kind="rows", rows=[["수준", "**한 개체**", "**집단**"]], col_titles=["구분", "polygeny", "polymorphism"], slide_refs=[1, 1001])
    good = Statement(text="", kind="callout", left_title="한 줄 구분", left=["polygeny는 한 사람의 유전자 개수, polymorphism은 집단의 버전 수입니다."], slide_refs=[1])
    long = Statement(text="", kind="callout", left_title="한 줄 구분", left=["첫 문장입니다. 두 번째 문장입니다."], slide_refs=[1])

    def codes(*sts):
        return [c for _, c, _ in hook_issues(LectureNote(title="t", topics=[Topic(heading="h", slide_numbers=[1], sections={"body": list(sts)})]))]

    assert codes(pair) == ["PAIR_NO_HOOK"]
    assert codes(pair, good) == []
    assert codes(pair, long) == ["HOOK_TOO_LONG"]
    assert codes(pair, good, good) == ["HOOK_TOO_MANY"]
    t = Topic(heading="h", chapter="c", slide_numbers=[1], style="explain", basics=["x"], sections={"body": [good]})
    doc = Document(str(export_mom(LectureNote(title="t", topics=[t], ref_style="para", meta={"points": "a"}), _tpl(), tmp_path / "h.docx")))
    assert "[한 줄 구분]" in "\n".join(c.text for tb in doc.tables for r in tb.rows for c in r.cells)

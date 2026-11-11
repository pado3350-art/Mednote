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

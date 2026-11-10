"""compare-mom: the measurements of the MOM-closeness loop (page fill, ink, ending style) and the pure assessment."""
import json
import shutil

import pytest
from PIL import Image, ImageDraw

from app import mom_compare as mc


def _pdf(path, blocks):
    """One A4-ish page per entry: a black block that reaches `blocks[i]` of the page height."""
    pages = []
    for frac in blocks:
        im = Image.new("RGB", (400, 560), "white")
        ImageDraw.Draw(im).rectangle((40, 60, 360, int(560 * frac)), fill="black")
        pages.append(im)
    pages[0].save(path, save_all=True, append_images=pages[1:])
    return path


def test_ending_kind():
    assert mc.ending_kind("외래는 경구가 기본이다.") == "한다체(-다)"
    assert mc.ending_kind("정맥염이 잘 생길 수 있음") == "개조식(-함/-음)"
    assert mc.ending_kind("순응도를 향상시킴") == "개조식(-함/-음)"
    assert mc.ending_kind("소리가 작아 설명이 짧았습니다.") == "합니다체"
    assert mc.ending_kind("BBB 통과 약제 사용") == "명사·어간 종결"
    assert mc.ending_kind("ceftriaxone + vancomycin") == "영문·숫자 종결"


def test_cell_lines_and_note_shape(tmp_path):
    note = {"topics": [
        {"role": "body", "heading": "짧은 제목", "chapter": "장", "basics_refs": [], "sections": {"body": [
            {"kind": "rows", "rows": [["라벨", "{b|파랑 줄}\n외래는 경구가 기본이다"], ["라벨2", "사용 가능"]]},
            {"kind": "check", "slide_refs": [1]}]}},
        {"role": "body", "heading": "기출 소절", "chapter": "장", "basics_refs": [], "sections": {"body": [
            {"kind": "para", "slide_refs": [1001]}, {"kind": "check", "slide_refs": [1]}]}},
        {"role": "body", "heading": "QUIZ", "chapter": "장", "sections": {"body": []}}]}
    f = tmp_path / "note.json"
    f.write_text(json.dumps(note, ensure_ascii=False), encoding="utf-8")
    assert mc.cell_lines(f) == ["파랑 줄", "외래는 경구가 기본이다", "사용 가능"]  # label column and markup removed
    shape = mc.note_shape(f)
    assert shape["checks"] == 2 and shape["checks_without_pad"] == 1 and shape["max_heading"] == len("기출 소절")


def test_assess_lists_only_what_differs():
    mom = {"pages": 11, "chars_per_page": 600, "glyph_pt": 12.0, "half_empty": [], "max_ink": 11.0, "inks": [11.0]}
    same = {"pages": 12, "chars_per_page": 620, "glyph_pt": 12.5, "half_empty": [], "max_ink": 12.0, "inks": [12.0]}
    assert mc.assess(mom, same, cells=["사용 가능"], shape={"max_heading": 20, "max_chapter": 20, "checks_without_pad": 0}) == []
    bad = {"pages": 14, "chars_per_page": 900, "glyph_pt": 10.0, "half_empty": [5], "max_ink": 17.0, "inks": [8.0, 17.0]}
    got = " | ".join(mc.assess(mom, bad, cells=["외래는 경구가 기본이다."],
                              shape={"max_heading": 60, "max_chapter": 40, "checks_without_pad": 2}))
    for part in ("쪽수 14쪽", "쪽당 글자 900자", "글자 크기 10.0pt", "[5]", "2쪽 잉크 17.0%", "‘-다’ 문장", "제목 길이", "개념 Check(L20)"):
        assert part in got, part
    empty = dict(same, chars_per_page=300)
    assert "쪽이 비었다" in " ".join(mc.assess(mom, empty))


@pytest.mark.skipif(not shutil.which("pdftoppm"), reason="poppler-utils needed")
def test_page_metrics_fill_and_cli(tmp_path, capsys):
    pdf = _pdf(tmp_path / "ours.pdf", [0.9, 0.35, 0.8])
    m = mc.page_metrics(pdf)
    assert [round(p["fill"], 1) for p in m] == [0.9, 0.4, 0.8] or abs(m[1]["fill"] - 0.35) < 0.08  # content end, top margin skipped
    assert m[0]["ink"] > m[1]["ink"] > 0
    s = mc.summarize(m, {"chars": 0, "glyph_pt": 0.0})
    assert s["pages"] == 3 and s["half_empty"] == [2]  # the last page may be short, the middle one is half empty
    mom = _pdf(tmp_path / "mom.pdf", [0.9, 0.9])
    from app.cli import main

    out = tmp_path / "report.md"
    assert main(["compare-mom", str(mom), str(pdf), "--out", str(out)]) == 0
    text = out.read_text(encoding="utf-8")
    assert "MOM 근접도 측정" in text and "절반 이하로 빈 쪽" in text and "[2]" in text


def test_abx_figs_side_by_side(tmp_path):
    """examples/abx_figs.py: the two curve slides are placed side by side on one white canvas (f34)."""
    from examples.abx_figs import PICKS, side_by_side

    a, b = tmp_path / "a.png", tmp_path / "b.png"
    Image.new("RGB", (460, 470), (255, 0, 0)).save(a)
    Image.new("RGB", (460, 400), (0, 0, 255)).save(b)
    out = side_by_side(a, b, tmp_path / "f34.png")
    im = Image.open(out)
    assert im.size == (460 + 460 + 30, 470)  # width = sum + gap, height = the taller one
    assert im.getpixel((10, 10)) == (255, 0, 0) and im.getpixel((460 + 30 + 10, 10)) == (0, 0, 255) and im.getpixel((460 + 10, 10)) == (255, 255, 255)
    assert set(PICKS) == {"f1_quadrant.png", "f2_static_cidal.png", "f3_time_dep.png", "f4_conc_dep.png", "f5_pkpd_index.png"}


def test_picture_led_mom_skips_density_findings():
    from app.mom_compare import assess

    mom = {"pages": 30, "chars_per_page": 259, "glyph_pt": 9.3, "max_ink": 35.0, "img_per_page": 4.1}
    ours = {"pages": 12, "chars_per_page": 600, "glyph_pt": 13.2, "avg_fill": 0.8, "half_empty": [], "max_ink": 14.0, "inks": [14.0], "img_per_page": 0.6}
    assert assess(mom, ours) == []
    text_mom = {**mom, "img_per_page": 0.3}
    assert any("쪽당 글자" in x for x in assess(text_mom, ours))


def test_prose_style_counts(tmp_path):
    import json

    from app.mom_compare import prose_style

    note = {"topics": [{"sections": {"body": [
        {"kind": "figure", "text": "그림"},
        {"kind": "para", "text": "{r|교수님 강조: 중요하다.} 그럼 왜 그럴까? 이유가 있다."},
        {"kind": "figure", "text": "그림2"}, {"kind": "qa", "text": "질문?"}]}}]}
    f = tmp_path / "n.json"
    f.write_text(json.dumps(note), encoding="utf-8")
    r = prose_style(f)
    assert r["red_marks"] == 1 and r["questions"] == 1 and r["figures_without_text"] == 1

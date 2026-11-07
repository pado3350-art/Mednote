import pytest
from PIL import Image
from pptx import Presentation
from pptx.util import Inches


@pytest.fixture
def sample_pptx(tmp_path):
    img = tmp_path / "pic.png"
    Image.new("RGB", (40, 30), "red").save(img)
    prs = Presentation()
    # 1: title+content
    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text = "Ulcerative colitis 개요"
    tf = s.placeholders[1].text_frame
    tf.text = "대장 점막의 만성 염증성 질환"
    p = tf.add_paragraph(); p.text = "직장에서 시작해 연속적으로 진행"; p.level = 1
    s.notes_slide.notes_text_frame.text = "발표자 노트: 젊은 성인에서 호발"
    # 2: table
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.shapes.title.text = "Mayo endoscopic subscore"
    tbl = s.shapes.add_table(3, 2, Inches(1), Inches(2), Inches(6), Inches(2)).table
    for r, row in enumerate([["Score", "소견"], ["2", "뚜렷한 발적, 점막 취약성"], ["3", "자발 출혈, 궤양"]]):
        for c, v in enumerate(row):
            tbl.cell(r, c).text = v
    # 3: image + numbers
    s = prs.slides.add_slide(prs.slide_layouts[5])
    s.shapes.title.text = "Mesalamine 용량"
    s.shapes.add_picture(str(img), Inches(1), Inches(3))
    tb = s.shapes.add_textbox(Inches(1), Inches(1.5), Inches(6), Inches(1))
    tb.text_frame.text = "Mesalamine 4.8 g/day 이상 고용량 사용 가능, 반응 평가는 8주 후"
    p = tmp_path / "lec.pptx"
    prs.save(p)
    return p


MARKED = """[슬라이드 1]
[00:10] 궤양성 대장염은 직장에서 시작합니다.

[슬라이드 2]
[00:40-01:10] Mayo 2점과 3점의 차이가 중요합니다. 시험에 나옵니다.

[슬라이드 3]
[01:10] 고용량은 4.8 g/day까지 씁니다.
"""

UNMARKED = """궤양성 대장염 은 대장 점막의 만성 염증성 질환이고 직장에서 시작해 연속적으로 진행합니다

Mayo endoscopic subscore 2점은 발적과 점막 취약성, 3점은 자발 출혈과 궤양입니다

mesalamine 용량은 고용량 4.8 g/day 이상도 가능하고 8주 후 반응을 평가합니다
"""


@pytest.fixture
def marked_script(tmp_path):
    p = tmp_path / "marked.txt"; p.write_text(MARKED, encoding="utf-8"); return p


@pytest.fixture
def unmarked_script(tmp_path):
    p = tmp_path / "unmarked.txt"; p.write_text(UNMARKED, encoding="utf-8"); return p

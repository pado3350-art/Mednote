from docx import Document
from PIL import Image

from app.export_mom import export_mom
from app.models import Diagram, Group, LectureNote, Statement, Topic
from app.template import load_template
from app.transcript import lecture_minutes, page_budget


def _note(tmp_path):
    img = tmp_path / "f.png"
    Image.new("RGB", (60, 40), "red").save(img)
    side = Statement(text="그림 설명", kind="figure_side", image=str(img), left_title="상자 제목",
                     left=["- 첫 줄", "- 둘째 줄"], slide_refs=[1])
    cols = Statement(text="비교", kind="columns", slide_refs=[2], diagram=Diagram(kind="compare", groups=[
        Group(title="A", items=["a1"]), Group(title="B", items=["b1"])]))
    topics = [
        Topic(heading="§a", chapter="장1", slide_numbers=[1], sections={"body": [side]}),
        Topic(heading="§b", chapter="장1", slide_numbers=[2], sections={"body": [cols]}),
        Topic(heading="§c", chapter="장2", slide_numbers=[2], sections={"body": [Statement(text="본문", slide_refs=[2])]}),
    ]
    return LectureNote(title="t", topics=topics, ref_style="para")


def test_compact_flow_layout(tmp_path):
    tpl = load_template("templates/mom_compact.yaml")
    assert tpl.format.page_break == "flow" and not tpl.format.basics_box and tpl.format.toc_level == "chapter"
    out = export_mom(_note(tmp_path), tpl, tmp_path / "n.docx")
    doc = Document(str(out))
    assert len(doc.sections) == 2  # cover + ONE body section (no page per § / chapter)
    text = "\n".join(p.text for p in doc.paragraphs)
    assert "§ 1. §a" in text and "§ 2. §b" in text and "2. 장2" in text  # in-body headings + chapter banner
    cells = [c.text for t in doc.tables for r in t.rows for c in r.cells]
    assert any("상자 제목" in c and "첫 줄" in c for c in cells)  # figure_side box
    assert "A" in cells and "B" in cells  # columns box


def test_topic_mode_keeps_page_per_section(tmp_path):
    tpl = load_template("templates/mom.yaml")
    doc = Document(str(export_mom(_note(tmp_path), tpl, tmp_path / "n.docx")))
    assert len(doc.sections) == 4


def test_page_budget():
    script = "[00:00 ~ 10:00] 도입\n가\n[10:00 ~ 30:00] 본론\n나\n[30:00 ~ 60:00] 정리\n다\n"
    assert lecture_minutes(script) == 60
    assert page_budget(60, 6) == 12  # 10 body pages + cover/summary
    assert page_budget(0, 6) == 0

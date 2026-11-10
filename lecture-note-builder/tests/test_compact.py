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
    assert page_budget(60, 6, n_checks=9, n_quiz=2) == 10 + 2 + 2 + 1  # 9 checks -> 2 pages, quiz -> 1 page


def test_explain_template_question_answer_box(tmp_path):
    """Explanatory (textbook) mode: question heading + one-line '핵심 답' box + paragraphs, flow layout."""
    tpl = load_template("templates/mom_explain.yaml")
    assert tpl.format.basics_box and tpl.format.basics_label == "핵심 답" and tpl.format.page_break == "flow"
    assert load_template("templates/mom.yaml").format.basics_label == "기본정석"  # default unchanged
    t = Topic(heading="왜 MSC로는 부족한가?", chapter="장1", slide_numbers=[1], basics_title="핵심 답",
              basics=["분화능이 제한되기 때문이다."],
              sections={"body": [Statement(text="MSC는 multipotent다. 그래서 iPSC로 바꾼다.", slide_refs=[1])]})
    doc = Document(str(export_mom(LectureNote(title="t", topics=[t], ref_style="para"), tpl, tmp_path / "e.docx")))
    cells = " ".join(c.text for tb in doc.tables for r in tb.rows for c in r.cells)
    assert "핵심 답" in cells and "분화능이 제한" in cells and "기본정석" not in cells
    assert "왜 MSC로는 부족한가?" in "\n".join(p.text for p in doc.paragraphs)

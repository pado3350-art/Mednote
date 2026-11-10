"""Top-down authoring: storyline template from prepare, STORYLINE_MISSING / STORYLINE_DRIFT after the build."""
from app.models import LectureNote, Statement, Topic
from app.storyline import skeleton_cues, storyline_issues, storyline_template
from app.transcript import parse_flow_script

SCRIPT = ("[00:00 - 05:00] 도입\n질문1. 항균제는 어떻게 고르나요? 첫 번째는 목적, 두 번째는 장기입니다.\n"
          "[05:00 - 10:00] 본론\n그냥 이야기입니다.\n")


def _topic(h, role="body"):
    return Topic(heading=h, chapter="장", role=role, slide_numbers=[1], sections={"body": [Statement(text="x", slide_refs=[1])]})


def test_template_lists_skeleton_cues_and_inputs():
    _, segs = parse_flow_script(SCRIPT)
    cues = skeleton_cues(segs)
    assert cues and cues[0][0] == 1 and "질문1" in cues[0][1]
    text = storyline_template(segs, title="항균제")
    for part in ("① 강의의 뼈대", "② 한 문장 요지", "⑦ 시험 축", "⑧ 그림 인벤토리", "¶1", "top_down_storyline.md"):
        assert part in text


def test_storyline_missing_and_drift(tmp_path):
    note = LectureNote(title="t", topics=[_topic("요약", "front"), _topic("항균제 선택은 무엇에서 시작하나?"),
                                          _topic("새로 끼워 넣은 소절"), _topic("QUIZ")])
    codes = [c for _, c, _ in storyline_issues(note, tmp_path / "storyline.md")]
    assert codes == ["STORYLINE_MISSING"]
    (tmp_path / "storyline.md").write_text("| 1 | 항균제 선택은 무엇에서 시작하나? | 목적, 장기, 환자 |", encoding="utf-8")
    issues = storyline_issues(note, tmp_path / "storyline.md")
    assert [c for _, c, _ in issues] == ["STORYLINE_DRIFT"] and "새로 끼워 넣은" in issues[0][2]


def test_prepare_writes_storyline_template_and_task_step(tmp_path):
    from app.cli import DEFAULT_TEMPLATE_MOM
    from app.prepare import prepare_brief

    sc = tmp_path / "s.txt"
    sc.write_text(SCRIPT, encoding="utf-8")
    prepare_brief(sc, tmp_path / "o", DEFAULT_TEMPLATE_MOM)
    brief = tmp_path / "o" / "brief"
    assert "① 강의의 뼈대" in (brief / "storyline_template.md").read_text(encoding="utf-8")
    task = (brief / "TASK.md").read_text(encoding="utf-8")
    assert "스토리라인 먼저" in task and task.index("스토리라인 먼저") < task.index("note_authored.json`을")

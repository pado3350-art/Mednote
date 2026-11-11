"""Top-down authoring: storyline template from prepare, STORYLINE_MISSING / STORYLINE_DRIFT after the build."""
from app.models import LectureNote, Statement, Topic
from app.write.storyline import skeleton_cues, storyline_issues, storyline_template
from app.write.transcript import parse_flow_script

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
    from app.write.prepare import prepare_brief

    sc = tmp_path / "s.txt"
    sc.write_text(SCRIPT, encoding="utf-8")
    prepare_brief(sc, tmp_path / "o", DEFAULT_TEMPLATE_MOM)
    brief = tmp_path / "o" / "brief"
    assert "① 강의의 뼈대" in (brief / "storyline_template.md").read_text(encoding="utf-8")
    task = (brief / "TASK.md").read_text(encoding="utf-8")
    assert "스토리라인 먼저" in task and task.index("스토리라인 먼저") < task.index("note_authored.json`을")


def test_vague_headings_are_flagged():
    """'질문1: 무엇을 고를까' says nothing about the lecture; subject + terms make a heading informative."""
    from app.write.storyline import heading_content, heading_issues

    assert heading_content("질문1: 무엇을 고를까") == "" and heading_content("질문2: 어떻게 줄까") == ""
    vague = LectureNote(title="t", topics=[
        Topic(heading="무엇을 고를까", chapter="질문1: 무엇을 고를까", slide_numbers=[1], sections={"body": [Statement(text="x", slide_refs=[1])]})])
    issues = heading_issues(vague)
    assert [c for _, c, _ in issues] == ["HEADING_TOO_VAGUE", "HEADING_TOO_VAGUE"] and "항균제" in issues[0][2]
    good = LectureNote(title="t", topics=[
        Topic(heading="경험적 치료(empiric)는 언제 표적 치료(targeted)로 바뀌나?", chapter="항균제 선택 원칙: 사용 목적, 감염 장기, 환자 맥락",
              slide_numbers=[1], sections={"body": [Statement(text="x", slide_refs=[1])]}),
        Topic(heading="QUIZ", chapter="", slide_numbers=[1], sections={"body": [Statement(text="x", slide_refs=[1])]})])
    assert heading_issues(good) == []


def test_heading_form_and_section_count():
    from app.models import LectureNote, Statement, Topic
    from app.write.storyline import heading_form_issues

    def t(h, ch="장", refs=(1, 2), kind="para"):
        return Topic(heading=h, chapter=ch, slide_numbers=[1], role="body",
                     sections={"body": [Statement(text="x", kind=kind, slide_refs=list(refs))]})

    codes = [c for _, c, _ in heading_form_issues(LectureNote(title="t", topics=[
        t("동공 반사는 어떤 경로로 일어나나?"), t("RAPD를 꼭 확인해야 합니다"), t("동공 반사의 경로"), t("시야 검사", refs=(3,))]))]
    assert codes.count("HEADING_QUESTION") == 1 and codes.count("HEADING_SENTENCE") == 1 and codes.count("THIN_SECTION") == 1
    many = [t(f"소절 {i}의 내용") for i in range(13)]
    codes = [c for _, c, _ in heading_form_issues(LectureNote(title="t", topics=many))]
    assert codes.count("SECTION_TOO_MANY") == 2  # total and per chapter


def test_noun_headings_ending_like_questions_are_not_flagged():
    from app.models import LectureNote, Statement, Topic
    from app.write.storyline import heading_form_issues, heading_issues

    ts = [Topic(heading=h, chapter="시야 결손", slide_numbers=[1], role="body",
                sections={"body": [Statement(text="x", kind="rows", slide_refs=[1, 2])]}) for h in ("시신경의 구조와 평가", "동공 반사", "어디에 있나")]
    note = LectureNote(title="t", topics=ts)
    assert [c for _, c, _ in heading_form_issues(note)] == ["HEADING_QUESTION"]
    assert not [m for _, c, m in heading_issues(note) if c == "HEADING_TOO_VAGUE" and ("동공" in m or "평가" in m)]


def test_long_lecture_widens_section_limits():
    from app.models import LectureNote, Statement, Topic
    from app.write.storyline import heading_form_issues

    def note(n, chapters, **meta):
        ts = [Topic(heading=f"항목 {i}의 정리", chapter=f"장 {i % chapters}", slide_numbers=[i],
                    sections={"body": [Statement(text="x", kind="rows", rows=[["a", "b"]], slide_refs=[i, i + 100])]}) for i in range(n)]
        return LectureNote(title="t", topics=ts, meta=meta)

    assert "SECTION_TOO_MANY" in {c for _, c, _ in heading_form_issues(note(16, 4))}
    assert "SECTION_TOO_MANY" not in {c for _, c, _ in heading_form_issues(note(16, 4, long_lecture="true"))}
    assert "CHAPTER_TOO_MANY" in {c for _, c, _ in heading_form_issues(note(14, 7, long_lecture="true"))}

"""해부 구조를 설명하는 소절에는 그림이 있어야 한다 (anatomy-visual-explainer)."""
from app.models import LectureNote, Statement, Topic
from app.write.anatomy import anatomy_issues


def _note(extra=None, meta=None):
    sts = [Statement(text="편도체(amygdala)는 시상과 해마, 시상하부로 신경 섬유를 보낸다.", kind="para", slide_refs=[1])] + (extra or [])
    return LectureNote(title="t", topics=[Topic(heading="변연계의 연결", slide_numbers=[1], sections={"body": sts})], meta=meta or {})


def test_anatomy_text_without_picture_warns():
    assert [c for _, c, _ in anatomy_issues(_note())] == ["ANATOMY_NO_VISUAL"]


def test_figure_or_diagram_clears_it():
    fig = Statement(text="변연계 구조", kind="figure", image="x.png", slide_refs=[1])
    assert anatomy_issues(_note([fig])) == []


def test_opt_out_and_non_anatomy():
    assert anatomy_issues(_note(meta={"anatomy_text_only": "변연계의 연결"})) == []
    t = Topic(heading="약 선택", slide_numbers=[1], sections={"body": [Statement(text="항생제는 균에 따라 고른다.", kind="para", slide_refs=[1])]})
    assert anatomy_issues(LectureNote(title="t", topics=[t])) == []


def test_fires_per_paragraph_in_any_lecture():
    anat = _note().topics[0]
    other = [Topic(heading=f"약 {i}", slide_numbers=[1], sections={"body": [Statement(text="항생제는 균에 따라 고른다.", kind="para", slide_refs=[1])]}) for i in range(3)]
    issues = anatomy_issues(LectureNote(title="t", topics=[anat, *other]))  # a drug lecture with one anatomy paragraph still fires
    assert len(issues) == 1 and "변연계의 연결" in issues[0][2]
    # the terms must sit in one paragraph: scattered single mentions do not make an anatomy paragraph
    spread = Topic(heading="증상", slide_numbers=[1], sections={"body": [Statement(text=x, kind="para", slide_refs=[1]) for x in ("시상 병변", "해마 위축", "편도체 활성")]})
    assert anatomy_issues(LectureNote(title="t", topics=[spread])) == []

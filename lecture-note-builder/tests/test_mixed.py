"""Mixed style (혼합형) = default (approved rule L10): explain § vs list § conventions."""
from app.mixed import mixed_issues, suggest_style
from app.models import LectureNote, Statement, Topic
from app.template import load_template


def _t(heading, style, body, basics=()):
    return Topic(heading=heading, chapter="장", slide_numbers=[1], style=style, basics=list(basics),
                 sections={"body": body})


def _codes(topics):
    return {c for _, c, _ in mixed_issues(LectureNote(title="t", topics=topics))}


def test_mixed_template_is_default_for_prepare():
    from app.cli import DEFAULT_TEMPLATE_MOM

    tpl = load_template(DEFAULT_TEMPLATE_MOM)
    assert DEFAULT_TEMPLATE_MOM.name == "mom_mixed.yaml"
    assert tpl.format.mixed and tpl.format.basics_label == "핵심 답" and tpl.format.page_break == "flow"
    assert not load_template("templates/mom_compact.yaml").format.mixed


def test_suggest_style():
    assert suggest_style("왜 이런 차이가 생길까? 연골세포는 기질 안에서만 안정적이기 때문이다. 그래서 덩어리로 넣는다.") == "explain"
    assert suggest_style("대조군 12명, MSC군 12명을 1년 관찰했고 9개월째 통증 점수가 p < 0.05였다. 4개 제품이 허가되었다.") == "list"


def test_good_mixed_note_has_no_warnings():
    ex = _t("왜 MSC로는 부족한가?", "explain",
            [Statement(text="MSC는 multipotent다. 그럼 분화능이 제한된다.", kind="para", slide_refs=[1])],
            basics=["분화능이 제한되기 때문이다."])
    ls = _t("RCT 결과", "list", [Statement(text="**통증**: 9개월째에만 유의했다.", kind="bullet", slide_refs=[1]),
                                 Statement(text="즉 절반의 성공이었다.", kind="bullet", slide_refs=[1])])
    assert _codes([ex, ls]) == set()


def test_mixed_checks_flag_problems():
    no_style = _t("무엇", "", [Statement(text="본문", slide_refs=[1])])
    listy = _t("기전 설명", "explain", [Statement(text=f"줄 {i}", kind="bullet", slide_refs=[1]) for i in range(3)])
    no_sum = _t("결과", "list", [Statement(text="**통증**: 유의", kind="bullet", slide_refs=[1])])
    codes = _codes([no_style, listy, no_sum])
    assert {"MIXED_STYLE_MISSING", "EXPLAIN_NO_ANSWER", "EXPLAIN_TOO_LISTY", "EXPLAIN_HEADING_NOT_QUESTION",
            "LIST_NO_SUMMARY"} <= codes
    one = _codes([_t("a?", "explain", [Statement(text="x", kind="para", slide_refs=[1])], ["y"])] * 2)
    assert "MIXED_ONE_STYLE" in one


def test_summary_line_may_start_with_markup():
    ls = _t("결과", "list", [Statement(text="{r|즉 핵심은 안전성이다}", kind="bullet", slide_refs=[1])])
    assert "LIST_NO_SUMMARY" not in _codes([ls, _t("왜?", "explain", [Statement(text="p", kind="para", slide_refs=[1])], ["a"])])


def test_prepare_writes_style_plan(tmp_path):
    from app.prepare import prepare_brief

    sc = tmp_path / "s.txt"
    sc.write_text("[00:00 ~ 10:00] 도입\n왜 이렇게 될까? 기질이 없기 때문이다. 그래서 덩어리로 넣는다.\n"
                  "[10:00 ~ 20:00] 결과\n대조군 12명, 투여군 12명, 9개월째 p < 0.05, 4개 제품 허가.\n", encoding="utf-8")
    from app.cli import DEFAULT_TEMPLATE_MOM

    prepare_brief(sc, tmp_path / "o", DEFAULT_TEMPLATE_MOM)
    plan = (tmp_path / "o" / "brief" / "style_plan.md").read_text(encoding="utf-8")
    assert "| explain |" in plan and "| list |" in plan
    assert "style_plan.md" in (tmp_path / "o" / "brief" / "TASK.md").read_text(encoding="utf-8")

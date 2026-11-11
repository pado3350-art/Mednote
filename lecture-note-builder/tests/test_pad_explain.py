import json

from app.models import LectureNote, Statement, Topic
from app.pad.exam import ExamItem
from app.pad.explain import evidence, load_authored, pad_commentary, write_pad_commentary


def _item(n, signals=()):
    return ExamItem(number=n, cohort="20학번", year=2022, professor="한", course="약리", q_no=n - 1000, question="Q? ① a ② b",
                    answer="② b", commentary="PAD 해설", signals=list(signals))


def _note():
    st = [Statement(text="{b|b가 맞다}", kind="para", slide_refs=[1001]),
          Statement(text="", kind="rows", rows=[["x", "y"]], slide_refs=[1001]),
          Statement(text="무관", kind="para", slide_refs=[3])]
    return LectureNote(title="t", topics=[Topic(heading="소절", slide_numbers=[1], sections={"body": st}, role="body")])


def test_evidence_and_commentary(tmp_path):
    note = _note()
    ev = evidence(note, 1001)
    assert ("소절", "b가 맞다") in ev and any(t.startswith("표:") for _, t in ev) and not any("무관" in t for _, t in ev)
    md = pad_commentary([_item(1001), _item(1002), _item(1003, ["미수업"])], note, {1001: {"explanation": "직접 쓴 해설"}})
    assert "직접 쓴 해설" in md and "직접 다루지 않았습니다" in md and "미수업" in md and "1/3문항" in md.replace("1/3", "1/3")
    a, b = write_pad_commentary([_item(1001)], note, tmp_path / "x_PAD해설.md")
    assert a.exists() and b.exists()


def test_load_authored(tmp_path):
    f = tmp_path / "p.json"
    f.write_text(json.dumps({"1001": {"answer": "② b"}}), encoding="utf-8")
    assert load_authored(f) == {1001: {"answer": "② b"}} and load_authored(None) == {}


def test_same_type_questions_share_one_commentary():
    from app.pad.explain import group_items

    note = _note()
    items = [_item(1001), _item(1002), _item(1003, ["미수업"])]
    note.topics[0].sections["body"][1].slide_refs = [1001, 1002]  # 1001 and 1002 cite the same table
    note.topics[0].sections["body"][0].slide_refs = [1001, 1002]
    g = group_items(items, note)
    assert [[i.number for i in x] for x in g] == [[1001, 1002], [1003]]
    md = pad_commentary(items, note, {1001: {"explanation": "한 번"}, 1002: {"explanation": "한 번"}})
    assert md.count("한 번\n") == 1 and "2개 유형" in md


def test_old_import_paths_still_work():
    import app.exam
    import app.mom_compare
    import app.pad.exam
    import app.design.mom_compare

    assert app.exam is app.pad.exam and app.mom_compare is app.design.mom_compare

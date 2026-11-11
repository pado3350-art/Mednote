from docx import Document

from app.write.material import extract_docx_material


def test_docx_material_splits_slides_and_drops_footer(tmp_path):
    d = Document()
    for t in ["Chapter 6", "6-1 First slide title", "• point A", "• point B",
              "6-2 Second slide title", "Fig. 6.1 Some figure",
              "본강의자료는 저작권 안내"]:
        d.add_paragraph(t)
    f = tmp_path / "m.docx"
    d.save(f)
    slides = extract_docx_material(f, tmp_path / "img")
    titles = [s.title for s in slides]
    assert any(t.startswith("6-1") for t in titles)
    assert any(t.startswith("6-2") for t in titles)
    text = " ".join(l.text for s in slides for l in s.body)
    assert "저작권" not in text
    assert "point A" in text

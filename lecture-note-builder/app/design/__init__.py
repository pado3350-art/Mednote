"""② 디자인 섹션: 정리글(LectureNote) + 이미지 -> 문서(DOCX/PDF/MD)로 엮는다.

extract_slides / figures   슬라이드 그림 추출, 그림을 본문 문장 옆에 배치
diagrams                   개념 목록을 도식(트리·흐름·4사분면·피라미드·순환)으로 그림
export_mom / export_docx   MOM 양식 렌더링(표·질문 상자·요약 쪽·표지), Markdown
pdf_render                 LibreOffice PDF 변환, 쪽 읽기
mom_compare                사람이 쓴 MOM과 비교(쪽 채움·밀도·문체)
입력은 note.json과 그림뿐이다. 글을 새로 쓰지 않는다(글은 write 섹션).
"""

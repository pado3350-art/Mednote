"""① 쓰기 섹션: 스크립트(+슬라이드 글) -> 전체 내용을 나눠 이해하기 쉬운 정리글(LectureNote)로 쓴다.

transcript / material / align_content   스크립트·슬라이드 읽기와 대응
outline / storyline                     top-down 목차와 흐름(storyline.md)
prepare / generate_notes / offline_organizer   작업 패킷, 정리글 생성(Claude Code가 직접 쓰거나 오프라인 정리)
mixed / validate_notes                  혼합형 문체·구성 검사, 근거(숫자·용어·출처) 검증
feedback / docx_diff                    사용자가 고친 DOCX에서 문체 규칙 학습(승인 후 저장)
출력: note.json(LectureNote). 이미지·레이아웃은 design 섹션, 파랑·기출은 pad 섹션이 맡는다.
"""

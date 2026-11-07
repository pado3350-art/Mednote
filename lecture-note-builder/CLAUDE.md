# lecture-note-builder

의과대학 강의 PPTX(+스크립트/음성) → 상세 강의록(DOCX/MD) 자동 생성기.

## 원칙
- 슬라이드 내용은 절대 생략하지 않는다(요약기가 아니라 상세 강의록 생성기).
- PPT 문장 / 교수 구두 설명을 항상 구분 저장(`Statement.origin`)하고 출처(슬라이드 번호, 음성 시각)를 보존한다.
- 서식은 코드(`export_docx.py`)와 YAML 템플릿이 결정한다. AI는 구조화 JSON(`Topic`)만 만든다.
- 이미지·표는 코드가 원본을 붙인다. 모델이 생성하지 않는다.
- 교수 발언이 지침과 달라 보여도 조용히 고치지 않고 `review_flags`로 남긴다.
- 정렬 신뢰도가 낮은 구간은 숨기지 않고 리포트에 노출한다.

## 구조
`app/extract_slides → transcript → align_content → generate_notes → validate_notes → export_docx`,
`pipeline.py`가 단계별 JSON을 `outputs/`에 저장(부분 재생성용). 템플릿: `templates/*.yaml`.

## 명령
- 테스트: `python -m pytest`
- 실행: `python -m app.cli build inputs/x.pptx --script inputs/x.txt --out outputs/x [--backend anthropic]`
- 새 기능은 반드시 `tests/`에 테스트를 추가한다. API 호출은 가짜 클라이언트로 테스트한다.

## 개인정보
환자 사례/비공개 자료는 `--backend anthropic` 사용 시 외부 API로 전송된다. 사용 전 자료 이용 권한을 확인.

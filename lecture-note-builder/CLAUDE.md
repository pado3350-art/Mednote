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

## 색상 규칙 (MOM 양식)
- **파랑 = 기출된 내용에만** (PAD=기출문제 모음에 실제로 나온 내용). 용어 강조 등 다른 용도로 쓰지 않는다. 강조는 굵게(**), 교수 강조/시험 언급은 빨강, 덜 중요한 부분은 회색, 검증 필요는 보라.
- 파랑 글씨 문장은 반드시 PAD 문항(`slide_refs`에 1000 이상 번호 = PAD 유닛)을 인용해야 한다. 검증기가 `BLUE_WITHOUT_PAD`(오류), `PAD_NOT_BLUE`(경고)로 강제한다.
- PAD 해설은 정리본 작성자의 코멘트이지 교수 발언이 아니다. `--exam-pdf`로 입력한다(pdftotext 필요).

## 목차(TOC)
스크립트 단독 입력은 시간 구간 헤더로 쪼개지 않고 전체 흐름으로 읽는다. 목차는 AI(`--backend anthropic`, 기본 `--toc ai`)가 판단하며
`outline.json`으로 저장/수정/재적용(`--outline-json`)한다. 오프라인에서는 휴리스틱 목차를 쓴다.

## 정리 스타일 (readable-note-organizer 스킬)
내용은 빠짐없이 넣되 받아쓰기가 아니라 이해하기 쉽게 재구성한다: § 섹션마다 기본정석 박스(2~4줄) → 설명 순서로 재배열한 본문 → Advice(헷갈리는 점) / Reference(강의에서 안 다룬 PPT 내용) → 비교표.
앞쪽에 핵심 어휘·요약 정리 페이지. 우수 예시와 규칙은 `.claude/skills/readable-note-organizer/`. AI 백엔드는 이 SKILL.md를 시스템 프롬프트에 자동으로 붙인다.
기출문제(PAD)·필수예제 섹션은 만들지 않는다(`exam_section: false`, PAD는 파랑 글씨 근거로만 사용).

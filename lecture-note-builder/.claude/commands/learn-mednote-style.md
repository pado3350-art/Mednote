---
description: 내가 수정한 강의록 DOCX와 AI 원본 DOCX를 비교해 수정 패턴을 뽑고, 내가 승인한 것만 학습 규칙으로 저장
argument-hint: <원본.docx> <수정본.docx>
---
`learn-mednote-style` 스킬을 따른다. 입력: $ARGUMENTS

1. 인자가 비어 있으면 `feedback/originals/`, `feedback/edited/`, `outputs/` 에서 후보를 찾아 어느 두 파일인지 사용자에게 확인한다.
2. `python -m app.cli feedback diff <원본> <수정본> --out feedback/reports` 를 실행하고 리포트(.md)를 읽는다.
3. 분류별 건수와 규칙 후보(규칙 문장 · 근거 건수 · 전/후 예시)를 한국어로 보고한다.
4. **사용자가 승인할 후보와 적용 강의 유형을 고를 때까지 `feedback approve`를 실행하지 않는다.** 의학적 사실 수정은 따로 확인받는다.
5. 승인받은 후보만 `feedback approve`로 저장하고, 저장된 규칙 ID·버전을 알린다.

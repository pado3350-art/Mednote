---
description: API 없이 강의록 만들기 (스크립트 + 기출 PDF + 그림 자료) — Claude Code가 직접 작성
argument-hint: <script> [--exam-pdf PAD.pdf] [--figures handout.pdf ...]
---
`make-lecture-note` 스킬을 따라 강의록을 만든다. 입력: $ARGUMENTS

1. `python -m app.cli prepare ...` 로 작업 패킷을 만든다 (인자가 비어 있으면 `inputs/` 폴더의 스크립트·PAD·그림 PDF를 찾아 사용자에게 확인).
2. `readable-note-organizer` 스킬(⛔ 파랑 = PAD 기출만, 내용 전부 + 이해하기 쉽게)과 `brief/TASK.md`를 읽고 노트 JSON을 작성한다.
3. 빌드 → 검증 오류 0 → PDF 확인 → 그림 배치 보정(`figures.json`) 순으로 마무리하고 결과 파일 경로를 알린다.

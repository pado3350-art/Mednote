---
name: learn-mednote-style
description: Learn from the user's own edits - compare the AI-generated note DOCX with the DOCX the user edited, report what changed (문체/구성/설명 깊이/용어/서식/의학적 사실), and save ONLY the rules the user explicitly approves. Use when the user says they edited a generated note, uploads an edited DOCX, or runs /learn-mednote-style.
---

# Learn Mednote style (feedback learning)

> ## ⛔ 승인 전 적용 금지
> 1. `feedback diff`는 리포트만 만든다. 규칙 후보는 전부 `pending`이고 생성에 쓰이지 않는다.
> 2. **`feedback approve`는 사용자가 이번 대화에서 해당 후보를 명시적으로 승인했을 때만 실행한다.** 추측·일괄 승인·“아마 원할 것” 금지. 승인 범위가 모호하면 묻는다.
> 3. 승인되지 않은 후보를 다음 강의록 작성에 미리 반영하지 않는다. 생성이 따르는 것은 `style_rules/approved_rules.json`의 `approved` 규칙뿐이다.
> 4. **의학적 사실 수정**(수치·부정·용어 교체)은 문체 규칙으로 일반화하지 않는다. 사용자가 승인하면 그 강의의 “사실 정정 기록”으로만 저장되고, 원자료 확인이 필요하다고 알린다.
> 5. 원본·수정본 DOCX와 리포트는 비공개 자료다. `feedback/`(gitignore) 밖으로 복사하거나 커밋하지 않는다.

## 순서
1. **파일 확인**: 원본(AI 생성 DOCX)과 수정본(사용자 편집 DOCX). 없으면 사용자에게 경로를 묻는다. 권장 위치: `feedback/originals/`, `feedback/edited/`.
2. **비교**: `python -m app.cli feedback diff <원본.docx> <수정본.docx> --out feedback/reports`
   → `feedback/reports/feedback_<수정본>.json` + `.md` (문단·제목·표·셀·굵게·색·순서 변경, 6분류, 규칙 후보).
3. **리포트를 읽고 사용자에게 보고**(한국어): 분류별 건수 → 후보별로 규칙 문장, 근거 건수, 전/후 예시 1~2개. 후보 문장은 기계적 초안이므로 예시를 보고 더 정확한 문장을 제안해도 된다(`--rule`). 오탐(정렬 실수, 우연한 변경)은 그렇다고 말한다.
4. **사용자에게 묻는다**: 어느 후보를 승인할지, 각 규칙의 **적용 강의 유형**(`all` 모든 강의 / `concept_chain` 개념·기전 연쇄형 / `list_intro` 나열형·인트로 / `clinical` 임상 강의). 의학적 사실 후보는 따로 확인한다.
5. **승인된 것만 저장**: `python -m app.cli feedback approve <리포트.json> --ids R1 R3 --lecture-type concept_chain [--note "…"] [--rule "다듬은 규칙 문장"]`
   거절은 `python -m app.cli feedback reject <리포트.json> --ids R2`.
6. **결과 보고**: 저장된 규칙 ID·버전, 적용 범위. 확인은 `python -m app.cli feedback rules [--lecture-type …]`, 전체 문서화는 `python -m app.cli feedback export`.

## 저장되는 것
`style_rules/approved_rules.json` — 규칙마다 `id`, `version`, `category`, `rule`, `lecture_types`, `examples`(수정 전/후), `evidence`(리포트, 변경 ID, 건수, 날짜), `history`; 저장소 전체 `store_version`. 같은 패턴을 같은 범위로 다시 승인하면 새 규칙이 아니라 버전이 올라가고 근거가 쌓인다. 잘못된 규칙은 `feedback rules --retire L2 --reason "…"`.

## 어디에 반영되나 (승인 후에만)
- `--backend anthropic`: 스타일 가이드 끝에 승인 규칙이 붙는다 (`app/generate_notes.learned_rules`).
- `/make-lecture-note`: `prepare`가 `brief/learned_rules.md`를 쓰고 TASK.md 0번 단계가 그것을 읽게 한다.
- 직접 작성할 때: `python -m app.cli feedback rules --lecture-type <유형>` 출력을 읽고 따른다.
- 우선순위: 승인 규칙 > `my-writing-style` > `readable-note-organizer`의 말투 표. 단 ⛔ 파랑 = PAD 기출 전용, 내용·수치·출처 보존 규칙은 어떤 학습 규칙으로도 바뀌지 않는다.

## 한계 (사용자에게 숨기지 않는다)
- 분류는 규칙 기반 추정이다(예: 숫자가 바뀌면 의학적 사실로 표시). 한 변경이 여러 분류에 들 수 있다.
- 제목 판별은 스타일·음영·굵게·`★ §` 표식으로 추정한다. 그림·도식 교체, 글자 크기, 표 테두리는 추출하지 않는다.
- 많이 고친 문단은 ‘삭제 + 추가’로 잡힐 수 있다.

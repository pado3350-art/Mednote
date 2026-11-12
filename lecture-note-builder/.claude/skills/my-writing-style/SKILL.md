---
name: my-writing-style
description: Apply the USER'S OWN wording style, learned from sentences the user edited by hand in generated notes. Use whenever writing or revising lecture-note text (readable-note-organizer, make-lecture-note) - read this first, then follow the rules and the before/after pairs. Update it whenever the user pastes or uploads more edits.
---

# My writing style (learned from the user's own edits)

The user rewrites generated sentences by hand. Those edits are the ground truth for voice. **User edits beat every other style rule** (including the voice table in `readable-note-organizer`) when they conflict.

## How to use
0. New edits given as DOCX files go through `/learn-mednote-style` (diff → report → user approval → `style_rules/approved_rules.json`). Approved rules there outrank the rules below. The rules below came from pasted text in an earlier session and stay as they are.
1. Before writing note text, read `references/edits_log.md` (before → after pairs, newest last).
2. Follow the rules below; when a rule and a pair disagree, trust the pair.
3. When the user gives new edits: append the pairs to `references/edits_log.md`, re-derive/adjust the rules here (mark each rule with how many edits support it), and say what changed. Never delete a rule unless an edit contradicts it.
4. Facts, numbers, terms and slide/script citations are NOT style: never drop them while restyling. The user's edit may drop a sentence for brevity - only drop what the edits show they drop (see rule 3).

## Scope
The story/narration rules apply to concept-chain lectures written as prose (`mom.yaml`). In compact notes (`mom_compact.yaml`, list-type lectures) the body is 개조식 bullets; rules 1 (no professor attribution), 4 (plain wording) and 8 (markup unchanged) still apply.

## Techniques adopted from the nucleotide example (user-approved)
Structure/technique rules in `readable-note-organizer` 0b (check boxes, effort tags, author-added parentheses, analogies, mechanism steps) are adopted; the example's voice (합니다체, colloquial, professor attribution) is NOT. Blue stays PAD-only.

## Rules (evidence: edit batch 1 = tcell_v2 §1 도입)
1. **Narrate directly; do not QUOTE the professor.** (Scope narrowed by approved rule L6: “교수님 연구(팀)” to mark the professor’s own research is allowed; “연자” is not used.) Delete "교수님은 ~라고 하셨다 / ~하라고 당부하셨다 / “…”라고 경고하셨다" framing and quoted professor lines. Write the content as the note's own flow. (Source ¶ citations stay in the refs, not in the prose.)
2. **Inclusive, short guiding voice:** "~를 보았다. 그렇다면 그 다음 질문은 …", "~로 넘어가 보자", "~생각해 보자". Not "교수님은 한번 ~ 생각해 보라고 하셨다".
3. **No filler/signposting sentences.** Cut "이야기를 따라가려면 ~ 해 두어야 한다", "여기에 하나가 더 있다", "교수님은 이 두 가지가 출발점이라고 하셨다" when the next sentence already says it.
4. **Plain, concrete wording over literary wording.** "두 겹으로 대비하고 있다" → "2가지 대비책을 둔다". Numbers as digits (2가지), enumerations as ① ② or 1. 2.
5. **End a thought with its consequence in your own words** when it clarifies: "…allele 종류가 아주 다양해서 MHC의 종류를 무한하게 만든다."
6. **Compress definitions into one flowing sentence** (X는 …라는 뜻이고, Y는 …라는 뜻이다. Z는 haplotype이라고 한다.).
8. **Markup stays exactly as before** (user confirmed): keep bold on key terms and conclusions, red/gray/purple marks, ①② numbering and the other existing marks. Restyle the wording only; never add or strip marks.
7. Keep the slide table (슬라이드 원문 ↔ 요점) as is; the user edited prose only.

## Open questions to confirm with the user (do not guess)
- Should Advice boxes (헷갈리는 점) and "공부 팁" stay? (Not visible in the pasted edits; keep them until told otherwise.)
- Exam-cue phrases (“참고만 해라”, “상식 차원”, “시험에 나올 수 있다”): keep them with attribution as the reference MOM notes do, or restate without “교수님”? (raised in outputs/precision/review_vs_MOM.md)

## 2026-11-10 갱신: 어미 = 합니다체 (승인 규칙 L5 v2)
설명 문단, 질문 상자의 `A.` 답, 핵심 답, 작성자 메모는 합니다체로 쓴다. 표 칸은 개조식(L19), 개념 Check·QUIZ의 O/X·보기는 시험 문장(한다체). 위 ‘한다체’ 예시와 충돌하면 이 항목이 우선한다(어미만 바뀌고 나머지 규칙 — 인용 금지 L6, 군더더기 삭제 — 은 그대로). 검증: `TONE_NOT_FORMAL`.

## 2026-11-10 갱신: 교수님 강조는 문장 끝에 (승인 규칙 L6 v2)
‘교수님 강조: A합니다.’처럼 라벨을 앞에 붙이지 않는다. 내용을 먼저 쓰고 끝에 자연스럽게 붙인다: **‘A해야 할 정도라고 강조하셨습니다.’ / ‘A라고 알려 주셨습니다.’** 빨강 표시는 그대로. 그 밖의 사실은 인용 도입 없이 서술한다. 위 규칙 1·2의 ‘교수님은 ~라고 하셨다’ 인용 도입 금지는 유지된다. 검증: `EMPHASIS_LABEL`.

## 강조·문장 리듬 규칙 (L35–L40, 사시 MOM 비교, `docs/style_compare_sasi.md`)
- **L35 강조 층**: 설명 문장 속 핵심 구는 빨강+굵게만, 문장 끝에 ‘강조하셨습니다’를 붙이지 않는다. ‘~라고 강조하셨습니다’는 시험 범위·공부 깊이 안내에만. 제목·정의·치료 원칙은 ★. 문장 전체를 빨갛게 칠하지 않는다.
- **L36 약한 비중**: 넘어가거나 안 나온다고 한 곳은 회색 괄호 한 줄(‘(짧게 설명하고 넘어가셨습니다)’, ‘(PPT, 언급X)’). 스크립트 근거가 있을 때만.
- **L37 표지 공부 깊이**: 작성자 코멘트·`meta.tips`에 ‘어디까지 공부하면 되는지’ 한 문단(근거가 있을 때만).
- **L38 문장 리듬**: 25자 이하 단정 줄 30% 안팎 + 풀어 쓴 설명 문장, 61자 넘는 문장이 30% 넘으면 둘로(`SENTENCE_TOO_LONG`).
- **L39 구어 자리**: 해요체는 환자 입장 제목·괄호 여담·독자 안내(‘기억하세요!’)에만. 본문은 합니다체.
- **L40 단어 강조 2단계**: 맥락상 주요 단어 `**굵게**` → 반드시 알아야 할 단어·개념 `{k|빨강+굵게}`(한 쪽 5개 안팎, 소절당 8개 이하). 글자 위 점은 쓰지 않는다. 파랑은 PAD 전용.

## 표와 줄글 (L41–L44)
- **L41 표는 비교일 때만**: 비교 대상이 분명하고 비교 항목이 모두 중요한 개념일 때만 표. ‘구분 | 내용’ 목록, 절차·채점 순서, 사례 나열은 줄글이나 ‘① **라벨**: 내용’ 줄(`TABLE_NOT_COMPARISON`). L16의 ‘나열형은 표로’를 대신한다.
- **L42 표 안 강조**: 대비되거나 헷갈리는 칸은 `**굵게**`, 반드시 알아야 할 대비는 `{k|빨강+굵게}`(`TABLE_NO_EMPHASIS`).
- **L43 줄글은 writing skill로**: my-writing-style → grammar-checker → style-guide → humanizer. 표에서 풀어낸 내용까지 사실·수치·용어는 하나도 빼지 않는다.
- **L44 순서**: 내용 정리 → 1차 빌드(커버리지·숫자) → humanize → 최종 빌드. 한 번에 하지 않는다(`docs/WORKFLOW.md`).

## 한 줄 구분 hook (L50)
헷갈리기 쉽고 문제로 내기 쉬우며 구분점이 분명한 짝(polygeny vs polymorphism, allogeneic vs xenogeneic, class I vs II 등)은 `[한 줄 구분]` 상자(kind=callout, left_title "한 줄 구분")에 한 문장, 70자 이하로 쓴다. 형식은 ‘A는 ~, B는 ~입니다’. 비교표가 있으면 바로 뒤에 둔다. 기출에서 온 구분점은 파랑과 출처를 붙이고, 스크립트나 기출에 없는 구분점은 만들지 않는다. 검사 `HOOK_TOO_LONG`, `PAIR_NO_HOOK` (`app/write/mom_format.py`).

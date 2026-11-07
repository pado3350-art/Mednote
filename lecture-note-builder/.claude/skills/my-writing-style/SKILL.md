---
name: my-writing-style
description: Apply the USER'S OWN wording style, learned from sentences the user edited by hand in generated notes. Use whenever writing or revising lecture-note text (readable-note-organizer, make-lecture-note) - read this first, then follow the rules and the before/after pairs. Update it whenever the user pastes or uploads more edits.
---

# My writing style (learned from the user's own edits)

The user rewrites generated sentences by hand. Those edits are the ground truth for voice. **User edits beat every other style rule** (including the voice table in `readable-note-organizer`) when they conflict.

## How to use
1. Before writing note text, read `references/edits_log.md` (before → after pairs, newest last).
2. Follow the rules below; when a rule and a pair disagree, trust the pair.
3. When the user gives new edits: append the pairs to `references/edits_log.md`, re-derive/adjust the rules here (mark each rule with how many edits support it), and say what changed. Never delete a rule unless an edit contradicts it.
4. Facts, numbers, terms and slide/script citations are NOT style: never drop them while restyling. The user's edit may drop a sentence for brevity - only drop what the edits show they drop (see rule 3).

## Rules (evidence: edit batch 1 = tcell_v2 §1 도입)
1. **Narrate directly; do not attribute to the professor.** Delete "교수님은 ~라고 하셨다 / ~하라고 당부하셨다 / “…”라고 경고하셨다" framing and quoted professor lines. Write the content as the note's own flow. (Source ¶ citations stay in the refs, not in the prose.)
2. **Inclusive, short guiding voice:** "~를 보았다. 그렇다면 그 다음 질문은 …", "~로 넘어가 보자", "~생각해 보자". Not "교수님은 한번 ~ 생각해 보라고 하셨다".
3. **No filler/signposting sentences.** Cut "이야기를 따라가려면 ~ 해 두어야 한다", "여기에 하나가 더 있다", "교수님은 이 두 가지가 출발점이라고 하셨다" when the next sentence already says it.
4. **Plain, concrete wording over literary wording.** "두 겹으로 대비하고 있다" → "2가지 대비책을 둔다". Numbers as digits (2가지), enumerations as ① ② or 1. 2.
5. **End a thought with its consequence in your own words** when it clarifies: "…allele 종류가 아주 다양해서 MHC의 종류를 무한하게 만든다."
6. **Compress definitions into one flowing sentence** (X는 …라는 뜻이고, Y는 …라는 뜻이다. Z는 haplotype이라고 한다.). Drop bold on those restated terms unless the user kept it. (Unconfirmed - bold treatment was not visible in the pasted edits; ask if it matters.)
7. Keep the slide table (슬라이드 원문 ↔ 요점) as is; the user edited prose only.

## Open questions to confirm with the user (do not guess)
- Should Advice boxes (헷갈리는 점) and "공부 팁" stay? (Not visible in the pasted edits.)
- Are bold/red/gray marks wanted in prose, or only in tables and boxes?

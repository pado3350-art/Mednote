---
name: readable-note-organizer
description: Turn lecture material (script/transcript/slides) into an easy-to-study note in the MOM "excellent example" style - keep ALL content, but reorganize it for understanding instead of transcribing it verbatim. Use whenever generating or revising lecture-note text (Topic statements, 기본정석 boxes, 핵심 어휘, 요약 정리).
---

# Readable Note Organizer

Goal: a student can study from the note alone. **Nothing from the source is dropped, but nothing is copied as dictation either.**
The reference is `references/excellent_example.md` (a high-rated MOM note for the same kind of lecture); imitate its structure and tone.

## 1. Keep everything, change the shape
- Every concept, term, number, unit, drug/gene name, cutoff and example in the source must appear (the validator checks numbers, terms and paragraph coverage).
- Remove only *speech noise*: fillers, "자, 그러면", repetitions, transitions like "다음으로 넘어가겠습니다", meta talk about the time/slide.
- Do not copy spoken sentences one by one. Re-group the points by idea, then re-write them as short study sentences.

## 2. Page skeleton (per § section)
1. **기본정석 box** (`basics`, 2-4 numbered lines): the core of the section in the shortest form, as if it were the answer to "what must I remember?".
2. Body, in the order that *explains* the idea (not necessarily the order spoken): what it is -> why it matters -> how it works -> exceptions / comparisons.
3. **Advice** call-out (`kind: advice`): pitfalls and distinctions to watch ("Class I과 II region의 차이점에 유의할 것!").
4. **Reference** call-out (`kind: reference`): content that is only in the slides/handout and was not explained by the lecturer, or background that helps.
5. A comparison **table** whenever two or more things are contrasted (class I vs II, allo vs super-antigen ...).

Front pages: **핵심 어휘** (one-line definitions of the key terms, easy words first) and **요약 정리** (cheat-sheet per section: bullets with the key words highlighted).

## 3. Writing style (Korean, 설명체)
- Plain study voice: "~하다 / ~이다 / ~해보자 / ~알아두자". Explain with intuition first ("감염원 입장에서 보면 ..."), then the term.
- Korean sentence + established English medical terms inline (한글(English) on first mention).
- Define a term where it first appears, in one clause. Prefer *cause -> result* chains and arrows over long sentences.
- Numbers get meaning: say what the number is for ("6번 염색체", "alloreactive T cell은 전체의 1~10%").
- One idea per bullet; max ~2 lines per bullet.
- Use the lecturer's mnemonics verbatim (e.g. "다리 하나짜리 / 두 개짜리") and mark them as the lecturer's expression.
- Examples and analogies from the lecture stay, with a one-line "왜 이 예시인지".

## 4. Colour / emphasis (inline markup)
- `{r|...}` RED: what the lecturer stressed or said is on the exam ("꼭", "중요", "시험에", "외워").
- `{g|...}` GRAY: low importance / only mentioned briefly / "언급 안 함" remarks.
- `{b|...}` BLUE: **only** content that actually appeared in the PAD (기출문제). Needs a PAD citation (`slide_refs` >= 1000). Never for generic emphasis - use **bold**.
- `{p|...}` PURPLE: uncertain, conflicts with a reference, or needs checking. Never silently "fix" the lecturer; flag it.
- `**bold**` key terms and the thing being defined.

## 5. Traceability
- Every statement keeps `slide_refs` (script paragraph numbers or slide numbers). A merged bullet cites all paragraphs it used.
- Add a `review_flags` entry for transcription doubts or conflicts with standard references.

## 6. Do NOT
- Do not invent medical facts, mechanisms or numbers that are not in the source (clarifying glue words are fine; new claims are not).
- Do not put exam questions (기출 / 필수예제) into the note unless the template asks for an exam section.
- Do not turn the note into a 3-line summary: if in doubt, include the point.

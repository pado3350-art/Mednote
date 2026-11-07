---
name: readable-note-organizer
description: Turn lecture material (script/transcript/slides) into an easy-to-study note in the MOM "excellent example" style - keep ALL content, but reorganize it for understanding instead of transcribing it verbatim. Use whenever generating or revising lecture-note text (Topic statements, 기본정석 boxes, 핵심 어휘, 요약 정리).
---

# Readable Note Organizer

> **먼저 `my-writing-style` 스킬을 읽는다.** 사용자가 직접 고친 문장에서 배운 문체 규칙이며, 아래 말투 표와 충돌하면 그쪽이 우선한다.

> ## ⛔ NON-NEGOTIABLE — BLUE = PAD(기출) ONLY, ALWAYS
> **파란색 글씨는 PAD(파드, 기출문제 모음)에 실제로 기출된 내용에만 쓴다. 예외 없음.**
> 1. If a PAD is provided, **every** point that appears in a PAD question, answer or explanation MUST be blue (`{b|...}`) **and** cite that PAD unit in `slide_refs` (>= 1000).
>    This includes lines in the 기본정석 box (`basics` + `basics_refs`), 핵심 어휘, 요약 정리, tables and call-outs. If the lecture text never covers a PAD point, add it as a blue **Reference** line instead of dropping it.
> 2. Blue is **never** used for anything else (no key-term highlighting, no "important" marking). Use **bold** for terms, red for lecturer emphasis, gray for low importance, purple for "needs checking".
> 3. If no PAD is provided there is **no blue at all** in the note.
> 4. PAD commentary (해설) was written by the handout author - it is not lecturer speech. Say so when it conflicts with the lecture, and flag with purple instead of "fixing" either side.
> 5. Procedure: (a) list every PAD item, (b) find/create the note lines that express its answer and key explanation, (c) colour them blue and cite them, (d) run the validator: `BLUE_WITHOUT_PAD`, `PAD_NOT_BLUE` are errors and `PAD_UNUSED` is a warning - fix all of them before delivering.

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

## 3. Writing style and voice (말투) — Korean, a fellow student talking to juniors
The author is a classmate, not a textbook. Pick the ending by **what the sentence does** (details and quotes: `references/excellent_examples_clinical.md`):

| The sentence ... | ending | example |
|---|---|---|
| states a fact / definition / translates a slide | ~한다 / ~이다 / ~할 수 있다 | "TIMI 점수가 높을수록 … 발생 확률이 높아진다." |
| reports what the lecturer said or stressed | ~하셨다 / ~라고 합니다 / ~라고 하심 | "~해야 한다고 합니다." / "특히 stria terminalis를 강조하셨습니다." |
| advises the reader how to study | ~하시면 됩니다 / ~해두시면 좋습니다 / ~하자 | "이걸 다 외울 필요는 없을 것 같습니다. 다음 쪽이 훨씬 중요합니다." |
| is the author's own opinion / unsure | in parentheses, honest | "(…정확하게는 classical class 2가 아니라고 받아들이는 것이 맞을 것 같습니다.)" |
| encourages | short and light | "화이팅입니다", "푸실 수 있을 거라고 생각합니다!" |

Rules of voice:
- Never present the author's guess as the lecturer's words; never present the lecturer's words as fact without attribution when it matters ("교수님은 ~라고 하셨는데").
- Always tell the reader the **priority**: "제일 중요!", "가볍게 읽어보아도 좋다", "이건 다 외울 필요는 없을 것 같습니다", "→ 결국 시험 정답은 이걸 기반으로 고릅니다."
- Order of explanation: intuition first ("감염원 입장에서 보면 …"), then the term, then the number (with its meaning: "5.1%로 약 3배 높다").
- Korean sentence + established English terms inline (한글(English) on first mention). One idea per bullet, <= ~2 lines.
- Student slang is allowed where the examples use it: 파드(PAD), 탈(기출 문제), 짤(재탕 문제), 작야/재작야(작년/재작년), 애플(PPT·교재). Use sparingly, never in definitions.
- Keep the lecturer's mnemonics verbatim and mark them as the lecturer's ("교수님 표현으로 ‘다리 하나짜리’"); add your own memory frames in the examples' style (ABCDE with **bold initials**, arrows for sequences).
- Light humour at most once per page; warnings are plain and red ("금기!").

## 3b. Cover, study strategy and learning objectives (표지)
The cover is read first and decides how the student studies:
- `meta.comment` : (1) how this note was made, (2) what kind of lecture it was (professor, year, how much was read from slides), (3) cautions ("반드시 PPT를 함께 보시기 바랍니다").
- `meta.tips` (yellow highlight, 2-4 lines): **study strategy** - what to memorise first, what to skim, where the PAD concentrates ("2쪽의 진단 기억하고, 치료는 파란색 위주로 …"). Derive it from the PAD and the lecturer's emphasis, never from guesses.
- `meta.objectives` (학습목표, 3-6 lines, "… 설명할 수 있다."). `Topic.tip` repeats the priority hint at the top of each §.
- Two professors' PADs: dark blue `{b|}` = PAD of the lecturer in charge, sky blue `{c|}` = PAD of another professor (templates with the `exam_other` legend; the validator enforces which is which).

## 3c. Design vocabulary (use the right component)
| need | component |
|---|---|
| slide content in English + explanation in Korean | `kind: row2` rows (left = original/term, right = ● explanation; consecutive rows = one table; `image` shows the slide capture on the left). Use it for glossaries and for "History / ECG / Markers"-type tables. |
| a case + options the lecture asked | `kind: quiz` (stem in `text`, `options`, `answer` with the reason) - boxed, answer below. Only for quizzes that are in the source. |
| 2+ things compared | `compare` diagram or `SlideTable` |
| a path / sequence | `flow` diagram; a classification | `tree` diagram |
| a sub-heading | `kind: star` (template draws ★ or a light-blue band) |
| what to do first | `Topic.tip` (yellow) and the 기본정석 box |
| lecturer's pointer to the exam | red + "→ 결국 시험 정답은 이걸 기반으로 고릅니다." |
| contraindication / warning | red bold + "금기!" |

## 4. Colour / emphasis (inline markup)
- `{r|...}` RED: what the lecturer stressed or said is on the exam ("꼭", "중요", "시험에", "외워").
- `{g|...}` GRAY: low importance / only mentioned briefly / "언급 안 함" remarks.
- `{b|...}` BLUE: **only** content that appeared in the PAD (기출문제) - see the non-negotiable rule at the top. `{c|...}` sky blue = PAD of another professor (only when the template declares it).
- `{y|...}` YELLOW highlight = study tip / must-look (cover strategy, `tip`); `{u|...}` underline = the key phrase of a sentence.
- `{p|...}` PURPLE: uncertain, conflicts with a reference, or needs checking. Never silently "fix" the lecturer; flag it.
- `**bold**` key terms and the thing being defined.

## 5. Traceability
- Every statement keeps `slide_refs` (script paragraph numbers or slide numbers). A merged bullet cites all paragraphs it used.
- Add a `review_flags` entry for transcription doubts or conflicts with standard references.

## 5b. Figures and photos (use them - they raise understanding)
- Use **every** informative picture the user provides (slides, handout PDF, anatomy photos, tables as images). The program extracts them and places each next to the sub-section it explains; you only make sure the text *refers to what the picture shows* ("그림에서 파란 경로는 basolateral ...").
- Look at the images (Read tool) before writing: describe what to notice (labels, arrows, colours) in the explanation or an **Advice** line.
- Give each figure a specific Korean caption through `figures.json` (`caption`) - not just the file name; fix wrong placement with `topic_heading` / `anchor`; `skip` only decorations or text-only slides.
- Pictures of pure bullet-point text (`text_like`) are skipped by default: the text is already in the note.
- Never draw or invent images; never put a figure in a section it does not belong to just to fill space.

## 5c. The 요약 정리 page MUST be visual (schematics + key figures)
A summary made only of bullets is not enough. For every chapter/§ on the **요약 정리** page put a **schematic** (`kind: "diagram"`, drawn by the program, `Diagram` spec) above its bullets, and let the program add the best source figures as thumbnails ("핵심 그림 모아보기").
- `tree`  = concept map: `root` + `groups` (2-5 cards: title + short items). Use for "what are the parts / classes" (MHC class I/II/Ib, septal 4 connections).
- `flow`  = left-to-right path: `groups` (stages) + `arrows` (src, dst, label, both). Use for pathways and sequences (afferent -> amygdala -> efferent; T cell recognition).
- `compare` = comparison cards: `groups` = columns, `row_labels`, items aligned by row. Use for A vs B (polymorphism vs polygeny, amygdala vs nucleus accumbens).
- Items are 1 short phrase each (<= ~30 chars when possible), same markup/colour rules as text: **bold** terms, `{r|}` stress, `{b|}` = PAD only. A diagram with blue items must cite the PAD unit(s) in `slide_refs`.
- Content comes only from the source - a diagram re-draws what the text says, it never adds facts.
- The validator warns `SUMMARY_NO_VISUAL` if the 요약 정리 page has neither a diagram nor a figure. Offline mode auto-draws a concept map; do better by hand.

## 6. Do NOT
- Do not invent medical facts, mechanisms or numbers that are not in the source (clarifying glue words are fine; new claims are not).
- Do not put exam questions (기출 / 필수예제) into the note unless the template asks for an exam section.
- Do not turn the note into a 3-line summary: if in doubt, include the point.

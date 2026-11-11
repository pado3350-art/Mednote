---
name: make-lecture-note
description: Make a lecture note (MOM style, with figures) from a lecture script (+ PAD 기출 PDF + figure sources) WITHOUT any API key - Claude Code itself writes the structured note, the program validates, lays out and places the figures. Use when the user asks for a lecture note / 강의록 and has no Anthropic API key, or says "API 없이".
---

# Make a lecture note without an API

You (Claude Code) do the AI part; the program does extraction, validation, layout, figures. No API key needed.

1. **Prepare** the work packet:
   `python -m app.cli prepare --script <script.docx|txt> [--exam-pdf <PAD.pdf>] [--figures <handout.pdf|slides.pptx|image-folder> ...] --out outputs/<name>`
   -> `outputs/<name>/brief/` (TASK.md, storyline_template.md, paragraphs.md, exam_items.md, figures.md, outline_proposal.json, note_skeleton.json, note_schema.json, build_command.sh).
2. **Read** `.claude/skills/readable-note-organizer/SKILL.md` (⛔ blue = PAD only, all content kept but reorganised) and `brief/TASK.md`, then paragraphs.md / exam_items.md / figures.md. View important images with the Read tool.
3. **Storyline first (top-down)** — before writing ANY note sentence, fill `brief/storyline_template.md` and save it as `outputs/<name>/storyline.md`
   (procedure + worked example: `.claude/skills/readable-note-organizer/references/top_down_storyline.md`, skill section 00):
   ① the lecture's own skeleton (lecturer's questions, "첫째/둘째", Part, slide titles, objectives) — if it exists, it IS the TOC;
   ② one-sentence thesis → ③ one claim per chapter → ④ per §: question, one-line answer, explain/list, ¶ list (every ¶ exactly once)
   → ⑤ bridges → ⑥ repeated axes (first vs second appearance) → ⑦ exam axes (front summary = PAD-type tables + one map only)
   → ⑧ figure inventory (what each figure SAYS, to be written into the text) → ⑨ emphasis / skipped / omitted.
   Check: the one-line answers read in order tell the whole lecture. Only then go on.
4. **Author** `outputs/<name>/note_authored.json` by expanding the storyline (Topic JSON, schema in `brief/note_schema.json`). Easiest: a small Python script like `examples/abx_note.py`.
   - Headings, order, `style` and `basics` (핵심 답) come straight from storyline.md; do not invent new sections while writing.
   - Sentences follow skill section 00b (한 번 읽고 이해되는 문장): topic sentence first, one new fact per sentence, define before use, one gloss per term, no pronoun openers, max one parenthesis, parallel contrasts, numbers with their reference, figures described by content.
   - Front: 요약 정리 (exam-axis tables + one map, schematics required, skill 5c). Cover `meta.json` (`comment`, `tips`, `objectives`, `omitted`) → `--meta-json`.
   - Every statement cites `slide_refs` (¶ numbers; PAD unit numbers >= 1000).
   - After writing: read only the 핵심 답 boxes in order, then only each chapter's first sentence. Both must match storyline.md.
5. **Build**: `bash outputs/<name>/brief/build_command.sh` (figures are placed automatically next to the related text).
6. **Fix** until `validation_report.md` has 0 errors and no BLUE_/PAD_/MARKUP_LEAK findings; look at the PDF pages; correct misplaced figures in `figures.json` (`topic_heading`, `anchor`, `caption`, `skip`) and rebuild with `--figures-json`.
7. Tell the user what is approximate (figure placement, anything flagged purple) and where the files are.

No Claude Code either? `python -m app.cli build --script ... --exam-pdf ... --figures ... --template templates/mom_mixed.yaml` works fully offline (rule-based organiser; good first draft, review blue/figure placement).


## 서술 기법 (모범 예시 반영)
`brief/effort_cues.md`의 노력 단서로 `effort`(필수/이해/참고)를 붙이고, § 마다 `kind: check` 1–2개, 비유·암기 팁은 `origin: "author"`로 쓴다. 자세한 규칙: `readable-note-organizer` 0b절. ⛔ 파랑 = 기출 전용 — 이 기법들은 파랑을 쓰지 않는다.

## 긴 강의(슬라이드 80장 이상 · 발화 25¶ 이상)
`docs/long_lecture.md`를 먼저 읽는다: 장 6개 이하 · 소절 20개 이하(`meta.long_lecture: "true"`), 장 단위로 쓰고 빌드, 같은 틀은 표, 반복되는 축은 한 번만, 목표 쪽수 ≈ 슬라이드/6. 예 `examples/geri_note.py`. 스크립트의 `[슬라이드 n]` 꼬리표는 지우고 문단을 빈 줄로 나눈다.

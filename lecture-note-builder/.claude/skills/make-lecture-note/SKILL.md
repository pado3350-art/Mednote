---
name: make-lecture-note
description: Make a lecture note (MOM style, with figures) from a lecture script (+ PAD 기출 PDF + figure sources) WITHOUT any API key - Claude Code itself writes the structured note, the program validates, lays out and places the figures. Use when the user asks for a lecture note / 강의록 and has no Anthropic API key, or says "API 없이".
---

# Make a lecture note without an API

You (Claude Code) do the AI part; the program does extraction, validation, layout, figures. No API key needed.

1. **Prepare** the work packet:
   `python -m app.cli prepare --script <script.docx|txt> [--exam-pdf <PAD.pdf>] [--figures <handout.pdf|slides.pptx|image-folder> ...] --out outputs/<name>`
   -> `outputs/<name>/brief/` (TASK.md, paragraphs.md, exam_items.md, figures.md, outline_proposal.json, note_skeleton.json, note_schema.json, build_command.sh).
2. **Read** `.claude/skills/readable-note-organizer/SKILL.md` (⛔ blue = PAD only, all content kept but reorganised) and `brief/TASK.md`, then paragraphs.md / exam_items.md / figures.md. View important images with the Read tool.
3. **Author** `outputs/<name>/note_authored.json` (Topic JSON, schema in `brief/note_schema.json`). Easiest: write a small Python script like `examples/limbic_note.py` (helpers `P B STAR ADV REF T`, then `_remap`) and dump `{"topics": [...]}`.
   - Chapters (2-4) -> § sections (2-4 each); every speech paragraph in exactly one section; closing remarks -> `부록 & 검증 참고`.
   - Per §: `basics` (+ `basics_refs`), body in explanatory order, Advice / Reference, comparison tables.
   - Two `role: "front"` topics: 핵심 어휘, 요약 정리 - the 요약 정리 page must contain schematics (`DIA(Diagram(kind=tree|flow|compare ...))`, see skill section 5c); source-figure thumbnails are added automatically.
   - Cover: write `meta.json` (`comment`, `tips` = study strategy in yellow, `objectives` = 학습목표) and build with `--meta-json`; per § add `tip`; slide content as `row2` rows (English | Korean explanation); lecture quizzes as `quiz`. Voice: skill section 3.
   - Every statement cites `slide_refs` (¶ numbers; PAD unit numbers >= 1000).
4. **Build**: `bash outputs/<name>/brief/build_command.sh` (figures are placed automatically next to the related text).
5. **Fix** until `validation_report.md` has 0 errors and no BLUE_/PAD_/MARKUP_LEAK findings; look at the PDF pages; correct misplaced figures in `figures.json` (`topic_heading`, `anchor`, `caption`, `skip`) and rebuild with `--figures-json`.
6. Tell the user what is approximate (figure placement, anything flagged purple) and where the files are.

No Claude Code either? `python -m app.cli build --script ... --exam-pdf ... --figures ... --template templates/mom_mixed.yaml` works fully offline (rule-based organiser; good first draft, review blue/figure placement).


## 서술 기법 (모범 예시 반영)
`brief/effort_cues.md`의 노력 단서로 `effort`(필수/이해/참고)를 붙이고, § 마다 `kind: check` 1–2개, 비유·암기 팁은 `origin: "author"`로 쓴다. 자세한 규칙: `readable-note-organizer` 0b절. ⛔ 파랑 = 기출 전용 — 이 기법들은 파랑을 쓰지 않는다.

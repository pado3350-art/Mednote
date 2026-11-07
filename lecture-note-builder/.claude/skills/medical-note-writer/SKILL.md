---
name: medical-note-writer
description: Create detailed Korean medical lecture notes from extracted slides and aligned lecture transcripts. Use for lecture note generation and template formatting.
---

# Medical Lecture Note Writer

## Inputs
`outputs/<lecture>/slides.json`, `alignment.json`, and `templates/*.yaml`.

## Workflow
1. Read the template (section keys, order, format flags).
2. Go through all slides in order; every slide must land in a `Topic`.
3. Put slide content in `core_concepts` (or a better-fitting medical section); put lecturer additions in `lecturer_additions`; lecturer emphasis in `professor_emphasis`.
4. Every `Statement` carries `origin`, `slide_refs`, `segment_ids`, `time_ranges`.
5. Save `note.json`, then run `python -m app.cli build ...` or `validate_notes.validate` before exporting.

## Content rules
- Do not omit slide concepts to shorten the notes.
- Preserve numbers, units, drug names, cutoffs verbatim; keep established English terms (한글(English)).
- Distinguish slide content from lecturer additions.
- No unsupported medical claims. Ambiguity or conflict with guidelines → `review_flags`, never a silent fix.
- Never generate images/tables; the renderer attaches the originals.

## Validation
Run `python -m pytest` and the validator; resolve every `error` issue (SLIDE_MISSING, NUMBER_LOST, TABLE_LOST, IMAGE_LOST, SEGMENT_LOST, NO_SOURCE).

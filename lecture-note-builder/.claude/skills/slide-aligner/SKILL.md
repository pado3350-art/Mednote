---
name: slide-aligner
description: Match lecture transcript segments to the slides they discuss and report low-confidence matches. Use when aligning scripts or STT output with a PPTX.
---

# Slide Aligner

1. Prefer explicit markers (`[슬라이드 N]`) and timestamps in the script.
2. Otherwise use `app/write/align_content.py` (bigram cosine + monotonic DP; lecture follows slide order).
3. Inspect `alignment.json`: every segment with `low_confidence_segment_ids` must be reviewed by a human or re-aligned using slide-transition times if available.
4. Never force a match; an unsure segment stays flagged. Backtracking to earlier slides is allowed only when the script says so explicitly.

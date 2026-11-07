---
name: lecture-reviewer
description: Review a generated lecture note against its source slides and transcript for omissions, altered numbers, terminology changes, and unsupported additions. Use after note generation.
---

# Lecture Reviewer

1. Run `python -m app.cli build ...`; read `validation_report.md`.
2. Spot-check 3+ slides: compare `slides.json` vs `note.json` line by line.
3. Delegate medical-accuracy review to the `medical-reviewer` subagent. Its findings are *annotations*, not edits to the lecture content.
4. Output: list of fixes applied + list of items left for the human.

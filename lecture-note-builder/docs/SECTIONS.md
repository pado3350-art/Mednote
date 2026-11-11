# 프로그램의 3개 섹션

```
스크립트 ─▶ ① 쓰기 (app/write) ─▶ note.json ─▶ ② 디자인 (app/design) ─▶ 강의록 DOCX/PDF/MD
                                      │
PAD 파일 ─▶ ③ PAD (app/pad) ──────────┘ (파랑 표시·출처)      └─▶ 새 PAD 파일 (문제·정답·이번 강의 기준 해설)
공통: app/models.py, template.py, markup.py, refs.py   실행: app/pipeline.py, app/cli.py
```

| 섹션 | 하는 일 | 모듈 | 산출물 |
|---|---|---|---|
| ① 쓰기 | 스크립트를 나눠 전체 내용을 이해하기 쉬운 정리글로 쓴다(top-down 스토리라인, 혼합형 문체 L1–L24, 근거 검증) | `transcript` `material` `align_content` `outline` `storyline` `prepare` `generate_notes` `offline_organizer` `mixed` `validate_notes` `feedback` `docx_diff` | `note.json`, `storyline.md`, `validation_report.md` |
| ② 디자인 | 정리글 + 이미지를 엮어 문서로 디자인한다(그림 배치, 도식, 표, 요약 쪽, 표지, PDF, 제목 체계 `Ⅰ.`/`[1]` — `docs/design_headings.md`) | `extract_slides` `figures` `diagrams` `export_mom` `export_docx` `pdf_render` `mom_compare` | `*_강의록.docx/.pdf/.md` |
| ③ PAD | PAD 파일로 파랑을 칠하고(문장 ↔ 기출 대응), 새 PAD 파일에 이번 스크립트 기준 해설을 쓴다 | `exam` `pad_match` `explain` | `*_PAD해설.md/.docx` |

경계 규칙
- ①은 글만 쓴다: 이미지·레이아웃을 모른다. ②는 글을 새로 쓰지 않는다: `note.json`과 그림만 읽는다.
- ③ 파랑은 PAD 내용 전용(무조건). 노트 본문에 별도 기출 섹션을 두지 않고, 기출 해설은 **새 PAD 파일**로 따로 나온다.
- 새 PAD 파일의 ‘이번 강의 기준 해설’은 노트에서 그 문항을 근거로 한 문장과 `pad_notes.json`으로 직접 쓴 해설뿐이다. 스크립트에 없으면 ‘직접 다루지 않았습니다’로 적는다.

실행
```bash
python -m app.cli build --script inputs/x_script.txt --template templates/mom_mixed.yaml \
  --note-json outputs/x/note_authored.json --exam-pdf inputs/x_pad.pdf --pad-notes examples/x_pad_notes.json --out outputs/x --name x
```
`--exam-pdf`를 주면 강의록과 함께 `x_PAD해설.md/.docx`가 나온다. 예: `examples/abx_pad_notes.json`.

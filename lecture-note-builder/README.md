# lecture-note-builder

PPTX(+TXT 스크립트) → 출처가 추적되는 상세 강의록(DOCX/Markdown) + 검증 리포트.

```bash
pip install -r requirements.txt
python -m pytest
python -m app.cli build inputs/lecture.pptx --script inputs/lecture.txt --out outputs/lecture
# AI 생성(ANTHROPIC_API_KEY 필요)
python -m app.cli build inputs/lecture.pptx --script inputs/lecture.txt --backend anthropic
```

스크립트 형식(모두 선택): `[슬라이드 12]` 마커, `[23:10]`/`[23:10-24:02]` 타임스탬프, 빈 줄로 문단 구분.
마커가 없으면 문자 bigram 유사도 + 슬라이드 순서 DP로 자동 정렬하며 신뢰도 낮은 구간은 리포트에 표시됩니다.

스크립트만 있을 때(PPTX 없이): 전체 흐름을 읽고 AI가 목차를 만든다.
```bash
# --exam-pdf: 파랑 글씨 = PAD(기출) 내용만, 무조건 (검증기가 강제)
python -m app.cli build --script inputs/lecture.docx --exam-pdf inputs/pad.pdf \
  --template templates/mom.yaml --backend anthropic --out outputs/lecture   # outputs/lecture/outline.json 생성
python -m app.cli build ... --outline-json outputs/lecture/outline.json      # 목차를 고친 뒤 재생성
```

## 예시
| 예시 | 입력 | 노트 작성 코드 | 결과 |
|---|---|---|---|
| T림프구에 대한 항원제시 (면역학) | 스크립트 DOCX + 기출 PAD PDF | `examples/tcell_note.py` | `outputs/tcell/` (파랑 = 기출) |
| Limbic system (신경과학1) | 스크립트 DOCX + 기출 PAD PDF | `examples/limbic_note.py` | `outputs/limbic/` (파랑 = 기출) |

두 스크립트는 구간 헤더 표기가 달라도(`[00:00–02:00] 제목 | 원본 2쪽` / `00:00–02:00 | 제목` + `자료 기준: 3쪽`) 같은 파서가 읽고,
시간 구간 구조는 버린 뒤 전체 흐름으로 목차를 새로 만든다.

설계: [docs/DESIGN.md](docs/DESIGN.md)

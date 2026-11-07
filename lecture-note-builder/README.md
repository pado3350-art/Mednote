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
python -m app.cli build --script inputs/lecture.docx --exam-pdf inputs/pad.pdf \
  --template templates/mom.yaml --backend anthropic --out outputs/lecture   # outputs/lecture/outline.json 생성
python -m app.cli build ... --outline-json outputs/lecture/outline.json      # 목차를 고친 뒤 재생성
```

설계: [docs/DESIGN.md](docs/DESIGN.md)

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

## API 없이 사용
API 키는 **필수가 아니다.** 세 가지 방법이 있다.

| 방법 | 품질 | 방법 |
|---|---|---|
| ① 완전 오프라인 (규칙 기반) | 읽을 만한 1차 초안 | `python -m app.cli build --script x.docx --exam-pdf pad.pdf --figures handout.pdf --template templates/mom.yaml` |
| ② Claude Code가 직접 작성 (API 키 불필요, 권장) | 최고 | Claude Code에서 `/make-lecture-note x.docx --exam-pdf pad.pdf --figures handout.pdf` (내부적으로 `prepare` → 노트 JSON 작성 → `build` → 검증) |
| ③ API (`--backend anthropic`) | 높음 | `ANTHROPIC_API_KEY` 필요 |

①은 군말 제거·한다체 변환·빨강/회색 단서·영어 용어 굵게·기본정석 박스·핵심 어휘/요약 정리를 규칙으로 만들고, PAD와 자동 대조해 파랑을 칠한다(근사치 — 오탐은 `--no-auto-blue`로 끄거나 검토).

## 그림·사진 활용
`--figures` 에 PDF(강의록·슬라이드) · PPTX · 이미지 폴더를 여러 개 줄 수 있다. 그림은 캡션/주변 글과 함께 추출되고(작은 장식·반복 로고 제외, 글자뿐인 슬라이드는 기본 제외),
섹션·위치를 글 유사도와 페이지 순서로 자동 배치해 본문 옆에 `그림 n. 캡션 (출처)`로 넣는다. 결과는 `figures.json` — 고쳐서 `--figures-json`으로 재적용
(`topic_heading`, `anchor`(★ 소제목 일부), `caption`, `skip`). 슬라이드 PDF/PPTX를 입력으로 주면 슬라이드 그림은 해당 슬라이드 설명 옆에 자동으로 들어간다.

## 핵심 요약의 도식·그림
요약 정리 쪽에는 시각 자료가 들어간다.
- **도식(코드가 직접 그림)**: `Diagram`(tree 개념 지도 / flow 경로·순서 / compare 비교 카드)을 PNG로 그려 `도식 n.`으로 삽입. 본문과 같은 색 규칙(빨강 강조, **파랑 = 기출만**, 굵게)을 박스 글에도 적용하며 파랑 박스는 PAD 출처 필수.
- **핵심 그림 썸네일**: 각 섹션의 가장 잘 맞는 원본 그림을 `핵심 그림 모아보기`에 작게 모아 넣는다 (`--summary-figures N`, 0이면 끔).
- 오프라인 모드는 개념 지도를 자동으로 그린다(섹션별 핵심 용어). Claude Code/API 모드는 흐름도·비교 카드까지 직접 설계한다.
- 폰트: 한글 폰트를 자동 탐색(NanumGothic/Noto CJK/맑은 고딕 등), `MEDNOTE_FONT=/path/font.ttf`로 지정 가능.

## 디자인 변형과 구성 요소 (임상 강의 예시 반영)
| 템플릿 | 특징 |
|---|---|
| `templates/mom.yaml` | 큰 색 제목 배너 표지 + 챕터/§ 배너 + 기본정석 박스 (기초 강의 노트) |
| `templates/mom_clinical.yaml` | 이중선 제목 박스, 테두리 코멘트 박스(색 범례·노란 공부 전략), 본문 로마자 제목, 연한 파랑 소제목 띠, 2단 슬라이드 표, QUIZ 박스, **두 가지 파랑**(담당 교수님 파드 = 파랑, 다른 교수님 파드 = 하늘색 `{c|}`; 검증기가 강제) |

구성 요소: 표지 `meta` — `comment`, `tips`(공부 전략, 노란 형광펜), `objectives`(학습목표), `numbering_start`(이전 교시에서 이어지는 목차 번호) / 섹션 `tip`(공부 팁) /
`row2`(왼쪽 슬라이드 원문·용어 ↔ 오른쪽 설명 2단 표) / `quiz`(사례·선지·정답 박스) / 마크업 `{y|형광펜}` `{u|밑줄}` `{c|하늘색}`. 슬라이드(PPTX/PDF)를 입력하고 `mom_clinical`을 쓰면
슬라이드 원문 ↔ 교수님 설명 2단 표가 자동 구성된다. `--meta-json 파일`로 표지 정보를 준다 (오프라인 모드는 비어 있으면 학습목표·공부 전략을 규칙으로 채움).

## 강의자료 DOCX + 스크립트 DOCX
슬라이드를 Word로 옮긴 강의자료(`6-10 제목` / `Chapter 6` 형태의 제목 줄, 그림 포함)도 입력으로 받는다(`app/material.py`): 슬라이드 단위로 쪼개고 그림은 해당 슬라이드·`Fig.` 캡션과 묶는다.
스크립트의 문단(¶)이 슬라이드에 정렬되어 `PPT p.3 · 발화 ¶5–7`처럼 인용된다. 결과 파일 이름은 `--name`으로 정한다.
```bash
python -m app.cli build inputs/material.docx --script inputs/script.docx --template templates/mom.yaml \
  --note-json outputs/x/note_authored.json --figures-json examples/tcell_v2_figures.json --name tcell_v2 --out outputs/tcell_v2
```
PAD를 주지 않으면 파랑 글씨는 0이다.

## 예시
| 예시 | 입력 | 노트 작성 코드 | 결과 |
|---|---|---|---|
| T림프구에 대한 항원제시 (면역학) | 스크립트 DOCX + 기출 PAD PDF + 그림(우수 예시 PDF) | `examples/tcell_note.py` + `examples/tcell_figures.json` | `outputs/tcell/` (파랑 = 기출, 그림 15개) |
| Limbic system (신경과학1) | 스크립트 DOCX + 기출 PAD PDF + 그림(해부 사진·도식 PDF) | `examples/limbic_note.py` + `examples/limbic_figures.json` | `outputs/limbic/` (파랑 = 기출, 그림 12개) |
| T림프구 항원제시 v2 (강의자료 DOCX + 스크립트, PAD 없음) | 강의자료 DOCX + 스크립트 DOCX | `examples/tcell_v2_note.py` (`examples/authoring.py` 헬퍼) | `outputs/tcell_v2/` |

두 스크립트는 구간 헤더 표기가 달라도(`[00:00–02:00] 제목 | 원본 2쪽` / `00:00–02:00 | 제목` + `자료 기준: 3쪽`) 같은 파서가 읽고,
시간 구간 구조는 버린 뒤 전체 흐름으로 목차를 새로 만든다.

설계: [docs/DESIGN.md](docs/DESIGN.md)

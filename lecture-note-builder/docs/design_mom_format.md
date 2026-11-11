# ② 디자인 섹션 규칙: 정리본 「사시」의 형식 (L27–L34)

근거: 사람이 쓴 정리본 「사시」(2025-11-24, 감각기, 박신혜 교수님, 11쪽, 비공개)와 첨부된 분석. 제목 체계(L27–L29)는 `docs/design_headings.md`, 여기는 나머지 형식(L30–L34).

| 규칙 | 정리본에서 본 것 | 프로그램 |
|---|---|---|
| L30 고정 구성 | 표지(날짜·교시·과목·교수님) → 작성자 코멘트(난이도 총평, 공부 팁, 응원) → 목차 → **[강조점 세가지]** → 본문 → **Ⅲ. Take home messages** | `meta.points`(표지 상자, 굵은 줄 + `- ` 하위 줄), `Topic.role="closing"`(마무리 장, 번호 이어짐, `[n]` 없음) |
| L31 번호 위계 | Ⅰ.(노란) → [1](굵게) → (1) 줄 → ①②③ / 1. / 1-1) | `kind="sub"`: `(1) 라벨 = 핵심★`(굵게, 배경 없음) |
| L32 PPT·스크립트 대조 표기 | `(PPT, 언급X)`, `(아래는 설명X)`, `[ppt에는 없는 여담 - …]`, `[Ppt 내용 추가]` | 슬라이드 글이 있는 강의에서만. 콜아웃 제목으로 사용. 스크립트만 있으면 쓰지 않음 |
| L33 콜아웃 박스 | `[작성자 추가설명]`(일상 비유), `[작성자가 헷갈려서 정리]`, `[잠깐 정리하고 가기]`, `[막간 퀴즈]` | `kind="callout"`(`left_title`, `left`), 퀴즈는 `qa` |
| L34 부호와 말투 | `A = B★`, `→`, 구어체 경어, 교수님 반응을 문장 끝에 | 문장 규칙(L5 v2, L6 v2 유지) |

## 분석 예시와 다르게 둔 것
- **색**: 정리본은 파랑을 용어(Hering's law 등)에도 쓰지만, 이 프로그램은 파랑 = 기출(PAD) 전용 규칙(무조건)을 유지한다. 용어 강조는 굵게 + ★.
- **폴더 구조·HTML 렌더링 제안**: 이미 있는 파이프라인(`prepare → 정리글 → build`, DOCX/PDF/MD)을 쓰므로 새로 만들지 않았다. CLAUDE.md는 기존 것에 규칙을 추가했다.
- **그림 자리표시자**(`[IMAGE: … | layout: left-column]`): 그림 배치는 `figures.json`/도식 스펙이 이미 담당한다.
- **작성자 추가설명의 비유**: 작성자의 말임을 상자 제목으로 밝히고, 원문에 없는 사실은 만들지 않는다.

## 사진 비교와 검사·수술 사례

- **유형·자세 비교(4·8쪽)**: 같은 시야의 원본 이미지를 `kind="columns"`의 `diagram.groups`에 비교 순서대로 넣는다. 각 그룹은 `title`, `image`(강의록 빌드 작업 폴더 기준 경로), `items`(관찰 포인트)를 받는다. DOCX/PDF는 줄마다 최대 3개 패널을 동일 너비로 놓고 원본 비율을 보존한다. Markdown에도 순서와 이미지 링크가 남는다.
- **검사·증례(6쪽)**: 한 장과 해석을 `kind="figure_side"`의 `image`·`left`로 묶는다. 수술 전후(10쪽)는 동일 사례의 사진을 `columns`의 `수술 전`, `수술 후`로 표시하고 한 블록에 모은다.
- **표지·요약(1·11쪽)**: `meta.points`에 실제 강조점을 넣고 `Topic.role="closing"`으로 마지막 요약을 둔다. 11쪽은 참고본 분량이다. 렌더링 후 목차 쪽번호, 사진과 캡션, 페이지 경계의 잘림을 확인한다.

```json
{
  "kind": "columns",
  "text": "수술 전후 안구 정렬",
  "slide_refs": [12],
  "diagram": {
    "kind": "compare",
    "groups": [
      {"title": "수술 전", "image": "inputs/before.png", "items": ["수술 전 관찰 소견"]},
      {"title": "수술 후", "image": "inputs/after.png", "items": ["수술 후 관찰 소견"]}
    ]
  }
}
```

## 검사 (`app/write/mom_format.py`)
`POINTS_MISSING`(info), `CLOSING_MISSING`(info), `CALLOUT_TITLE_UNKNOWN`(info), `CALLOUT_EMPTY`, `SUB_LINE_FORMAT`. 요약 장(closing)과 콜아웃은 `UNGROUNDED` 검사에서 제외한다.

## 적용 예
`examples/neuroophth_note.py` + `examples/neuroophth_meta.json`(points): 표지 [강조점 세가지], (1)(2) 줄, [작성자 추가설명], [작성자가 헷갈려서 정리], [막간 퀴즈], [잠깐 정리하고 가기], Ⅳ. Take home messages. 이 강의에는 PPT가 없어 L32 표기는 쓰지 않았다.

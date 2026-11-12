---
name: readable-note-organizer
description: Turn lecture material (script/transcript/slides) into an easy-to-study note in the MOM "excellent example" style - keep ALL content, but reorganize it for understanding instead of transcribing it verbatim. Use whenever generating or revising lecture-note text (Topic statements, 기본정석 boxes, 핵심 어휘, 요약 정리).
---

# Readable Note Organizer

> **작성 순서는 top-down이다(00절): ① `storyline.md`(뼈대 → 요지 → 장 → 소절의 질문과 한 줄 답 → 다리 → 시험 축 → 그림 인벤토리) ② 그다음에 문장(00b절 한 번 읽고 이해되는 문장).**

> **사용자가 승인한 학습 규칙이 최우선**: `python -m app.cli feedback rules --lecture-type <유형>` (또는 `brief/learned_rules.md`). 현재 L1–L18(사람 정리본 비교·사용자 지시로 승인). **L16–L18 레이아웃(0e절)**: 나열형은 표, 강의의 질문 단위 유지, 한 쪽 한 앵커, 장치 줄이기, 10.5pt. **L15 개념 정리는 도식화**(강의자료 그림 우선, 없으면 도형 도식, 0d절). **L10 혼합형이 기본**(0c절), L11 정의 → “그럼” 추론 · L12 기전 사슬 + “따라서 A → B → C” · L13 원리 → 사례 적용·대조 · L14 “**용어**: 정의 + 한 마디”. L1–L9: 한 줄 한 사실 · 표 도입문과 “즉” 정리문 · 인과 다리는 본문 · 연구 서사 방법→결과→의미 · 메모는 합니다체 괄호 · “교수님 연구(팀)” 허용(인용형은 금지, “연자” 금지) · 슬라이드 영문 용어 우선 · 일화·장식 수치는 회색(아주 사소하고 기출 없음은 삭제, `meta.omitted`) · 사례는 “이름(영문): 한 줄” + 회색 부가설명. 검증 `LINE_TOO_DENSE`.

> **먼저 `my-writing-style` 스킬을 읽는다.** 사용자가 직접 고친 문장에서 배운 문체 규칙이며, 아래 말투 표와 충돌하면 그쪽이 우선한다.

> ## ⛔ NON-NEGOTIABLE — BLUE = PAD(기출) ONLY, ALWAYS
> **파란색 글씨는 PAD(파드, 기출문제 모음)에 실제로 기출된 내용에만 쓴다. 예외 없음.**
> 1. If a PAD is provided, **every** point that appears in a PAD question, answer or explanation MUST be blue (`{b|...}`) **and** cite that PAD unit in `slide_refs` (>= 1000).
>    This includes lines in the 기본정석 box (`basics` + `basics_refs`), 핵심 어휘, 요약 정리, tables and call-outs. If the lecture text never covers a PAD point, add it as a blue **Reference** line instead of dropping it.
> 2. Blue is **never** used for anything else (no key-term highlighting, no "important" marking). Use **bold** for terms, red for lecturer emphasis, gray for low importance, purple for "needs checking".
> 3. If no PAD is provided there is **no blue at all** in the note.
> 4. PAD commentary (해설) was written by the handout author - it is not lecturer speech. Say so when it conflicts with the lecture, and flag with purple instead of "fixing" either side.
> 5. Procedure: (a) list every PAD item, (b) find/create the note lines that express its answer and key explanation, (c) colour them blue and cite them, (d) run the validator: `BLUE_WITHOUT_PAD`, `PAD_NOT_BLUE` are errors and `PAD_UNUSED` is a warning - fix all of them before delivering.

Goal: a student can study from the note alone. **Nothing from the source is dropped, but nothing is copied as dictation either.**
The reference is `references/excellent_example.md` (a high-rated MOM note for the same kind of lecture); imitate its structure and tone.

## 00. Top-down: 흐름을 먼저 짜고, 문장은 나중에 (모든 노트에 적용)
**문장을 한 줄도 쓰기 전에 `{out}/storyline.md`를 완성한다.** 노트는 스토리라인을 펼쳐 쓰는 것이다. 절차·양식·예시: `references/top_down_storyline.md`.
1. **강의의 뼈대를 먼저 찾는다.** 교수의 질문(“질문1/질문2”), “첫째/둘째”, Part, 슬라이드 제목, 학습목표 순서. 뼈대는 **순서의 근거**다. 장과 소절은 **강의 내용의 위계**(주제 → 하위 주제)로 나누되, 소절 순서는 스크립트가 흘러간 ¶ 순서를 따른다.
   - **제목은 제목만 읽어도 무슨 강의인지 알아야 한다.** 장·소절 제목에 **대상(예: 항균제, 줄기세포)과 핵심 의학 용어**를 넣는다. ‘질문1: 무엇을 고를까’, ‘어떻게 줄까’처럼 주어와 용어가 없는 제목은 쓰지 않는다. 교수의 ‘질문N’은 본문 첫 문단에서 설명하는 말이다(검증 `HEADING_TOO_VAGUE`).
   - 장 제목 = 주제 + 하위 항목(예: “항균제 선택 원칙: 사용 목적, 감염 장기, 환자 맥락”). 소절 제목 = 대상과 용어가 들어간 질문(예: “경험적 치료(empiric)는 언제 표적 치료(targeted)로 바뀌나?”).
   - 같은 주제가 스크립트에서 흩어져 나오면 한 장으로 모으되, **스크립트 순서를 뒤섞지 않는다.** 순서가 어긋나는 소절은 장 경계를 다시 긋는다(예: 환자 인자 ¶24–27은 정균·살균 ¶22–23 바로 뒤).
2. **한 문장 요지 → 장 요지 → 소절의 질문과 한 줄 답** 순서로 내려간다. 장 요지를 이어 읽으면 강의 요지가, 한 줄 답을 이어 읽으면 강의 줄거리가 되어야 한다.
3. **다리**: 다음 소절의 질문은 앞 소절의 결론에서 나온다. 같은 개념이 다시 나오면 첫 등장과 짝지어 “앞에서 본 X를 이번에는 Y의 눈으로”로 연다.
4. **시험 축과 앞쪽 요약**: 앞쪽 요약 = PAD 유형별 표 + 전체 지도 1장. 모든 주제를 요약에 넣지 않는다(넓고 얕은 요약은 기출을 묻는다).
5. **그림 인벤토리**: 그림마다 담은 사실을 적고, 그림 속 글(약물 목록, 수치, 축의 뜻)을 본문 문장으로 옮긴다.
6. 다 쓴 뒤 **핵심 답만 이어 읽기, 장 첫 문장만 이어 읽기**로 스토리라인과 맞는지 확인한다. 빌드는 storyline.md가 없으면 `STORYLINE_MISSING`, 노트 소절 제목이 스토리라인에 없으면 `STORYLINE_DRIFT`를 띄운다.

## 00b. 한 번 읽고 이해되는 문장
독자가 문장을 **다시 읽지 않고** 이해해야 한다. 문장을 쓴 뒤 아래를 하나씩 확인한다.

**연결해서 쓴다 (설명형 문단).** 문장마다 새 주어로 시작하는 짧은 문장의 나열은 끊겨 읽힌다. 설명형 § 문단은 **시간·인과 연결어(~하면서, ~가 나오면, 그 결과를, 다만, 그래서, 반대로)로 이은 2–4문장의 한 흐름**으로 쓴다. 한 문장은 60–100자까지 허용한다.
- 나쁜 예(끊김): “감수성 검사는 경험적 치료와 동시에 한다. 검체는 치료 전에 채취한 혈액 등이다. 균이 동정되고 감수성이 확인되면 표적 치료로 바꾼다. 검사 결과지는 항균제별 감수성을 보여 준다. …”
- 좋은 예(연결): “경험적 치료를 시작하면서, 치료 전에 채취한 혈액 등의 검체로 감수성 검사를 함께 한다. 이 검사로 균이 동정되고 항균제별 감수성과 MIC가 나오면, 그 결과를 보고 지금 환자에게 가장 알맞은 약으로 바꾸는 것이 표적 치료다. 다만 경험적 치료가 이미 적절하다면 그대로 유지하는 것이 가장 좋고, 바꿀지는 다음 다섯 가지로 판단한다.”
- 적용 범위: **L1(한 줄 한 사실, 45자 이하)은 나열형 § 의 bullet·표 칸에 적용**한다. 설명형 문단에는 적용하지 않는다(사용자 확인 필요 시 `feedback`으로 규칙 범위를 다시 승인받는다).

**영어 병기는 독자를 위한 것만.** 한 문장에 괄호는 하나까지이고, 핵심 용어(기출·PK/PD 지표·약 이름)만 영어를 병기한다. 녹취에 ‘스페시멘(Specimen)’, ‘옵티멀(Optimal)’처럼 붙은 사소한 영어는 노트에 넣지 않고 `meta.omitted_terms`(“specimen|optimal”)에 적는다. **검증 경고(TERM_LOST)를 없애려고 괄호를 끼워 넣지 않는다.**

| 규칙 | 나쁜 예 | 좋은 예 |
|---|---|---|
| 문단 첫 문장이 그 문단의 결론이다 | (사례 셋을 늘어놓고 마지막에 결론) | “면역이 약하면 살균제를 쓴다. 정균제는 증식만 막고 나머지는 면역에 기대기 때문이다.” |
| 한 문장에 새 정보는 둘까지, 셋 이상이면 목록 (문장은 연결어로 이어 한 흐름으로) | “수정 여부는 감염 부위, 원인균, 감수성 패턴, 숙주 인자, 치료 반응을 종합해 정한다.” | “경험적 치료를 바꿀지는 다섯 가지로 본다.” + 목록. “그중 가장 중요한 것은 치료 반응이다.” |
| 정의하기 전에 쓰지 않는다 | 1장에서 “살균제 선택”을 말하고 2장에서 살균제를 정의 | 처음 나오는 곳에서 한 문장으로 정의하거나, 정의가 나오는 소절로 미룬다 |
| 용어는 처음 한 번만 병기, 그다음은 하나로 | “time-dependent killing(시간 의존성 살균)을 하는지, concentration-dependent killing(농도 의존성 살균)을 하는지” | 정의 문장에서 한 번 병기 → 이후 “시간 의존성”만 |
| 주어를 앞에, 지시어 대신 명사 | “이는 그래서 중요하다.” “위의 경우” | “PAE가 있으므로 농도가 MIC 아래로 내려가도 효과가 남는다.” |
| 괄호는 한 문장에 하나까지 | “IND(…)는 임상시험(…)용으로 규제기관(…)에서” | 괄호 내용을 다음 문장으로 뺀다 |
| 대비는 같은 문장 틀로 | “시간 의존성은 오래 유지할수록 좋다. 반면 aminoglycoside 같은 경우는 높게 올리는 게 낫다.” | “시간 의존성은 **오래** 유지할수록 유리하다. 농도 의존성은 **높이** 올릴수록 유리하다.” |
| 수치는 기준과 함께 | “16/24다.” | “투여 간격 24시간 중 16시간이 MIC 위에 있으면 T>MIC는 16/24다.” |
| 그림 설명은 색이 아니라 내용 | “파랑 글씨는 concentration-dependent다.” | “Cmax/MIC를 보는 약은 aminoglycoside와 fluoroquinolone이다.” |
| 길이: 한 문장 50자 안팎, 문단 2–4문장 | 100자가 넘는 문장 | 두 문장으로 나눈다 |

## 0. 먼저 강의 유형을 판단한다 (서술 모드 · 템플릿 · 쪽 예산)

> **기본값은 혼합형 `mom_mixed.yaml`(L10, 0c절).** 아래 표는 강의 전체가 한쪽으로 치우쳤을 때만 쓴다(예: 인트로 강의 전체가 나열형이면 `mom_compact.yaml`).

| 유형 (스크립트 단서) | 템플릿 | 본문 형식 | 쪽 예산 |
|---|---|---|---|
| 개념·기전 연쇄형 (“그래서/그런데/왜”, 원리 설명) | `mom.yaml` | 스토리 문단 + 기본정석 + 공부 팁 | 약 4분당 1쪽 |
| 사례·목록 나열형 (“첫째/또/그다음에”, 제품·DB·기술 나열) | `mom_compact.yaml` | 개조식, `A → B → C` 사슬, `figure_side`, `columns` | 약 6분당 1쪽 |
| 비중 낮은 인트로·교양 (“한두 문제”, “상식 차원”, “참고만”) | `mom_compact.yaml` | 앞쪽 **시험 정리 2–3쪽** + 압축 본문 | 전체 10–12쪽 이하 |

압축형(compact) 규칙 — 실제 MOM 정리본과 비교해서 얻은 것 (`outputs/precision/review_vs_MOM.md`):
1. **2층 구조**: 맨 앞 `요약 정리 · 시험 정리` (front) = 출제 단서가 있는 표(약물–표적 짝 등) + 주제별 핵심 표 1장 + 전체 흐름 도식 1개. “여기까지만 봐도 된다”는 층.
2. **같은 사실은 최대 2번** (시험 정리 1번 + 본문 1번). 핵심 어휘·기본정석·공부 팁은 쓰지 않는다.
3. **쪽 나눔은 앞쪽 뒤에 한 번** (`page_break: flow`), 장은 본문 안 띠로 이어 간다.
4. **그림은 글과 좌우로** (`kind: figure_side`: `image` + `left_title` + `left` 줄). 병렬 항목(데이터베이스 3개, 기술 2개)은 **가로 칸** (`kind: columns`, `diagram.groups` = 칸).
5. **주제로 묶는다**: 정의·배경 성격의 문단은 시간 순서와 달라도 해당 주제 장으로 옮긴다(예: 중간에 나온 정책 발표를 ‘정의’ 장으로).
6. 수업 안내·자료 주의·코스 소개·출석은 작성자 코멘트나 회색 한 줄로.
7. 출제 단서(“참고 수준”, “상식 차원”)는 **소제목 꼬리표**로 붙인다(예: `CAR-T (참고 수준)`).
8. 표를 담은 이미지는 “글자 위주”라고 버리지 말고 **표로 옮기고 원본 이미지도 싣는다**. 그림과 본문의 숫자가 다르면 그림 기준 + 보라 주석.
9. 빌드 후 `PAGE_BUDGET` 경고(템플릿 `minutes_per_page`)가 없을 때까지 줄인다.

## 0b. 모범 예시에서 체득한 서술 기법 (사용자 승인: “서술 기법을 반영해서 업데이트”)
상세: `references/nucleotide_example_techniques.md`. **어미는 합니다체(L5 v2), 교수님 인용 없음. ⛔ 파랑은 기출(PAD) 전용 — 아래 기법 어디에도 파랑을 쓰지 않는다.**
1. **3층**: 급한 사람용 앞쪽(요약 GUIDE + 시험 필수) → 본문 → QUIZ. 표지 코멘트에서 독자를 분기시킨다(“급하면 앞 2쪽만”).
2. **개념 Check**: § 마다 1–2개 (`kind: check`, `answer` “O”/“X”, 첫 항목 `left_title`에 한 줄 요약, `explanations[0]`에 이유). 그 § 본문만으로 풀려야 하고(`CHECK_NOT_GROUNDED`), 정답은 자동으로 § 끝 정답 상자에 찍힌다.
3. **노력 단서 `effort`**: 교수가 외우라/안 외워도 된다/참고만/시험에 나온다고 한 문장에 붙인다(`prepare`의 `brief/effort_cues.md` 참고). 필수 = 빨강 꼬리표, 참고 = 회색. 단서가 없는 문장에는 붙이지 않는다.
4. **작성자 추가분 `origin: "author"`**: 비유·암기 팁·슬라이드 오류 정정만. 회색 괄호로 나온다. 의학적 사실 주장은 작성자 추가로 쓰지 않는다(출처 있는 문장으로).
5. **비유**: 기전·약물마다 1개 이내, 작성자 추가분으로. 비유 뒤에 실제 용어를 꼭 다시 쓴다.
6. **기전 표준형**: 번호 단계 목록 + 마무리 한 줄(무엇이 되었고 무엇이 남았나).
7. **그림 지시 문장**: 그림 옆 문장이 그림 속 위치·색·화살표를 가리킨다. 그림과 본문 숫자가 다르면 그림 기준 + 괄호 정정(`{p|…}`).
8. **개념 정리 박스(`kind: concept`)**: 헷갈리는 용어 대비 1–2개. 기본정석(요약)과 목적이 다르다.
9. **QUIZ 해설**: `quiz.explanations`에 선지별 해설, 정답 선지에 `(정답)`.
10. 이전 교시와의 연결 문장은 `meta`에 이전·다음 교시 정보가 있을 때만.
11. **시험 신호 → 표지 코멘트**: `brief/exam_signals.md`의 집계(문항 수, 연도, 출제예고·강조 안 함)를 사실로만 인용한다(“PAD 해설 기준 올해 강조 없음”). 예상(“~~ 나올 듯”)은 쓰지 않는다. 표지에는 빌드가 자동으로 **기출 이력(PAD 집계)** 한 줄을 넣는다(`meta.exam_history`).
12. **PAD 꼬리표**(`mom_compact`: `pad_tags: true`): 파랑 문장 끝에 `[PAD 2021 Q1]`, 스크립트(발화)에 없고 PAD에만 있는 사실은 `[Only PAD …]`가 자동으로 붙는다. 그 사실은 **스크립트 출처 없이 PAD 번호만** 인용하는 별도 문장으로 분리한다(예: “Ryoncil은 골수 유래 MSC” = Only PAD). ⛔ 파랑은 PAD 내용 자체에만 — 꼬리표는 회색이다.
13. **개념 구분 박스 의무**: 교수가 두 용어를 대비해 강조하거나 PAD 해설이 한쪽을 강조하면(스페로이드 vs 오가노이드) `kind: concept` 박스 1개.
14. **연결 문장**: 표·목록 뒤에 결론으로 이어지는 한 줄(“따라서 각각의 한계 때문에 …”)을 작성자 추가분(`origin: "author"`)으로 쓴다. 사실을 새로 주장하지 않고 위 내용을 잇기만 한다.
15. **수업에서 다루지 않은 기출**(해설에 ‘배우지 않았다’): 기본은 파랑 Reference 한 줄. 사용자가 `--uncovered-pad omit`을 주면 생략해도 경고가 없다.

## 0f. 제목 체계 (L27–L29) — 사람 정리본「사시」에서
장 `Ⅰ.` = 강의의 큰 부분 3–5개, 소절 `[1]` = **짧은 명사구**(장당 6개·전체 12개 이하), 세부 항목은 제목 블록이 아니라 본문 굵은 라벨 줄 `**1. 정상 동공**`. 질문형(‘~나?’)·문장형(‘~다’) 소절 제목 금지 — 교수님이 던진 질문은 qa 상자. 핵심 한 줄은 `basics`에 쓰면 `[n] 제목 : 핵심 한 줄`로 제목 옆에 붙는다. 강조 소절은 `mark: "★"`(정보 꼬리표는 ‘국시 출제’처럼). 상세 `docs/design_headings.md`. 아래 0c의 ‘질문형 제목’은 이 규칙으로 바뀌었다.

## 0g. 정리본 형식 (L30–L34) — 사람 정리본「사시」에서
- **표지**: 작성자 코멘트(난이도 총평, 공부 팁, 응원) → 목차 → `[강조점 세가지]`(`meta.points`: 굵은 줄 = 강조점, `- ` = 하위). **마지막 장**: `Take home messages`(role=closing; `1. 핵심 = 요약★` 줄들).
- **번호**: `Ⅰ.` → `[1]` → `(1) 라벨 = 핵심★`(kind=sub) → `①`/`1.`/`1-1)`.
- **상자**(kind=callout): `[작성자 추가설명]` 어려운 기전을 일상 비유로(‘짝꿍이 되는 점’, 작성자 말임, 원문에 없는 사실 금지), `[작성자가 헷갈려서 정리]` 구분 요약, `[잠깐 정리하고 가기]` 중간 요약, `[막간 퀴즈]`는 qa 상자.
- **PPT가 있을 때만**: 수업에서 넘어간 PPT 내용 `(PPT, 언급X)`/`(아래는 설명X)`, 구두로만 한 말 `[ppt에는 없는 여담 - 소제목]`, 슬라이드 글 보충 `[Ppt 내용 추가]`. 스크립트만 있으면 쓰지 않는다.
- **말투**: 정의·인과는 `=`/`→`, 핵심어 `★`, 구어체 경어(~하네요, ~기억하세요!), 교수님 반응은 문장 끝에. 파랑은 PAD 전용(용어 강조에 쓰지 않는다).

## 0c. 혼합형 = 기본 (L10, `templates/mom_mixed.yaml`) — 사람 MOM 3건에서 배운 서술
분석: `docs/mixed_style_analysis.md`. 적용 예: `examples/stemcell_mixed_note.py`, 비교 `outputs/stemcell_mixed/compare_three_versions.md`.
소절마다 `style`을 정한다(`prepare`의 `brief/style_plan.md`가 ¶별로 제안). 검증: `MIXED_STYLE_MISSING`, `EXPLAIN_NO_ANSWER`, `EXPLAIN_TOO_LISTY`, `LIST_NO_SUMMARY`, `MIXED_ONE_STYLE`.

| `style` | 쓰는 곳 | 모양 |
|---|---|---|
| `explain` | 개념·기전·원리·병리·임상 판단·“왜” | **질문형 제목** + `basics` 한 줄(**핵심 답**) + 짧은 문단 2–4개 |
| `list` | 수치·사례·제품·실험 결과·절차·원인 분류·감별 소견 | 도입문 1줄 → `**라벨**: 내용` bullet / `columns` / 표 → 끝에 **“즉 …” 1줄**. 핵심 답 상자 없음 |

설명형 문단의 기법:
- **L11 정의 → 그럼**: 정의 다음 문장에서 바로 따라 나오는 결론을 끌어낸다. “ESC는 inner cell mass를 배양한 것이다. 그럼 수정란을 써야 하므로 윤리 문제가 생긴다.”
- **L12 기전 사슬**: 원인 → 결과를 문단으로 풀고 “따라서 A → B → C” 한 줄로 묶는다(화살표는 인과에만).
- **L13 원리 → 사례**: 원리를 먼저 세우고 사례마다 원리를 다시 부른다(“~이므로”, “앞의 X와 달리 …, 이는 ~ 때문이다”). 표 앞 읽는 법 안내는 회색 메모(합니다체): “먼저 두 원리를 이해하고, 아래 네 조합에 대입해 보세요.”
- 문장 길이는 개조식과 같게(평균 40자 내외). 늘리는 것은 연결어뿐이다. 연결어는 **스크립트에 있는 인과만** 잇는다.
나열형의 기법:
- **L14** 항목은 “**용어**(한글): 정의”에 쉬운 풀이나 이유 한 마디. 결과·수치 라벨은 굵게(**대상**, **통증**, **1상**).
- 마지막 “즉 …” 다음에 다음 설명형 소절의 질문을 다리 문장으로 둘 수 있다(“그렇다면 무엇을 바꾸면 …?”).
공통: 파랑 = PAD 전용, 합니다체(L5 v2; 요체는 합니다체로 바꾼다), 교수님 인용형 금지(L6), 일화는 회색(L8). 같은 강의에 두 모양이 섞여야 한다 — 한쪽만 쓰면 `MIXED_ONE_STYLE`.

## 0d. 개념은 그림으로 (L15) — 강의자료 그림 우선, 없으면 도식
위계·분류·대비·기전 사슬·순환·단계를 글로만 정리하지 않는다. 순서:
1. **강의자료에 그 내용의 그림이 있으면 그것을 쓴다.** `figure_side`(그림 + “그림에서 볼 것: …” 줄) 또는 `concept`의 `image`. 아직 안 쓴 슬라이드 그림부터 확인한다(`brief/figures.md`, 이미지를 직접 본다).
2. **없거나 일부만 있으면 도식을 그린다**(`diagram`, 프로그램이 PNG로 그림, 캡션 ‘도식 n.’):

| 내용 | `diagram.kind` | 놓는 곳 |
|---|---|---|
| 위계 (totipotent > pluripotent > multipotent) | `pyramid` (위 = 높은 단계, `root` = 축 이름) | `concept` 박스 오른쪽 (`size: side`) |
| 순환 (세포 → 기질 → 세포 돌봄) | `cycle` (`root` = 가운데 글자, 화살표 라벨) | `figure_side` (`size: side`) |
| 인과 사슬, 치료 단계, 임상 단계 | `flow` (화살표 라벨) | 전체 폭 `kind: diagram` |
| 분류 (한 개념 아래 둘 이상) | `tree` | `concept` 박스 오른쪽 |
| 항목 × 속성 대비 | `compare` | 전체 폭 또는 `columns` |

- 도식 칸 글자는 짧게(한 칸 2–3줄, 줄당 15자 안팎). 설명은 옆 글이 한다.
- 도식 안 파랑도 PAD 출처가 있어야 한다(`BLUE_WITHOUT_PAD`). 그림을 지어내지 않는다 — 도식은 강의 내용을 도형으로 옮기는 것만.
- 검증: `CONCEPT_NO_VISUAL`(mom_mixed) — 그림도 도식도 없는 개념 정리 박스.
- 예: `examples/stemcell_mixed_note.py` (분화능 피라미드, ECM 순환, 골관절염 치료 공백 flow, mitochondria 논리 flow, spheroid/organoid tree, 임상 단계 flow + 슬라이드 s02, s08, s11, s12).

## 0e. 레이아웃 v2 (L16–L18) — 사람 MOM처럼 훑어 읽히는 쪽
근거: `outputs/abx/review_vs_MOM.md` 8절(같은 쪽 나란히 비교). 예: `examples/abx_note.py`. 헬퍼 `QA`, `ROWS`, `FIG`.

| 쓰는 곳 | 구성요소 (`kind`) | 규칙 |
|---|---|---|
| 강의가 던진 질문·역질문 | `qa`: 노란 상자(`left_title` = “질문1”, “역질문2”, `text` = 질문) + `left` = “A.” 한두 줄 | 교수·영상의 질문을 그대로 살린다. 질문이 있는 소절은 핵심 답 띠 대신 이것으로 시작(`basics` 생략) |
| 나열형 § (기관별, 환자별, 정의 비교, 지표) | `rows`: `[[라벨, 칸, ...]]`, `col_titles`, `col_widths` | 라벨 칸은 굵게, 칸은 한 줄 + `→ 결론`. 칸 안 줄바꿈 `\n`. bullet 4개 이상이면 표로(`LIST_NOT_TABLE`) |
| 큰 슬라이드 그림 | `figure`(그림 + 캡션) | 쪽 첫머리에 크게. 그림이 담은 사실은 **같은 소절의 표**가 말한다. 그림을 되풀이하는 bullet은 쓰지 않는다. 그림이 중심인 소절은 `new_page=True` |
| 설명형 § 요지 | `basics` = 핵심 답 **한 줄 띠**(`basics_style: band`) | 상자·번호·빨간 줄 없음 |
| 복습 | `check` | 소절 사이가 아니라 **장 끝에 한 상자**(`checks_where: chapter`) |
| 기출 두 유형 | 앞쪽 요약의 `rows` = 본문의 `rows` (같은 객체) | **같은 표를 같은 모양으로 두 번** |

- 한 쪽에 하나의 시각 앵커(큰 그림 또는 표 하나)를 둔다. 작은 도식·상자·썸네일을 한 쪽에 여럿 놓지 않는다.
- 같은 사실은 요약과 본문의 같은 표 두 번까지. 개념 정리 박스, 문단, Check에서 모양을 바꿔 또 쓰지 않는다.
- 장치는 파랑 제목띠 · 질문 상자 · 표 · 그림 · 보라/회색 메모 정도로 줄인다.

**말투·문체 (L19–L21, 사람 MOM 비교 13절)**
- **표 칸은 개조식**: ‘-다’ 문장으로 끝내지 않는다. 명사형(사용, 투여, 고려, 가능)이나 ‘-음/-함/-됨’, ‘~할 수 있음’으로 마친다. 마침표 없이 한 줄에 조건 → 조치(`TABLE_CELL_STYLE`). 예: “외래는 경구가 기본, 그래도 하루 한 번 주사실에서 IV를 맞는 경우가 있음”.
- 설명 문단·`A.` 줄·작성자 메모는 합니다체(L5 v2), 표 칸은 개조식(L19). 표 칸에서 문장을 연결하려고 길게 늘이지 않는다(줄을 나눈다).
- **개념 Check는 기출(PAD)이 있는 소절에만**(`CHECK_NO_PAD`). 기출이 없는 소절에는 두지 않는다.
- **요약 쪽은 그 주제의 슬라이드 그림을 포함**한다(4사분면 요약 = 4사분면 그림 + 표).

**레이아웃 v2.1 — 사람 MOM과의 비교(review 10절)에서 나온 쓰기 규칙** (빌드 검사가 알려 준다)
- **제목은 한 줄**: 장 29자, 소절 44자 이하(`HEADING_TOO_LONG`). 대상과 용어는 넣되 세부 용어는 질문 상자와 표에 맡긴다. 질문은 노란 질문 상자에 있으므로 소절 제목은 짧은 명사구여도 된다.
- **소절 앞머리는 하나**: 질문 상자가 있으면 핵심 답 띠를 쓰지 않고, `A.` 줄은 제목을 되풀이하지 않는다. 교수 강조(빨강)는 한 줄.
- **한 소절에 한 모양**: 같은 사실을 핵심 답 띠, 표, 문단, Check로 되풀이하지 않는다. PAD(파랑) 내용은 표 안에 두고 같은 내용의 파란 문단을 또 쓰지 않는다.
- **문단은 3줄(175자) 이하**(`PARAGRAPH_TOO_LONG`). 영어 풀이는 한 곳에서 한 번만. 회색·빨강 문장은 문단 안이 아니라 별도 줄로(`COLOUR_IN_PARAGRAPH`).
- **핵심 답 띠는 62자 이하**(`BASICS_TOO_LONG`). 한글 줄 끝 1–2글자가 다음 줄에 혼자 남지 않게 한다. 표 칸 줄은 칸 너비에 맞게 `\n`으로 나눈다(`TABLE_ORPHAN`).
- **개념 Check는 장당 2개 이하**(`CHECK_TOO_MANY`). 장 끝 상자에 `[§n]`으로 소절이 표시된다.
- 소절은 새 쪽으로 시작하지 않는다(장 시작만 새 쪽). 표 앞 도입 문장은 표와 같은 쪽에 붙는다.

## 1. Keep everything, change the shape
- Every concept, term, number, unit, drug/gene name, cutoff and example in the source must appear (the validator checks numbers, terms and paragraph coverage).
- Remove only *speech noise*: fillers, "자, 그러면", repetitions, transitions like "다음으로 넘어가겠습니다", meta talk about the time/slide.
- Do not copy spoken sentences one by one. Re-group the points by idea, then re-write them as short study sentences.

## 2. Page skeleton (per § section)
1. **기본정석 box** (`basics`, 2-4 numbered lines): the core of the section in the shortest form, as if it were the answer to "what must I remember?".
2. Body, in the order that *explains* the idea (not necessarily the order spoken): what it is -> why it matters -> how it works -> exceptions / comparisons.
3. **Advice** call-out (`kind: advice`): pitfalls and distinctions to watch ("Class I과 II region의 차이점에 유의할 것!").
4. **Reference** call-out (`kind: reference`): content that is only in the slides/handout and was not explained by the lecturer, or background that helps.
5. A comparison **table** whenever two or more things are contrasted (class I vs II, allo vs super-antigen ...).

Front pages: **핵심 어휘** (one-line definitions of the key terms, easy words first) and **요약 정리** (cheat-sheet per section: bullets with the key words highlighted).

## 3. Writing style and voice (말투) — Korean, a fellow student talking to juniors
The author is a classmate, not a textbook. Pick the ending by **what the sentence does** (details and quotes: `references/excellent_examples_clinical.md`):

| The sentence ... | ending | example |
|---|---|---|
| states a fact / definition / translates a slide | ~한다 / ~이다 / ~할 수 있다 | "TIMI 점수가 높을수록 … 발생 확률이 높아진다." |
| reports what the lecturer stressed or said is on the exam (L6 v2) | the sentence first, then **~라고 강조하셨습니다 / ~라고 알려 주셨습니다** at its end, in red | "편도체와 공포의 연결은 졸업 뒤에도 기억해야 할 정도라고 강조하셨습니다." (NOT "교수님 강조: 편도체와 공포의 연결은 …합니다.") |
| advises the reader how to study | ~하시면 됩니다 / ~해두시면 좋습니다 / ~하자 | "이걸 다 외울 필요는 없을 것 같습니다. 다음 쪽이 훨씬 중요합니다." |
| is the author's own opinion / unsure | in parentheses, honest | "(…정확하게는 classical class 2가 아니라고 받아들이는 것이 맞을 것 같습니다.)" |
| encourages | short and light | "화이팅입니다", "푸실 수 있을 거라고 생각합니다!" |

Rules of voice:
- **No label in front.** Never write "교수님 강조: …" / "교수님 말씀: …"; say the content, then close the sentence with the attribution (검증 `EMPHASIS_LABEL`). Other facts are narrated directly, without "교수님은 ~라고 하셨다" openers.
- Never present the author's guess as the lecturer's words; never present the lecturer's words as fact without attribution when it matters ("교수님은 ~라고 하셨는데").
- Always tell the reader the **priority**: "제일 중요!", "가볍게 읽어보아도 좋다", "이건 다 외울 필요는 없을 것 같습니다", "→ 결국 시험 정답은 이걸 기반으로 고릅니다."
- Order of explanation: intuition first ("감염원 입장에서 보면 …"), then the term, then the number (with its meaning: "5.1%로 약 3배 높다").
- Korean sentence + established English terms inline (한글(English) on first mention). One idea per bullet, <= ~2 lines.
- Student slang is allowed where the examples use it: 파드(PAD), 탈(기출 문제), 짤(재탕 문제), 작야/재작야(작년/재작년), 애플(PPT·교재). Use sparingly, never in definitions.
- Keep the lecturer's mnemonics verbatim and mark them as the lecturer's ("교수님 표현으로 ‘다리 하나짜리’"); add your own memory frames in the examples' style (ABCDE with **bold initials**, arrows for sequences).
- Light humour at most once per page; warnings are plain and red ("금기!").

## 3b. Cover, study strategy and learning objectives (표지)
The cover is read first and decides how the student studies:
- `meta.comment` : (1) how this note was made, (2) what kind of lecture it was (professor, year, how much was read from slides), (3) cautions ("반드시 PPT를 함께 보시기 바랍니다").
- `meta.tips` (yellow highlight, 2-4 lines): **study strategy** - what to memorise first, what to skim, where the PAD concentrates ("2쪽의 진단 기억하고, 치료는 파란색 위주로 …"). Derive it from the PAD and the lecturer's emphasis, never from guesses.
- `meta.objectives` (학습목표, 3-6 lines, "… 설명할 수 있다."). `Topic.tip` repeats the priority hint at the top of each §.
- Two professors' PADs: dark blue `{b|}` = PAD of the lecturer in charge, sky blue `{c|}` = PAD of another professor (templates with the `exam_other` legend; the validator enforces which is which).

## 3c. Design vocabulary (use the right component)
| need | component |
|---|---|
| slide content in English + explanation in Korean | `kind: row2` rows (left = original/term, right = ● explanation; consecutive rows = one table; `image` shows the slide capture on the left). Use it for glossaries and for "History / ECG / Markers"-type tables. |
| a case + options the lecture asked | `kind: quiz` (stem in `text`, `options`, `answer` with the reason) - boxed, answer below. Only for quizzes that are in the source. |
| 2+ things compared | `compare` diagram or `SlideTable` |
| a path / sequence | `flow` diagram; a classification | `tree` diagram |
| a sub-heading | `kind: star` (template draws ★ or a light-blue band) |
| what to do first | `Topic.tip` (yellow) and the 기본정석 box |
| lecturer's pointer to the exam | red + "→ 결국 시험 정답은 이걸 기반으로 고릅니다." |
| contraindication / warning | red bold + "금기!" |

## 4. Colour / emphasis (inline markup)
- `{r|...}` RED: what the lecturer stressed or said is on the exam ("꼭", "중요", "시험에", "외워").
- `{g|...}` GRAY: low importance / only mentioned briefly / "언급 안 함" remarks.
- `{b|...}` BLUE: **only** content that appeared in the PAD (기출문제) - see the non-negotiable rule at the top. `{c|...}` sky blue = PAD of another professor (only when the template declares it).
- `{y|...}` YELLOW highlight = study tip / must-look (cover strategy, `tip`); `{u|...}` underline = the key phrase of a sentence.
- `{p|...}` PURPLE: uncertain, conflicts with a reference, or needs checking. Never silently "fix" the lecturer; flag it.
- `**bold**` key terms and the thing being defined.

## 5. Traceability
- Every statement keeps `slide_refs` (script paragraph numbers or slide numbers). A merged bullet cites all paragraphs it used.
- Add a `review_flags` entry for transcription doubts or conflicts with standard references.

## 5b. Figures and photos (use them - they raise understanding)
- Use **every** informative picture the user provides (slides, handout PDF, anatomy photos, tables as images). The program extracts them and places each next to the sub-section it explains; you only make sure the text *refers to what the picture shows* ("그림에서 파란 경로는 basolateral ...").
- Look at the images (Read tool) before writing: describe what to notice (labels, arrows, colours) in the explanation or an **Advice** line.
- Give each figure a specific Korean caption through `figures.json` (`caption`) - not just the file name; fix wrong placement with `topic_heading` / `anchor`; `skip` only decorations or text-only slides.
- Pictures of pure bullet-point text (`text_like`) are skipped by default: the text is already in the note.
- Never draw or invent images; never put a figure in a section it does not belong to just to fill space.

## 5c. The 요약 정리 page MUST be visual (schematics + key figures)
A summary made only of bullets is not enough. For every chapter/§ on the **요약 정리** page put a **schematic** (`kind: "diagram"`, drawn by the program, `Diagram` spec) above its bullets, and let the program add the best source figures as thumbnails ("핵심 그림 모아보기").
- `tree`  = concept map: `root` + `groups` (2-5 cards: title + short items). Use for "what are the parts / classes" (MHC class I/II/Ib, septal 4 connections).
- `flow`  = left-to-right path: `groups` (stages) + `arrows` (src, dst, label, both). Use for pathways and sequences (afferent -> amygdala -> efferent; T cell recognition).
- `compare` = comparison cards: `groups` = columns, `row_labels`, items aligned by row. Use for A vs B (polymorphism vs polygeny, amygdala vs nucleus accumbens).
- Items are 1 short phrase each (<= ~30 chars when possible), same markup/colour rules as text: **bold** terms, `{r|}` stress, `{b|}` = PAD only. A diagram with blue items must cite the PAD unit(s) in `slide_refs`.
- Content comes only from the source - a diagram re-draws what the text says, it never adds facts.
- The validator warns `SUMMARY_NO_VISUAL` if the 요약 정리 page has neither a diagram nor a figure. Offline mode auto-draws a concept map; do better by hand.

## 6. Do NOT
- Do not invent medical facts, mechanisms or numbers that are not in the source (clarifying glue words are fine; new claims are not).
- Do not put exam questions (기출 / 필수예제) into the note unless the template asks for an exam section.
- Do not turn the note into a 3-line summary: if in doubt, include the point.

## 마지막 윤문 3종 (grammar-checker · humanizer · style-guide)
글을 다 쓴 뒤 **빌드 전에** 순서대로 적용한다: ① grammar-checker(맞춤법·띄어쓰기) → ② style-guide(용어·숫자·어조 일관성) → ③ humanizer(번역투·군더더기·`~것입니다` 남발). 이 프로젝트 규칙(합니다체, 표 칸 개조식, 교수님 강조 문장, `=`/`→`/`★`, 가운뎃점은 짝만, 단위 붙여쓰기, 파랑 = PAD)이 3종 지침보다 우선한다. 사실·수치·용어는 바꾸지 않는다. 덮어쓰기 표와 절차: `docs/korean_polish.md`.

## 강조·문장 리듬 규칙 (L35–L40, 사시 MOM 비교, `docs/style_compare_sasi.md`)
- **L35 강조 층**: 설명 문장 속 핵심 구는 빨강+굵게만, 문장 끝에 ‘강조하셨습니다’를 붙이지 않는다. ‘~라고 강조하셨습니다’는 시험 범위·공부 깊이 안내에만. 제목·정의·치료 원칙은 ★. 문장 전체를 빨갛게 칠하지 않는다.
- **L36 약한 비중**: 넘어가거나 안 나온다고 한 곳은 회색 괄호 한 줄(‘(짧게 설명하고 넘어가셨습니다)’, ‘(PPT, 언급X)’). 스크립트 근거가 있을 때만.
- **L37 표지 공부 깊이**: 작성자 코멘트·`meta.tips`에 ‘어디까지 공부하면 되는지’ 한 문단(근거가 있을 때만).
- **L38 문장 리듬**: 25자 이하 단정 줄 30% 안팎 + 풀어 쓴 설명 문장, 61자 넘는 문장이 30% 넘으면 둘로(`SENTENCE_TOO_LONG`).
- **L39 구어 자리**: 해요체는 환자 입장 제목·괄호 여담·독자 안내(‘기억하세요!’)에만. 본문은 합니다체.
- **L40 단어 강조 2단계**: 맥락상 주요 단어 `**굵게**` → 반드시 알아야 할 단어·개념 `{k|빨강+굵게}`(한 쪽 5개 안팎, 소절당 8개 이하). 글자 위 점은 쓰지 않는다. 파랑은 PAD 전용.

## 표와 줄글 (L41–L44)
- **L41 표는 비교일 때만**: 비교 대상이 분명하고 비교 항목이 모두 중요한 개념일 때만 표. ‘구분 | 내용’ 목록, 절차·채점 순서, 사례 나열은 줄글이나 ‘① **라벨**: 내용’ 줄(`TABLE_NOT_COMPARISON`). L16의 ‘나열형은 표로’를 대신한다.
- **L42 표 안 강조**: 대비되거나 헷갈리는 칸은 `**굵게**`, 반드시 알아야 할 대비는 `{k|빨강+굵게}`(`TABLE_NO_EMPHASIS`).
- **L43 줄글은 writing skill로**: my-writing-style → grammar-checker → style-guide → humanizer. 표에서 풀어낸 내용까지 사실·수치·용어는 하나도 빼지 않는다.
- **L44 순서**: 내용 정리 → 1차 빌드(커버리지·숫자) → humanize → 최종 빌드. 한 번에 하지 않는다(`docs/WORKFLOW.md`).

## 한 줄 구분 hook (L50)
헷갈리기 쉽고 문제로 내기 쉬우며 구분점이 분명한 짝(polygeny vs polymorphism, allogeneic vs xenogeneic, class I vs II 등)은 `[한 줄 구분]` 상자(kind=callout, left_title "한 줄 구분")에 한 문장, 70자 이하로 쓴다. 형식은 ‘A는 ~, B는 ~입니다’. 비교표가 있으면 바로 뒤에 둔다. 기출에서 온 구분점은 파랑과 출처를 붙이고, 스크립트나 기출에 없는 구분점은 만들지 않는다. **소절당 1개까지**(`HOOK_TOO_MANY`). 넣을지는 판단한다: (가) 바꿔 쓰기 쉬운 두 개념의 짝(셋 이상 나열·순위·단순 대비는 제외) (나) 시험에 나오기 쉬움(기출, 교수님 강조, ‘구분하라’) (다) 한 기준으로 갈림. 후보가 여럿이면 기출 > 교수님 ‘구분하라’ > 혼동 정도로 하나만 고르고 나머지는 본문·표 강조로. 검사 `HOOK_TOO_LONG`, `HOOK_TOO_MANY`, `PAIR_NO_HOOK` (`app/write/mom_format.py`).

## 공부법 메타 문장 금지 (L51)
노트 본문에는 사실만 쓴다. ‘번호를 외우기보다 원리를 이해합니다’, ‘표를 볼 때는 ~를 먼저 찾습니다’, ‘~라는 사고방식을 익힙니다’ 같은 공부법·읽는 법 지시 문장은 빼고, 그 문장이 말하려던 내용을 바로 서술한다. 공부 깊이·범위 안내는 표지 코멘트(L37)나 회색 작성자 메모(`{g|…}`)로만. 검사 `STUDY_ADVICE`(`app/write/mixed.py`).

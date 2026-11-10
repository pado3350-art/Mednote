---
name: readable-note-organizer
description: Turn lecture material (script/transcript/slides) into an easy-to-study note in the MOM "excellent example" style - keep ALL content, but reorganize it for understanding instead of transcribing it verbatim. Use whenever generating or revising lecture-note text (Topic statements, 기본정석 boxes, 핵심 어휘, 요약 정리).
---

# Readable Note Organizer

> **사용자가 승인한 학습 규칙이 최우선**: `python -m app.cli feedback rules --lecture-type <유형>` (또는 `brief/learned_rules.md`). 현재 L1–L15(사람 정리본 비교·사용자 지시로 승인). **L15 개념 정리는 도식화**(강의자료 그림 우선, 없으면 도형 도식, 0d절). **L10 혼합형이 기본**(0c절), L11 정의 → “그럼” 추론 · L12 기전 사슬 + “따라서 A → B → C” · L13 원리 → 사례 적용·대조 · L14 “**용어**: 정의 + 한 마디”. L1–L9: 한 줄 한 사실 · 표 도입문과 “즉” 정리문 · 인과 다리는 본문 · 연구 서사 방법→결과→의미 · 메모는 합니다체 괄호 · “교수님 연구(팀)” 허용(인용형은 금지, “연자” 금지) · 슬라이드 영문 용어 우선 · 일화·장식 수치는 회색(아주 사소하고 기출 없음은 삭제, `meta.omitted`) · 사례는 “이름(영문): 한 줄” + 회색 부가설명. 검증 `LINE_TOO_DENSE`.

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
상세: `references/nucleotide_example_techniques.md`. **어미는 한다체 유지, 교수님 인용 없음. ⛔ 파랑은 기출(PAD) 전용 — 아래 기법 어디에도 파랑을 쓰지 않는다.**
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
공통: 파랑 = PAD 전용, 한다체(L5; 사람 예시의 합니다·요체는 따르지 않는다), 교수님 인용형 금지(L6), 일화는 회색(L8). 같은 강의에 두 모양이 섞여야 한다 — 한쪽만 쓰면 `MIXED_ONE_STYLE`.

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
| reports what the lecturer said or stressed | ~하셨다 / ~라고 합니다 / ~라고 하심 | "~해야 한다고 합니다." / "특히 stria terminalis를 강조하셨습니다." |
| advises the reader how to study | ~하시면 됩니다 / ~해두시면 좋습니다 / ~하자 | "이걸 다 외울 필요는 없을 것 같습니다. 다음 쪽이 훨씬 중요합니다." |
| is the author's own opinion / unsure | in parentheses, honest | "(…정확하게는 classical class 2가 아니라고 받아들이는 것이 맞을 것 같습니다.)" |
| encourages | short and light | "화이팅입니다", "푸실 수 있을 거라고 생각합니다!" |

Rules of voice:
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

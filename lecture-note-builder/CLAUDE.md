# lecture-note-builder

의과대학 강의 PPTX(+스크립트/음성) → 상세 강의록(DOCX/MD) 자동 생성기.

## 원칙
- 슬라이드 내용은 절대 생략하지 않는다(요약기가 아니라 상세 강의록 생성기).
- PPT 문장 / 교수 구두 설명을 항상 구분 저장(`Statement.origin`)하고 출처(슬라이드 번호, 음성 시각)를 보존한다.
- 서식은 코드(`export_docx.py`)와 YAML 템플릿이 결정한다. AI는 구조화 JSON(`Topic`)만 만든다.
- 이미지·표는 코드가 원본을 붙인다. 모델이 생성하지 않는다.
- 교수 발언이 지침과 달라 보여도 조용히 고치지 않고 `review_flags`로 남긴다.
- 정렬 신뢰도가 낮은 구간은 숨기지 않고 리포트에 노출한다.

## 구조
`app/extract_slides → transcript → align_content → generate_notes → validate_notes → export_docx`,
`pipeline.py`가 단계별 JSON을 `outputs/`에 저장(부분 재생성용). 템플릿: `templates/*.yaml`.

## 명령
- 테스트: `python -m pytest`
- 실행: `python -m app.cli build inputs/x.pptx --script inputs/x.txt --out outputs/x [--backend anthropic]`
- 새 기능은 반드시 `tests/`에 테스트를 추가한다. API 호출은 가짜 클라이언트로 테스트한다.

## 개인정보
환자 사례/비공개 자료는 `--backend anthropic` 사용 시 외부 API로 전송된다. 사용 전 자료 이용 권한을 확인.

## 색상 규칙 (MOM 양식)
- **⛔ 파랑 = 파드(PAD, 기출문제 모음)에 기출된 내용에만, 무조건.** PAD가 주어지면 거기 나온 내용은 빠짐없이 파랑(기본정석 박스·요약 포함), PAD가 없으면 파랑 0. 용어 강조 등 다른 용도로 쓰지 않는다. 스킬 `readable-note-organizer` 최상단에 규칙을 박아두었다. 강조는 굵게(**), 교수 강조/시험 언급은 빨강, 덜 중요한 부분은 회색, 검증 필요는 보라.
- 파랑 글씨 문장은 반드시 PAD 문항(`slide_refs`에 1000 이상 번호 = PAD 유닛)을 인용해야 한다. 검증기가 `BLUE_WITHOUT_PAD`(오류), `PAD_NOT_BLUE`(오류), `PAD_UNUSED`(경고)로 강제한다. 기본정석 박스의 파랑은 `Topic.basics_refs`에 PAD 번호가 있어야 한다.
- PAD 해설은 정리본 작성자의 코멘트이지 교수 발언이 아니다. `--exam-pdf`로 입력한다(pdftotext 필요).

## 목차(TOC)
스크립트 단독 입력은 시간 구간 헤더로 쪼개지 않고 전체 흐름으로 읽는다. 목차는 AI(`--backend anthropic`, 기본 `--toc ai`)가 판단하며
`outline.json`으로 저장/수정/재적용(`--outline-json`)한다. 오프라인에서는 휴리스틱 목차를 쓴다.

## 정리 스타일 (readable-note-organizer 스킬)
내용은 빠짐없이 넣되 받아쓰기가 아니라 이해하기 쉽게 재구성한다: § 섹션마다 기본정석 박스(2~4줄) → 설명 순서로 재배열한 본문 → Advice(헷갈리는 점) / Reference(강의에서 안 다룬 PPT 내용) → 비교표.
앞쪽에 핵심 어휘·요약 정리 페이지. 우수 예시와 규칙은 `.claude/skills/readable-note-organizer/`. AI 백엔드는 이 SKILL.md를 시스템 프롬프트에 자동으로 붙인다.
기출문제(PAD)·필수예제 섹션은 만들지 않는다(`exam_section: false`, PAD는 파랑 글씨 근거로만 사용).

## API 없이 / 그림
- API 키 없이 쓴다: ① 오프라인 규칙 기반 `build` ② Claude Code가 직접 작성하는 `/make-lecture-note` (`prepare` → 노트 JSON → `build`). 스킬 `make-lecture-note` 참고.
- 그림·사진 자료(`--figures` PDF/PPTX/폴더, 슬라이드 입력)는 최대한 활용한다: 본문이 그림이 보여주는 것을 가리키게 쓰고, `figures.json`으로 캡션·위치를 다듬는다. 글자뿐인 슬라이드는 제외, 그림을 만들어 내지 않는다.

## Top-down 작성 (흐름 먼저, 문장은 나중)
노트 문장을 쓰기 전에 `{out}/storyline.md`를 먼저 쓴다: 강의 스스로의 뼈대(교수의 질문, 첫째/둘째, Part — 있으면 그것이 목차) → 한 문장 요지 → 장 요지 → 소절의 질문과 한 줄 답 → 다리 → 반복되는 축 → 시험 축(앞쪽 요약 = PAD 유형 표 + 지도 1장) → 그림 인벤토리. 장·소절 제목에는 대상과 의학 용어를 넣는다(‘질문1: 무엇을 고를까’ 같은 제목 금지 — `HEADING_TOO_VAGUE`). 장은 내용의 위계로, 소절 순서는 스크립트 ¶ 순서로. `prepare`가 `brief/storyline_template.md`(구조 신호·PAD·그림 미리 채움)를 만들고, 빌드는 `STORYLINE_MISSING`/`STORYLINE_DRIFT`/`HEADING_TOO_VAGUE`를 띄운다(`app/storyline.py`). 문장은 스킬 00b절 ‘한 번 읽고 이해되는 문장’. 근거 `outputs/abx/review_vs_MOM.md`, 예시 `references/top_down_storyline.md`.

## 레이아웃 v2 (L16–L18: 표 우선, 강의의 질문 단위, 한 쪽 한 앵커)
`mom_mixed.yaml` 기본: 본문 10.5pt, 핵심 답 한 줄 띠(`basics_style: band`), 개념 Check는 장 끝에 모음(`checks_where: chapter`), 장마다 새 쪽(`chapter_page_break`) + 그림 중심 소절 새 쪽(`Topic.new_page`). 새 문장 종류 `rows`(라벨 | 한 줄 → 결론 표; 작은 표는 한 쪽에 붙음), `qa`(강의의 질문 노란 상자 + A. 한 줄). 나열형은 표로(`LIST_NOT_TABLE`), 큰 슬라이드 그림은 `figure`로 쪽 첫머리에. 근거 `outputs/abx/review_vs_MOM.md` 8절, 예 `examples/abx_note.py`, 스킬 0e. 사소한 녹취 영어는 `meta.omitted_terms`로 뺀다(괄호를 끼워 넣지 않는다). **v2.1**(review 10절): 상자형 표지(`cover_style: box`), 장 29자·소절 44자 제목, 문단 3줄, 핵심 답 62자, 장당 Check 2개, 소절은 새 쪽 없이 이어 붙임(장 시작만 새 쪽). 검사 `HEADING_TOO_LONG`·`PARAGRAPH_TOO_LONG`·`COLOUR_IN_PARAGRAPH`·`BASICS_TOO_LONG`·`TABLE_ORPHAN`·`CHECK_TOO_MANY`. **문체(L19–L21)**: 표 칸은 개조식(명사형, ‘-음/-함’), 개념 Check는 기출이 있는 소절에만, 요약 쪽은 그 주제의 그림 포함(`TABLE_CELL_STYLE`, `CHECK_NO_PAD`). 알려진 한계: 샌드박스 PDF에는 한글 굵은 글꼴이 없어 한글 굵게가 안 보인다(Word 파일은 정상).

## MOM 근접 루프 (스킬 `mom-closeness-loop`, 명령 `/mom-loop`)
사람 MOM과 같은 쪽 단위로 비교하며 반복 개선한다. 측정 `python -m app.cli compare-mom <MOM.pdf> <노트.pdf> --note note.json`(쪽 채움, 쪽당 글자, 글자 크기, 잉크, 표 칸 문체, 제목 길이, 기출 없는 Check → 남은 차이 목록, `app/mom_compare.py`). 절차·점검표·멈춤 조건·재현 방법·함정은 스킬과 `references/loop_findings.md`. MOM 글은 비교 전용(생성엔 이미지만), 승인 없는 규칙은 저장하지 않고, 푸시는 종료 코드로 확인한다.

## 개념 = 그림 (L15)
개념 정리(위계·분류·대비·사슬·순환·단계)는 도식화한다: 강의자료 그림 우선(`figure_side`, `concept.image`), 없으면 프로그램 도식 `diagram`(pyramid/cycle/flow/tree/compare, `size: side`면 글 옆 좁은 그림). `concept`·`figure_side`에 `diagram`을 주면 빌드가 PNG로 그려 넣는다(캡션 ‘도식 n.’). 검증 `CONCEPT_NO_VISUAL`. 스킬 0d.

## 핵심 요약 = 시각 자료 필수
요약 정리 쪽에는 반드시 도식(`kind: diagram`: tree/flow/compare)과 핵심 그림 썸네일을 넣는다(검증 `SUMMARY_NO_VISUAL`). 도식 안 파랑도 PAD 출처가 있어야 한다. 규칙: 스킬 `readable-note-organizer` 5c.

## 디자인·말투 (임상 강의 우수 예시 반영)
표지: 코멘트 + 공부 전략(`meta.tips`) + 학습목표(`meta.objectives`); 섹션: 기본정석 → 공부 팁(`tip`) → 본문(슬라이드 원문은 `row2` 2단 표, 퀴즈는 `quiz`). 템플릿 `mom_clinical.yaml`은 파랑 두 가지(담당 교수님 파드/하늘색 다른 교수님 파드).
말투는 문장 기능별: 사실 ~한다 / 교수님 말 ~라고 합니다·하셨다 / 독자 안내 ~하시면 됩니다·~하자 / 작성자 의견은 괄호. 규칙과 예문: `.claude/skills/readable-note-organizer/` (3절, references/excellent_examples_clinical.md).

## 강의 유형 → 템플릿 (실제 정리본 비교에서 얻은 규칙)
개념 연쇄형은 `mom.yaml`(스토리), 나열형·인트로는 `mom_compact.yaml`(시험 정리 2–3쪽 + 개조식 본문, `figure_side`/`columns`, `page_break: flow`). 같은 사실은 최대 2번, 빌드 후 `PAGE_BUDGET` 경고가 없게. 근거: `outputs/precision/review_vs_MOM.md`.
**기본 = 혼합형 `mom_mixed.yaml` (승인 규칙 L10–L14)**: 개념·기전 소절은 설명형(`Topic.style: explain` — 질문형 제목 + 핵심 답 + 추론 문단: 정의→그럼, 기전 사슬→따라서, 원리→사례), 수치·사례·결과 소절은 나열형(`style: list` — `**라벨**: 내용` + ‘즉 …’). `prepare` 기본 템플릿이며 `brief/style_plan.md`가 ¶별 제안, 검증은 `app/mixed.py`(MIXED_*/EXPLAIN_*/LIST_*). 근거 `docs/mixed_style_analysis.md`(사람 MOM 3건), 스킬 0c. 순수 설명식 `mom_explain.yaml`·나열식 `mom_compact.yaml`은 비교용.

## 피드백 학습 (사용자 수정본 → 승인 규칙)
`app/docx_diff.py`(DOCX 비교) + `app/feedback.py`(6분류, 규칙 후보, 승인 저장소), CLI `feedback diff|approve|reject|rules|export`, 스킬 `/learn-mednote-style`.
- **사용자가 승인하지 않은 규칙은 절대 적용·저장하지 않는다.** `feedback approve`는 사용자가 명시적으로 고른 후보에만 실행한다.
- 생성은 `style_rules/approved_rules.json`의 `approved` 규칙만 읽는다. 의학적 사실 수정은 문체 규칙으로 일반화하지 않는다.
- 원본·수정본 DOCX와 리포트는 `feedback/`(gitignore)에만 둔다. `*.docx`·`*.pptx`·음성은 커밋하지 않는다(force-add 금지).

## 서술 기법 (Nucleotide 모범 예시 반영)
`kind: check`(쪽마다 O/X + § 끝 정답 상자), `effort`(필수/이해/참고 꼬리표), `origin: "author"`(회색 괄호 — 비유·팁·정정), `kind: concept`(개념 정리 박스), `quiz.explanations`(해설). `prepare`가 `brief/effort_cues.md`를 만든다. 어미는 한다체 유지, **파랑은 기출(PAD) 전용 — 이 기능들은 파랑을 쓰지 않는다.** 규칙: 스킬 `readable-note-organizer` 0b, 분석: `docs/nucleotide_example_analysis.md`.

## 시험 신호·PAD 꼬리표 (사람 정리본 비교에서 얻은 규칙)
`--exam-pdf`는 PDF/DOCX 모두 가능. 기출 해설의 단서(출제예고·강조 안 함·‘배우지 않았다’·이전 기출 반복)를 `ExamItem.signals`로 모아 표지에 **기출 이력(PAD 집계)** 을 자동 표시하고(`meta.exam_history`, 사실만) `prepare`가 `brief/exam_signals.md`를 만든다. 템플릿 `pad_tags: true`(mom_compact)면 PAD 인용 문장에 `[PAD …]`, PAD에만 있는 사실에 `[Only PAD …]` 회색 꼬리표. `--uncovered-pad omit`은 수업에서 안 다룬 기출의 생략을 허용한다. **파랑은 PAD 내용 전용이며 꼬리표·신호는 파랑을 쓰지 않는다.**

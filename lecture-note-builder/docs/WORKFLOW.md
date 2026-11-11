# 워크플로우: 스크립트 → 강의록 + 새 PAD 해설

입력 3개를 넣고 산출물 3개를 받는다. **내용 정리(1~3단계)와 문장 다듬기(4단계)는 따로 한다**(L44). 사람이 판단하는 지점(★)에서는 확인하고 넘어간다.

| 입력 | 산출물 |
|---|---|
| 스크립트(.docx/.txt, 문단은 빈 줄로 구분) | 강의록 `*_강의록.docx/.pdf/.md` |
| 슬라이드 그림(정리본 PDF·PPTX·이미지 폴더) | 새 PAD 파일 `*_PAD해설.md/.docx` |
| PAD 파일(기출 PDF) | 검증 리포트 `validation_report.md` |

한눈에 보기:

```
0 준비 → 1 스토리라인 → 2 내용 정리(표 판단) → 3 1차 빌드(내용 검증) → 4 humanize(writing skill) → 5 최종 빌드·쪽 확인 → 6 PAD → 7 마무리
```

## 0. 준비
- 파일을 `inputs/`에 둔다(비공개, 커밋하지 않음). 규칙은 `style_rules/approved_rules.md`(L1–L44)가 자동 적용된다.
- 그림: MOM이 있으면 이미지만 뽑는다(`examples/abx_figs.py`, `examples/geri_figs.py`). **MOM 글은 비교·평가에만 쓰고 생성에는 읽지 않는다.**
- 스크립트의 `[슬라이드 n]` 꼬리표는 지우고 문단은 빈 줄로 나눈다. 슬라이드 80장 이상이면 `docs/long_lecture.md`도 읽는다.
```bash
python -m app.cli prepare --script inputs/x_script.txt --exam-pdf inputs/x_pad.pdf --figures inputs/x_figs --out outputs/x
```
→ `outputs/x/brief/`(문단 번호 ¶, 기출 목록, 그림 목록, 스켈레톤)

## 1. 스토리라인 (`app/write`)
- 강의 자체의 뼈대(교수님 질문, 학습목표) → 주제문 1줄 → 장마다 주장 1개 → 소절마다 ‘명사구 제목 · 핵심 답 1줄 · ¶ 목록’. 저장: `outputs/x/storyline.md`.
- 제목은 강의 속 표현의 짧은 명사구, 잘 안 쓰는 한글 용어는 영어 병기(L25–L28).
- ★ 핵심 답만 순서대로 읽어 강의 전체가 이해되는지 확인.

## 2. 내용 정리 — 무엇을 어떤 꼴로 담을지 (`examples/x_note.py`)
이 단계에서는 **빠짐없이 담는 것**이 목표다. 문장은 아직 다듬지 않는다.
1. ¶마다 사실을 모두 옮긴다(수치·용어·사례·교수님 강조, 커버리지 100%).
2. **꼴을 고른다**:
   - **표**: 비교 대상이 분명하고 비교 항목이 모두 중요한 개념일 때만(L41). 예: 정상 애도 vs 주요우울장애, 진짜 치매 vs 가성치매, 4대 부작용.
   - **① 라벨 줄**: 절차·채점 순서, 같은 틀의 항목 나열(예: MMSE 11개 항목, 치료 기법 4가지).
   - **줄글**: 그 밖의 설명. 기전과 인과는 문단으로 잇는다.
   - **그림·도식**: 강의자료 그림 우선, 해부 구조를 설명하는 문단에는 반드시(anatomy-visual-explainer).
3. **표 안 강조**(L42): 대비되거나 헷갈리는 칸은 `**굵게**`, 반드시 알아야 할 대비는 `{k|빨강+굵게}`.
4. **교수님 강조**(L35–L37): 핵심 구는 빨강+굵게, ‘~라고 강조하셨습니다’는 시험 범위·공부 깊이에만, 넘어간 부분은 회색 괄호, 표지에 공부 깊이 안내.

## 3. 1차 빌드 — 내용 검증
```bash
python -m examples.x_note > outputs/x/note_authored.json
python -m app.cli build --script inputs/x_script.txt --template templates/mom_mixed.yaml \
  --note-json outputs/x/note_authored.json --exam-pdf inputs/x_pad.pdf --pad-notes examples/x_pad_notes.json \
  --out outputs/x --name x --title "…" --subject … --date … --professor … --meta-json examples/x_meta.json
```
- `validation_report.md`: 오류 0, 커버리지 100%, `NUMBER_LOST`/`TERM_LOST` 0, `TABLE_NOT_COMPARISON` 0.
- 여기서 통과한 내용이 4단계의 기준선이다. 4단계에서 사실이 하나라도 빠지면 이 검사들이 다시 잡는다.

## 4. Humanize — writing skill로 문장 다듬기 (L43, `docs/korean_polish.md`)
내용은 그대로 두고 **문장만** 다시 짠다. 순서:
1. **my-writing-style**: 사용자가 직접 고친 문장에서 배운 규칙을 먼저 적용(최우선).
2. **grammar-checker**: 맞춤법, 띄어쓰기, 구두점.
3. **style-guide**: 용어·숫자·어조의 일관성(합니다체, 표 칸 개조식).
4. **humanizer**: 번역투(`에 대한`, `을 통해`), `~것입니다` 남발, 접속사 반복, 단조로운 문장 길이를 고친다. 짧은 단정 줄과 풀어 쓴 설명 문장을 섞는다(L38, `SENTENCE_TOO_LONG`).

지켜야 할 것: 사실·수치·용어·¶ 근거는 바꾸지 않는다. 교수님 구어 인용(‘몰라요’)과 강조 문장 형식, `=`/`→`/`★`, 파랑 = PAD 전용은 유지한다. 고친 곳은 전 → 후로 남긴다.

## 5. 최종 빌드와 쪽 확인 (`app/design`)
- 3단계 명령으로 다시 빌드 → 오류 0, 커버리지 100% 유지 확인(4단계에서 빠진 사실이 없는지).
- 쪽 이미지로 표지, 비교 페이지, 마지막 요약을 확인: 목차 쪽번호, 그림과 설명의 대응, 잘림, 빈 쪽, 표 쪼개짐. 사진 비교·검사·수술 전후는 [사시 MOM 디자인 규칙](design_mom_format.md#사진-비교와-검사수술-사례)을 따른다.
- ★ 어긋난 그림은 `figures.json`에서 고친다.
- (선택) MOM 근접 루프: `python -m app.cli compare-mom <MOM.pdf> outputs/x/x_강의록.pdf --note outputs/x/note.json` (스킬 `mom-closeness-loop`). 다른 강의의 MOM은 문체만 비교(L24).

## 6. PAD — 파랑과 새 PAD 해설 (`app/pad`)
- **파랑 칠하기**: PAD 문항과 노트 문장을 대응해 PAD 내용만 파랑(무조건), 출처는 `PAD 2022(20학번) Q1`. 별도 기출 섹션은 두지 않는다. `BLUE_WITHOUT_PAD` 0건. 기출 없는 소절에는 개념 Check를 두지 않는다(L20).
- **새 PAD 파일**: 같은 유형의 기출은 한 묶음으로 합쳐 ‘이번 강의 기준 해설’을 한 번만 쓴다. ★ 스크립트에 없는 내용은 ‘직접 다루지 않았습니다’로 남기고 지어내지 않는다. 해설 문장도 4단계 humanize를 거친다.

## 7. 마무리
- 테스트 통과(`pytest -q`), 사람이 못 보는 근사 항목(그림 위치, 보라색 표시)을 알린다.
- 커밋·푸시(`outputs`는 md/pdf/json만 `git add -f`, 비공개 입력·DOCX·MOM PDF는 올리지 않음). 사용자가 수정한 DOCX가 있으면 `/learn-mednote-style`로 비교하고 **승인한 규칙만** 저장한다.

## 사람이 개입하는 지점(★)
스토리라인 핵심 답 확인 · 어긋난 그림 위치 · 해설에서 스크립트에 없는 내용 · 새 규칙 승인.

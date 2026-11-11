# 워크플로우: 스크립트 → 강의록 + 새 PAD 해설

입력 3개를 넣고 산출물 3개를 받는다. 사람이 판단하는 지점(★)에서는 확인하고 넘어간다.

| 입력 | 산출물 |
|---|---|
| 스크립트(.docx/.txt, `[mm:ss - mm:ss]` 구간) | 강의록 `*_강의록.docx/.pdf/.md` |
| 슬라이드 그림(정리본 PDF·PPTX·이미지 폴더) | 새 PAD 파일 `*_PAD해설.md/.docx` |
| PAD 파일(기출 PDF) | 검증 리포트 `validation_report.md` |

## 0. 준비
- 파일을 `inputs/`에 둔다(비공개, 커밋하지 않음). 규칙은 `style_rules/approved_rules.md`(L1–L24)가 자동 적용된다.
- 그림: MOM이 있으면 이미지만 뽑는다(`examples/abx_figs.py`). **MOM 글은 비교·평가에만 쓰고 생성에는 읽지 않는다.**
```bash
python -m app.cli prepare --script inputs/x_script.txt --exam-pdf inputs/x_pad.pdf --figures inputs/x_figs --out outputs/x
```
→ `outputs/x/brief/`(문단 번호 ¶, 기출 목록, 그림 목록, 스켈레톤)

## ① 쓰기 — 스크립트 → 정리글 (`app/write`)
1. **스토리라인 먼저(top-down)**: 강의 자체의 뼈대(교수님 질문, 학습목표) → 주제문 1줄 → 장마다 주장 1개 → 소절마다 ‘질문 · 핵심 답 1줄 · 설명형/나열형 · ¶ 목록’. 저장: `outputs/x/storyline.md`. ★ 핵심 답만 순서대로 읽어 강의 전체가 이해되는지 확인.
2. **제목과 용어**: 장·소절 제목은 강의 속 표현의 명사구(‘편도체(amygdala)의 구조와 연결’)이고, 잘 안 쓰는 한글 용어는 영어 또는 병기(L25, L26). 제목이 스토리라인에서 온 압축어가 아닌지 확인한다.
3. **정리글 작성**: `examples/x_note.py` → `outputs/x/note_authored.json`. 규칙: 한 문장에 사실 하나, 합니다체(L5), 표 칸 개조식(L19), 정의 → 그럼 → 기전 사슬, 안내문·소절 끝 요약 금지, 교수 인용형 금지(L6).
4. **근거 검증**: 모든 문장이 `slide_refs`(¶ 번호)를 가진다. 숫자·용어가 스크립트와 같은지, 빠진 문단이 없는지(커버리지 100%).

## ② 디자인 — 정리글 + 이미지 → 문서 (`app/design`)
4. **빌드**
```bash
python -m examples.x_note > outputs/x/note_authored.json
python -m app.cli build --script inputs/x_script.txt --template templates/mom_mixed.yaml \
  --note-json outputs/x/note_authored.json --exam-pdf inputs/x_pad.pdf --pad-notes examples/x_pad_notes.json \
  --out outputs/x --name x --title "…" --subject … --date … --professor … --meta-json examples/x_meta.json
```
5. **쪽 확인**: PDF를 쪽 이미지로 보고 빈 쪽, 표 쪼개짐, 그림 위치를 점검. 그림 중심 개념 목록은 도식으로(슬라이드 그림 우선, 없으면 새로 그림). 요약 쪽에는 그 주제의 그림을 넣는다(L21). ★ 어긋난 그림은 `figures.json`에서 고친다.
6. **MOM 근접 루프(선택)**: `python -m app.cli compare-mom <MOM.pdf> outputs/x/x_강의록.pdf --note outputs/x/note.json` → 남은 차이를 고치고 재빌드(스킬 `mom-closeness-loop`, 4회 등 횟수 지정). 다른 강의의 MOM은 문체만 비교(L24).

## ③ PAD — 파랑과 새 PAD 해설 (`app/pad`)
7. **파랑 칠하기**: PAD 문항과 노트 문장을 대응해 PAD 내용만 파랑(무조건), 출처는 `PAD 2022(20학번) Q1`. 별도 기출 섹션은 본문에 두지 않는다. 검증: `BLUE_WITHOUT_PAD` 0건. 기출 없는 소절에는 개념 Check를 두지 않는다(L20).
8. **새 PAD 파일**: 같은 유형의 기출은 한 묶음(유형)으로 합쳐 ‘이번 강의 기준 해설’을 한 번만 쓴다. 근거는 노트의 문장·표와 `pad_notes.json`(직접 쓴 해설 `explanation`, 문항별 `answer_note`). ★ 스크립트에 없는 내용은 ‘직접 다루지 않았습니다’로 남기고 지어내지 않는다.

## 마무리
9. `validation_report.md` 오류 0, 테스트 통과(`pytest -q`), 사람이 못 보는 근사 항목(그림 위치, 보라색 표시)을 알린다.
10. 커밋·푸시(`outputs`는 md/pdf/json만 `git add -f`, 비공개 입력·DOCX·MOM PDF는 올리지 않음). 사용자가 수정한 DOCX가 있으면 `/learn-mednote-style`로 비교하고 **승인한 규칙만** 저장한다.

## 사람이 개입하는 지점(★)
스토리라인 핵심 답 확인 · 어긋난 그림 위치 · 해설에서 스크립트에 없는 내용 · 새 규칙 승인.

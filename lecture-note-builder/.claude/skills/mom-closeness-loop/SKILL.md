---
name: mom-closeness-loop
description: Iteratively make a generated lecture note (PDF/DOCX) closer to a human-written MOM note. Measure page fill, density and sentence style against the MOM PDF (`compare-mom`), find readability problems page by page, fix them in the code / template / note, rebuild, verify, record, push. Use when the user says /loop, "MOM에 근접", "MOM과 비교해서 개선", "가독성 떨어지는 부분 찾아줘", or uploads a human MOM PDF next to a generated note.
---

# MOM 근접 루프

사람이 쓴 MOM 정리본과 우리 노트를 **같은 쪽 단위로 비교 → 측정 → 고침 → 다시 측정**하는 절차. 항균제(Clinical Therapeutics) 노트에서 여러 회차 돌려 얻은 규칙과 함정을 그대로 담았다. 결과 기록: `references/loop_findings.md`, 도구: `python -m app.cli compare-mom`, 예: `examples/abx_note.py`.

## 0. 철칙 (어기지 않는다)
1. **MOM 글은 비교 전용.** 노트를 *만들* 때는 MOM에서 슬라이드 이미지 외에는 읽지 않는다(사용자 지시). 비교·평가 때만 글(pdftotext)과 쪽 이미지를 본다.
2. **파랑 = 이 강의 PAD(기출) 내용 전용**, 무조건. MOM이 다른 교수님 파드까지 파랑으로 칠해도 따르지 않는다.
3. **사용자가 승인하지 않은 학습 규칙은 저장하지 않는다.** 사용자가 “학습해”, “모두 적용”처럼 명시했을 때만 `approve_manual`로 등록하고, 등록한 규칙 ID와 철회 방법(`feedback rules --retire`)을 보고한다.
4. 사용자가 이미 승인한 규칙(L1–L21, `style_rules/approved_rules.md`)과 충돌하면 조용히 바꾸지 말고 보고한다(예: MOM에 없는 수사 질문은 사용자 문체라 유지하고 물어본다).
5. 숫자는 기억이 아니라 **세어서** 쓴다(실제로 “표 13개, Check 12개”를 잘못 적었다가 11개, 15개로 정정했다).
6. 입력 자료(`inputs/`), DOCX, PPTX는 커밋하지 않는다. 결과물은 `git add -f`로 md/pdf/json만.

## 1. 한 회차 (이 순서)
1. **측정**: `python -m app.cli compare-mom <MOM.pdf> outputs/<name>/<name>_강의록.pdf --note outputs/<name>/note.json --out outputs/<name>/mom_compare.md`
   → 쪽수, 쪽당 글자, 글자 크기, 쪽 평균 채움, 가장 빽빽한 쪽 잉크, 절반 이하로 빈 쪽, 표 칸 문체, 제목 길이, 기출 없는 Check, **남은 차이** 목록.
2. **쪽 이미지로 확인**(측정이 못 보는 것): `pdftoppm -r 85 -png` 로 두 쪽씩 붙여 MOM과 같은 쪽을 나란히 본다. 아래 점검표(§3)를 쪽마다 대본다. 숫자가 좋아도 이미지에서 잘리거나 떨어진 곳이 나온다(빈 쪽, 제목만 쪽 끝에 남음).
3. **문제 목록**: 심각한 순서로, 쪽 번호·원인·고칠 곳을 적는다. 사용자가 “찾아줘”만 했으면 여기서 멈추고 보고한다. “적용해줘/루프”면 계속한다.
4. **고침**: 가능하면 **코드/템플릿/검사 규칙**으로(재발 방지), 그다음 노트 본문. 새 기능은 `tests/`에 테스트를 추가한다.
5. **재빌드·검증**: `python -m pytest -q`; 노트 빌드(아래 §5); `validation.json`에서 `ERROR` 0, 새 검사 경고 0을 확인; 다시 `compare-mom`과 쪽 이미지.
6. **기록**: `outputs/<name>/review_vs_MOM.md`에 절을 추가(전/후 표, 고친 것, 남은 차이). 규칙화할 것은 스킬·`CLAUDE.md`에.
7. **커밋·푸시**(§6) 후 사용자에게 한국어로 보고(첨부: PDF, 대표 쪽 이미지, 비교 문서).
8. **계속할지 판단**: `compare-mom`의 남은 차이가 **내가 혼자 고칠 수 있는 것**이면 다음 회차를 예약한다. 사용자 결정이 필요한 것만 남았으면 멈추고 결정 목록을 보고한다(§4).

## 2. 구성요소 (노트 JSON에서 쓰는 것)
| 목적 | 쓰는 것 |
|---|---|
| 나열형 소절 = 표 | `kind: rows` (`rows=[[라벨, 칸…]]`, `col_titles`, `col_widths`; 칸 안 줄바꿈 `\n`; 작은 표는 한 쪽에 붙음) |
| 강의의 질문·역질문 | `kind: qa` (`left_title`=“질문1”, `text`=질문, `left`=“A.” 줄) — 표가 아니라 **테두리 문단**이다(제목 → 질문 → A. → 표가 함께 움직이게) |
| 큰 슬라이드 그림 | `kind: figure` (쪽 첫머리, 그림 내용은 같은 소절의 표가 말한다) |
| 소절 옆 시험 표시 | `Topic.mark = "출제예고 · 기출"` (빨강, MOM의 ⭐출제예고/짤⭐ 자리) |
| 쪽 나눔 | 템플릿 `chapter_page_break`, `Topic.new_page`; 표 앞 도입 문장은 자동으로 표와 붙음 |
| 장치 줄이기 | 템플릿 `basics_style: band`, `checks_where: chapter`, `cover_style: box` |
| 사소한 영어 병기 | `meta.omitted_terms = "specimen\|optimal"` (괄호를 끼워 넣지 않는다) |

기본 템플릿 `templates/mom_mixed.yaml`(본문 10.5pt). 요약 쪽은 `role: "front"` 주제 둘(예: `요약 ① 4사분면 [출제예고]`, `요약 ② PK/PD [중요언급]`): **그 주제의 슬라이드 그림 + 표**(L21).

## 3. 점검표 (MOM과 같은 쪽을 보며) — 각 항목은 빌드 검사나 측정으로 재발을 잡는다
| 문제 | 원인 | 고치는 곳 | 잡는 검사 |
|---|---|---|---|
| 도입 문장이 표·그림과 다른 쪽에 남음, 소절 제목+질문 상자만 쪽 끝 | keep-with-next가 표를 못 건넌다(LibreOffice) | 질문 상자를 문단으로, 도입 문단·표 행에 keep_with_next | 쪽 이미지 |
| 빈 쪽이 통째로 생김 | 쪽 끝 여백 문단이 넘쳐 새 쪽 강제와 겹침 | 얇은 여백 문단 `_gap` | `compare-mom`(채움), 쪽별 글자 수 0 |
| 표 칸 글자가 테두리에 붙음, 머리글 단어 중간 끊김 | 칸 여백 없음, 좁은 칸 | `tblCellMar`, 영어는 첫 행으로, 칸 너비 | 쪽 이미지, `TABLE_ORPHAN` |
| 표 칸 줄 끝 1–2글자만 다음 줄(“항균\n제”) | 한글은 글자 단위로 줄바꿈 | 줄을 나눈다 | `TABLE_ORPHAN` |
| 제목이 두 줄, 질문 상자와 같은 말 반복 | 제목에 용어를 몰아넣음 | 소절 44자·장 29자, 제목은 짧은 명사구 | `HEADING_TOO_LONG` |
| 문단이 5줄 덩어리, 괄호 많음 | 문장을 억지로 이음, TERM_LOST 경고를 괄호로 막음 | 3줄(175자) 이하, `meta.omitted_terms` | `PARAGRAPH_TOO_LONG` |
| 문단 중간에 회색·빨강 문장 | 색 문장을 문단에 끼움 | 별도 줄 | `COLOUR_IN_PARAGRAPH` |
| 같은 사실이 표·띠·문단·Check로 반복 | 소절마다 모양을 바꿔 되풀이 | 한 소절 한 모양, PAD(파랑)는 표 안에만 | 쪽 이미지 |
| 개념 Check가 소절마다 | — | **기출(PAD)이 있는 소절에만**(L20), 장 끝 한 상자, `[§n]` 표시 | `CHECK_NO_PAD`, `CHECK_TOO_MANY` |
| 표 칸이 ‘-다’ 문장 | MOM의 표 칸은 개조식 | **명사형, ‘-음/-함’**(L19), 설명 문단·A.·작성자 메모는 합니다체(L5 v2) | `TABLE_CELL_STYLE` |
| 표지가 빽빽, 제목 두 번 | 배너 표지 | `cover_style: box`, 코멘트 3문단 | 쪽 이미지 |
| QUIZ 상자가 쪽 사이에서 갈라짐, QUIZ가 § 번호를 받음 | — | `cantSplit`, QUIZ는 번호 없음 | 쪽 이미지 |
| 요약 쪽에 그림 없음/주제 그림 없음 | — | 요약 쪽 = 그 주제의 슬라이드 그림 + 표 | `SUMMARY_NO_VISUAL` |
| **PDF에서 한글 굵게가 안 보임** | 샌드박스에 한글 굵은 글꼴 없음(`pdffonts`: Regular만) | Word 파일은 정상. 사용자가 제외했다. 한계로 기록 | — |

## 4. 멈추는 조건 (사용자 결정이 필요한 것)
- **QUIZ와 개념 Check**: MOM에는 없다. 모범 예시(Nucleotide)에서 승인한 기능이라 지우려면 확인한다(쪽수 13 → 11에 가장 큰 영향).
- **수사 질문(“그럼 …까?”)·독자 안내(“~보자”)**: MOM에는 없지만 사용자가 직접 고친 문장에서 배운 문체.
- **PDF 한글 굵은 글꼴**: 환경 설치 또는 굵게 대체.
- **입력에 없는 내용**: PPT에만 있는 표(예: 장기별 흔한 균), MOM의 넷째 칸 사례. 만들어 내지 않는다.
- 같은 문제를 두 회차 연속 못 줄였을 때.

## 5. 재현: 항균제 예시
입력(비공개, `inputs/`에 직접 넣는다): 스크립트 `abx_script.txt`(`[mm:ss - mm:ss]` 구간 헤더), 기출 PDF `abx_pad.pdf`. 슬라이드 그림은 MOM PDF에서 **이미지만** 뽑는다(스크립트가 같은 파일을 바이트 단위로 재현함을 확인). 메타 `examples/abx_meta.json`은 저장소에 있다.
```bash
python3 -m examples.abx_figs <MOM.pdf> --out inputs/abx_figs      # f1..f5 + 곡선 두 장을 합친 f34
mkdir -p outputs/abx && cp outputs/abx/storyline.md /경로/새_out/   # 스토리라인이 없으면 STORYLINE_MISSING 경고 1개가 더 뜬다
python3 -m examples.abx_note > outputs/abx/note_authored.json
python3 -m app.cli build --script inputs/abx_script.txt --template templates/mom_mixed.yaml \
  --note-json outputs/abx/note_authored.json --exam-pdf inputs/abx_pad.pdf --out outputs/abx --name abx \
  --title "Clinical Therapeutics: 중환자와 항균제" --subject 임상약리 --date 2026-08-19 --period 2교시 \
  --professor 한성필 --meta-json examples/abx_meta.json --pad-notes examples/abx_pad_notes.json --summary-figures 0
python3 -m app.cli compare-mom <MOM.pdf> outputs/abx/abx_강의록.pdf --note outputs/abx/note.json
```
재현 확인(새 폴더에서 실행): 노트 JSON 동일, 검증 항목 46개 동일(스토리라인을 복사한 경우), 그림 6개 바이트 동일.
기대: 13쪽, 오류 0, 쪽당 글자 ≈ MOM(609), 표 칸 ‘-다’ 0줄, 절반 이하로 빈 쪽 0, 개념 Check 3(기출 소절만).
새 강의는 `make-lecture-note` 스킬의 절차(`prepare` → `storyline.md` → 노트 스크립트 → `build`) 뒤에 이 루프를 돌린다.

## 6. 커밋·푸시 (실수 방지)
- 푸시는 **종료 코드로 확인**한다: `if git push -u origin <branch>; then …; else git fetch; git rebase origin/<branch>; fi`. `git push … | tail -1 && break` 는 push가 실패해도 성공으로 보인다(실제로 한 번 놓칠 뻔했다).
- 원격에 새 커밋이 있으면 **덮어쓰지 않고 리베이스**한다. 충돌 없이 합쳐져도 같은 함수를 둘이 고쳤다면 테스트를 돌리고 결과물(md/pdf)을 다시 만든다.
- 커밋 메시지 끝에 시스템이 지정한 `Co-Authored-By`, `Claude-Session` 줄.

## 6. 다른 강의의 MOM(그림 중심)과 비교할 때
`compare-mom`은 MOM의 쪽당 큰 그림이 2개 이상이면 쪽수·글자 밀도·글자 크기·잉크 비교를 생략하고 `prose_style`(본문 문장 길이, 질문, 빨강, 글 없는 그림)만 보고한다. 문체 판단은 `docs/mom_style_head_trauma.md`처럼 ‘채택 / 채택하지 않음(승인 규칙 우선) / 후보’로 나눠 적고, 승인 전 규칙은 `approved_rules`에 넣지 않는다.

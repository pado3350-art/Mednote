# 설계

## 데이터 흐름
```
PPTX ─ extract_slides ─▶ slides.json ┐
TXT/DOCX ─ transcript ─▶ segments    ├─ align_content ─▶ alignment.json
                                     ┘          │
                  template(YAML) ─▶ generate_notes (Offline | Anthropic) ─▶ note.json
                                                │
                                    validate_notes ─▶ validation.json / .md
                                                │
                                    export_docx ─▶ .docx / .md
```
각 단계 산출물을 JSON으로 저장 → 특정 슬라이드만 재생성/검토 가능(향후 UI).

## 핵심 결정
| 결정 | 이유 |
|---|---|
| AI는 `Topic` JSON만 생성(forced tool call, Pydantic 스키마) | 서식 일관성, 검증 가능 |
| 표·이미지는 코드가 원본 첨부 | 환각/누락 방지 |
| `Statement.origin` + `slide_refs/segment_ids/time_ranges` | PPT 문장 vs 구두 설명 구분, 출처 추적 |
| OfflineBackend 기본 제공 | 테스트·드라이런·API 없는 환경 |
| 검증은 규칙 기반(커버리지, 수치, 용어, 표/이미지, 근거 유사도, 발화 누락) | 재현 가능한 1차 방어선 |

## 검증 코드
`SLIDE_MISSING NUMBER_LOST TABLE_LOST IMAGE_LOST SEGMENT_LOST NO_SOURCE BAD_REF`(error),
`TERM_LOST UNGROUNDED LOW_ALIGNMENT`(warning), `REVIEW_FLAG`(info).

## 로드맵 (README의 개발 계획 대응)
- ✅ MVP: PPTX + TXT → DOCX/MD, 정렬, 검증, 템플릿(YAML), Anthropic 백엔드
- 다음: PDF 입력(PyMuPDF), PDF 출력, 음성 전사(faster-whisper; `lecture-transcriber` 스킬 참조), 슬라이드 렌더링 이미지 분석
- 이후: Streamlit 검토 UI(원본/강의록 나란히), 부분 재생성, 다중 템플릿(usmle/case-study), 일괄 처리

## 한계
- 유사도 정렬은 어휘 기반이며 의미 임베딩이 아님; 마커/타임스탬프가 있으면 더 정확.
- 용어/수치 검증은 정규식 휴리스틱 → 오탐 가능(경고는 사람이 판단).
- Anthropic 백엔드는 가짜 클라이언트로만 테스트됨(실 API 미검증).

## PAD(기출문제) 입력과 색상 규칙
`--exam-pdf`로 기출 PDF를 넣으면 `app/exam.py`가 문항을 파싱해 *기출 유닛*(번호 101~)으로 추가한다.
유닛은 강의 구간과 동일하게 커버리지·출처 추적 대상이다(모든 문항이 어떤 Topic에 반영되어야 함).
파랑 글씨는 기출 내용 전용이며, 검증기가 `BLUE_WITHOUT_PAD`(error) / `PAD_NOT_BLUE`(warning)로 확인한다.
섹션 0에는 MOM의 '땡시 기출' 표처럼 기출 빈도(heat 색칠)·문항 목록 표를 둔다.

## 스크립트 단독 모드: AI 목차 (시간 구간 분해 안 함)
`parse_flow_script`는 스크립트를 **하나의 연속된 발화 단락 흐름**(¶1, ¶2, …)으로 읽는다. `[00:00–02:00] 제목 | 원본 N쪽` 같은
시간 구간 헤더는 구성 정보로 쓰지 않고 버린다(끝의 '검증 참고' 문단만 `kind=note`로 남아 부록이 된다).
목차는 `app/outline.py`가 만든다:
- `--backend anthropic`: Claude가 전체 단락을 읽고 주제 흐름으로 섹션을 나눔(forced tool call) → 섹션마다 1회씩 노트 생성.
- 오프라인: 어휘 유사도 기반 주제 전환 탐지 + tf-idf 키워드 제목(휴리스틱, 품질은 AI보다 낮음).
- `outline.json`이 저장되며, 직접 고쳐서 `--outline-json`으로 다시 적용 가능. `normalize_outline`이 모든 단락이 정확히 한 번, 순서대로 포함되도록 보정.
PPTX 모드는 기본이 슬라이드별(`--toc unit`)이고 `--toc ai|heuristic`으로 슬라이드를 묶는 목차도 만들 수 있다.
출처 표기는 `발화 ¶5–7` / `PAD 2022(20학번) Q1` 형식.

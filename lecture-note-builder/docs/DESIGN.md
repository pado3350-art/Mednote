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

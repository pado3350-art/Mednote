# Mednote — UI/UX 디자인 규칙

> 이 문서는 모든 UI 작업에 일관되게 적용되어야 하는 디자인 원칙을 정의합니다.
> 새로운 컴포넌트나 페이지를 개발할 때 반드시 이 규칙을 먼저 확인하세요.

---

## 1. 핵심 원칙: 가독성 최우선 (Readability First)

모든 디자인 결정에서 **가독성과 명확성**이 최우선입니다.
시각적 화려함보다 정보 전달의 명확함을 우선시합니다.

---

## 2. 색상 규칙 (Color Rules)

### 2.1 텍스트 & 배경 대비
| 배경색 | 허용 텍스트 색 | 금지 텍스트 색 |
|--------|--------------|--------------|
| 흰색 (`#FFFFFF`) | 검정 (`#111827`), 진한 회색 (`#374151`) | 연한 회색, 연한 파란색 |
| 연한 회색 (`#F9FAFB`, `#F3F4F6`) | 검정, 진한 회색 | 흰색, 연한 색상 |
| 파란색 계열 (`#2563EB`, `#3B82F6` 등) | **흰색(`#FFFFFF`) 전용** | **검정, 진한 회색 — 절대 금지** |
| 진한 남색 / 어두운 배경 | 흰색, 연한 회색 | 검정 — 절대 금지 |

> **규칙 요약:** 파란 배경에 검정 텍스트는 절대 사용하지 않습니다.
> 파란 버튼/카드/배지에는 항상 **흰색 텍스트**를 사용합니다.

### 2.2 브랜드 색상 팔레트
```
Primary Blue:   #2563EB  (버튼, 링크, 강조 요소)
Primary Hover:  #1D4ED8  (인터랙션 상태)
Light Blue:     #EFF6FF  (배경 강조, 카드 배경)
Success Green:  #16A34A
Warning Amber:  #D97706
Error Red:      #DC2626
Text Primary:   #111827
Text Secondary: #6B7280
Border:         #E5E7EB
Background:     #F9FAFB
Surface:        #FFFFFF
```

### 2.3 파란 버튼 표준 스펙
```css
/* 항상 이 규칙을 따르세요 */
.btn-primary {
  background-color: #2563EB;
  color: #FFFFFF;          /* 흰색 텍스트 — 필수 */
  font-weight: 600;
}
.btn-primary:hover {
  background-color: #1D4ED8;
  color: #FFFFFF;          /* hover 상태에서도 흰색 유지 */
}
```

---

## 3. 타이포그래피 (Typography)

### 3.1 폰트
- **주 폰트:** `Pretendard` (한국어 최적화) — 없을 경우 `Noto Sans KR` 사용
- **코드/모노:** `JetBrains Mono`, `Fira Code`, `monospace`

### 3.2 폰트 크기 스케일
| 역할 | 크기 | 굵기 |
|------|------|------|
| 페이지 제목 (H1) | 2rem (32px) | 700 |
| 섹션 제목 (H2) | 1.5rem (24px) | 600 |
| 카드 제목 (H3) | 1.25rem (20px) | 600 |
| 본문 | 1rem (16px) | 400 |
| 보조 텍스트 | 0.875rem (14px) | 400 |
| 레이블/배지 | 0.75rem (12px) | 500 |

### 3.3 줄 간격
- 본문: `line-height: 1.75` (한국어 가독성 최적화)
- 제목: `line-height: 1.3`

---

## 4. 레이아웃 & 간격 (Layout & Spacing)

### 4.1 그리드
- 최대 콘텐츠 폭: `max-width: 1280px`
- 기본 패딩: `px-4` (모바일) / `px-8` (데스크톱)
- 카드 그리드: 모바일 1열 → 태블릿 2열 → 데스크톱 3열

### 4.2 간격 단위 (4px 기반)
```
xs:  4px   (0.25rem)
sm:  8px   (0.5rem)
md:  16px  (1rem)
lg:  24px  (1.5rem)
xl:  32px  (2rem)
2xl: 48px  (3rem)
```

### 4.3 카드 컴포넌트 표준
```css
.card {
  background: #FFFFFF;
  border: 1px solid #E5E7EB;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.card:hover {
  box-shadow: 0 4px 12px rgba(0,0,0,0.12);
  transition: box-shadow 0.2s ease;
}
```

---

## 5. 컴포넌트 규칙 (Component Rules)

### 5.1 버튼
| 유형 | 배경 | 텍스트 | 테두리 |
|------|------|--------|--------|
| Primary | `#2563EB` | `#FFFFFF` | 없음 |
| Secondary | `#FFFFFF` | `#374151` | `#D1D5DB` |
| Danger | `#DC2626` | `#FFFFFF` | 없음 |
| Ghost | 투명 | `#2563EB` | 없음 |
| Disabled | `#E5E7EB` | `#9CA3AF` | 없음 |

### 5.2 입력 필드
```css
.input {
  border: 1px solid #D1D5DB;
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 1rem;
  color: #111827;
  background: #FFFFFF;
}
.input:focus {
  border-color: #2563EB;
  outline: 2px solid rgba(37, 99, 235, 0.2);
}
```

### 5.3 배지 (Badge)
- 배지 배경이 색상일 경우 텍스트는 항상 흰색 또는 극도로 진한 색상만 허용

### 5.4 챗봇 말풍선
| 역할 | 배경 | 텍스트 |
|------|------|--------|
| AI 응답 | `#F3F4F6` (연한 회색) | `#111827` (검정) |
| 사용자 입력 | `#EFF6FF` (연한 파란색) | `#1E40AF` (진한 파란색) |

---

## 6. 간격 복습 카드 (Spaced Repetition Card)

복습 카드는 학습 집중도를 높이기 위해 아래 규칙을 따릅니다:
- 배경: 흰색, 테두리: `#E5E7EB`
- 질문 텍스트: H3 크기, `#111827`
- 정답 공개 후 배경: `#F0FDF4` (연한 초록) — 긍정 피드백
- 난이도 버튼: 쉬움(초록/흰), 보통(황색/흰), 어려움(빨강/흰)

---

## 7. 접근성 (Accessibility)

- 모든 색상 조합은 **WCAG 2.1 AA** 기준 (대비율 4.5:1 이상) 준수
- 모든 인터랙티브 요소에 `:focus` 스타일 명시
- 이미지/아이콘에 `alt` 속성 또는 `aria-label` 필수
- 클릭 가능 요소의 최소 크기: 44×44px

---

## 8. 다크 모드 (향후 Phase 3 고려사항)

현재는 라이트 모드만 지원합니다. Phase 3에서 다크 모드 추가 시:
- CSS 변수(`--color-*`)를 사용해 색상을 관리
- 하드코딩된 색상값 사용 금지 — 반드시 CSS 변수 참조

---

## 9. 금지 사항 체크리스트

개발 전 아래 항목을 반드시 확인하세요:

- [ ] 파란 배경에 검정/진한 회색 텍스트 사용 금지
- [ ] 연한 회색 배경에 흰 텍스트 사용 금지
- [ ] 버튼 텍스트와 배경 대비율 4.5:1 미만 금지
- [ ] `color: blue` 같은 브라우저 기본 색상 직접 사용 금지
- [ ] 텍스트 없는 색상만으로 정보 전달 금지 (색맹 고려)

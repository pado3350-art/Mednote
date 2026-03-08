# Mednote — 시스템 아키텍처 & 개발 로드맵

> Katzung 교재 기반 약리학 학습 앱 (의대·약대생/전문가 대상)
> UI, 콘텐츠, LLM 응답 전체 **한국어** 제공

---

## 목차
1. [기술 스택 추천](#1-기술-스택-추천)
2. [시스템 아키텍처 개요](#2-시스템-아키텍처-개요)
3. [단계별 개발 계획](#3-단계별-개발-계획)
4. [데이터베이스 스키마](#4-데이터베이스-스키마)
5. [LLM 통합 전략](#5-llm-통합-전략)
6. [폴더 구조](#6-폴더-구조)

---

## 1. 기술 스택 추천

### 1.1 Frontend
| 항목 | 선택 | 이유 |
|------|------|------|
| UI 프레임워크 | **React 18** + TypeScript | 필수 요건, 생태계 풍부 |
| 빌드 도구 | **Vite** | 빠른 HMR, 최신 번들링 |
| 라우팅 | **React Router v6** | 표준 SPA 라우터 |
| 상태 관리 | **Zustand** | 가볍고 직관적, Redux 대비 보일러플레이트 최소 |
| 서버 상태 | **TanStack Query (React Query)** | API 캐싱, 로딩/에러 상태 자동 관리 |
| 스타일링 | **Tailwind CSS** | 유틸리티 클래스로 디자인 규칙 일관 적용 용이 |
| 시각화 | **Recharts** + **D3.js** (복잡한 PK/PD 그래프) | React 친화적, 커스터마이징 자유도 |
| 폼 관리 | **React Hook Form** + **Zod** | 타입 안전한 폼 검증 |
| 한국어 폰트 | **Pretendard** (CDN) | 가독성 최적화 한국어 폰트 |

### 1.2 Backend
| 항목 | 선택 | 이유 |
|------|------|------|
| 런타임 | **Node.js** (v20 LTS) | Frontend와 언어 통일, 생태계 |
| 프레임워크 | **FastAPI (Python)** | LLM 연동(Python 생태계)에 최적, 자동 API 문서 |
| 대안 | **Express.js** | Node 팀 선호 시 |
| 인증 | **Supabase Auth** 또는 **JWT + Refresh Token** | |
| LLM 연동 | **Python SDK (Anthropic / OpenAI)** | 스트리밍 지원 |

> **추천 조합:** React (Vite/TS) + **FastAPI (Python)** + Supabase
> LLM 생태계는 Python이 압도적으로 강력하므로 백엔드를 Python으로 유지하는 것이 유리합니다.

### 1.3 데이터베이스
| 항목 | 선택 | 이유 |
|------|------|------|
| 주 DB | **PostgreSQL** (via Supabase) | 복잡한 관계형 데이터(복습 스케줄링), 풀 텍스트 검색 |
| 호스팅 | **Supabase** | PostgreSQL + Auth + Realtime + Storage 통합, 무료 티어 |
| 캐시 | **Redis** (Phase 2+) | LLM 응답 캐싱, 세션 관리 |

> Supabase를 선택하면 Auth, DB, Storage, Realtime을 단일 플랫폼에서 관리 가능하여
> 초기 개발 속도가 크게 향상됩니다.

### 1.4 LLM API
| 항목 | 선택 | 이유 |
|------|------|------|
| 1순위 | **Claude (Anthropic API)** — `claude-sonnet-4-6` | 긴 맥락 이해, 의학 정확도, 한국어 품질 우수 |
| 2순위 | **GPT-4o (OpenAI)** | 대안 |
| 프롬프트 전략 | System Prompt에 한국어 강제 + 약리학 역할 지정 | |
| 스트리밍 | SSE (Server-Sent Events) | 실시간 타이핑 효과 |

### 1.5 인프라 & 배포
| 항목 | 선택 |
|------|------|
| Frontend 배포 | **Vercel** (자동 CI/CD, 글로벌 CDN) |
| Backend 배포 | **Railway** 또는 **Render** (FastAPI 컨테이너) |
| 컨테이너 | **Docker** + `docker-compose` (로컬 개발) |
| CI/CD | **GitHub Actions** |

---

## 2. 시스템 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────┐
│                        클라이언트 (브라우저)                         │
│                    React 18 + TypeScript + Vite                  │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────────────┐ │
│  │챕터 요약  │ │AI 챗봇   │ │개인 노트  │ │간격 반복 복습카드   │ │
│  │+ 시각화  │ │스트리밍  │ │저장/관리  │ │Ebbinghaus 알고리즘 │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────────────┘ │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS / REST / SSE
┌──────────────────────────▼──────────────────────────────────────┐
│                      Backend API (FastAPI)                        │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────────────────────┐ │
│  │ /api/chat   │ │ /api/notes   │ │ /api/review               │ │
│  │ LLM 프록시  │ │ CRUD + 저장  │ │ SRS 스케줄 계산           │ │
│  │ + 스트리밍  │ │              │ │ SM-2 알고리즘             │ │
│  └─────────────┘ └──────────────┘ └───────────────────────────┘ │
└─────────────┬───────────────────────────────┬────────────────────┘
              │                               │
┌─────────────▼──────────┐      ┌─────────────▼──────────────────┐
│   PostgreSQL (Supabase) │      │      Anthropic Claude API       │
│   - users               │      │   claude-sonnet-4-6             │
│   - chapters            │      │   한국어 System Prompt          │
│   - notes               │      │   SSE 스트리밍                  │
│   - review_cards        │      └────────────────────────────────┘
│   - review_logs         │
└────────────────────────┘
```

---

## 3. 단계별 개발 계획

### Phase 1 — 핵심 MVP (예상 기간: 6~8주)

**목표:** 핵심 학습 루프 구축 (읽기 → 질문 → 저장)

#### Sprint 1–2: 프로젝트 기반 구축 (2주)
- [ ] 모노레포 구성: `/frontend` (Vite+React+TS), `/backend` (FastAPI)
- [ ] Supabase 프로젝트 생성 및 기본 스키마 적용
- [ ] Supabase Auth 연동 (이메일/비밀번호 + Google OAuth)
- [ ] 기본 라우팅 설정: `/`, `/chapters`, `/chat`, `/notes`
- [ ] DESIGN_RULES.md 기반 Tailwind 테마 설정 (`tailwind.config.ts`)
- [ ] Pretendard 폰트 적용
- [ ] Docker Compose 로컬 개발 환경 구성

#### Sprint 3–4: 챕터 요약 & 기본 시각화 (2주)
- [ ] 챕터 목록 페이지 (`/chapters`)
- [ ] 챕터 상세 페이지 (`/chapters/:id`) — Katzung 챕터 구조 반영
- [ ] Markdown 기반 챕터 콘텐츠 렌더링 (`react-markdown`)
- [ ] **Phase 1 시각화:** 기본 약동학(PK) 그래프 (Recharts)
  - 혈중 농도-시간 곡선 (단회 투여)
  - Tmax, Cmax, AUC 시각적 표시
- [ ] 콘텐츠 검색 기능 (챕터 내 키워드 검색)

#### Sprint 5–6: AI 챗봇 (2주)
- [ ] FastAPI `/api/chat` 엔드포인트 구현
- [ ] Anthropic Claude API 연동 (SSE 스트리밍)
- [ ] System Prompt 설계:
  ```
  당신은 Katzung 약리학 교재를 기반으로 한 전문 약리학 튜터입니다.
  모든 답변은 반드시 한국어로 작성하세요.
  의학적 정확성을 최우선으로 하며, 임상적 관련성을 포함하여 설명하세요.
  ```
- [ ] React 챗봇 UI (타이핑 애니메이션, 대화 이력)
- [ ] 챗봇 응답에 "노트에 저장" 버튼 추가

#### Sprint 7–8: 개인 노트 시스템 (2주)
- [ ] 노트 저장 API (`POST /api/notes`)
- [ ] 노트 목록 & 상세 페이지
- [ ] 노트 편집 (제목, 태그, 내용)
- [ ] 노트 삭제 & 검색
- [ ] 챕터 요약에서도 "노트 저장" 원클릭 기능

**Phase 1 완료 기준:**
- 사용자가 로그인하여 챕터를 읽고, AI에게 질문하고, 답변을 노트에 저장할 수 있음

---

### Phase 2 — 간격 반복 시스템 (예상 기간: 4~6주)

**목표:** Ebbinghaus 망각 곡선 기반 스마트 복습 시스템

#### Sprint 9–10: SRS 핵심 엔진 (2주)
- [ ] **SM-2 알고리즘 구현** (Python):
  ```python
  def calculate_next_review(quality: int, repetitions: int,
                             easiness: float, interval: int):
      """
      quality: 0~5 (0=완전히 잊음, 5=완벽하게 기억)
      SM-2 알고리즘으로 다음 복습 간격 계산
      """
      if quality >= 3:
          if repetitions == 0:
              interval = 1
          elif repetitions == 1:
              interval = 6
          else:
              interval = round(interval * easiness)
          repetitions += 1
      else:
          repetitions = 0
          interval = 1

      easiness = max(1.3, easiness + 0.1 - (5 - quality) * 0.08)
      next_review = datetime.now() + timedelta(days=interval)
      return interval, repetitions, easiness, next_review
  ```
- [ ] 복습 카드 생성 API (노트 → 플래시카드 변환)
- [ ] 복습 일정 조회 API (`GET /api/review/due`)
- [ ] 복습 결과 기록 API (`POST /api/review/result`)

#### Sprint 11–12: 복습 UI & 알림 (2주)
- [ ] 플래시카드 복습 인터페이스
  - 앞면: 질문 / 뒤면: 답변
  - 난이도 버튼: 다시(0), 어려움(3), 보통(4), 쉬움(5)
- [ ] 복습 대시보드: 오늘 복습할 카드 수, 누적 통계
- [ ] 진도 시각화: 망각 곡선 그래프 (D3.js)
- [ ] 브라우저 Push 알림 (복습 리마인더)
- [ ] Redis 캐싱: 당일 복습 스케줄 캐싱

#### Sprint 13: 통계 & 개선 (1주)
- [ ] 학습 통계 페이지 (연속 학습일, 총 복습 횟수, 정확도)
- [ ] 취약 개념 자동 식별 (낮은 easiness 카드 그룹화)
- [ ] 주간 복습 리포트

**Phase 2 완료 기준:**
- 저장된 노트가 자동으로 플래시카드화되어 최적 시점에 복습 알림이 오고, 결과에 따라 다음 복습 일정이 조정됨

---

### Phase 3 — 고급 시각화 & 기능 확장 (예상 기간: 6~8주)

**목표:** 인터랙티브 시뮬레이션으로 개념 직관적 이해

#### Sprint 14–16: 고급 PK/PD 시뮬레이션 (3주)
- [ ] **약동학(PK) 인터랙티브 시뮬레이터**
  - 슬라이더로 파라미터 실시간 조절: Vd, CL, t½, bioavailability (F)
  - 단회 vs. 반복 투여 비교
  - 경구/정맥 투여 경로 선택
  - Steady-state 도달 시각화
- [ ] **약력학(PD) 시뮬레이터**
  - 용량-반응 곡선 (Emax 모델)
  - EC50, Emax 파라미터 조절
  - 효능제/길항제 상호작용 시각화
- [ ] **특수 PK 시뮬레이션**
  - 신부전/간부전 시 약물 동태 변화
  - 노인/소아 약동학 비교
  - 약물-약물 상호작용 (CYP450 기반)

#### Sprint 17–18: AI 기능 고도화 (2주)
- [ ] **RAG (Retrieval-Augmented Generation)**
  - Katzung 교재 텍스트 벡터화 (pgvector)
  - 질문 관련 챕터 자동 검색 후 컨텍스트로 제공
  - 답변의 정확도 및 교재 근거 강화
- [ ] 챕터별 AI 퀴즈 자동 생성
- [ ] AI 오답 분석 & 맞춤 학습 경로 제안

#### Sprint 19–20: 협업 & 소셜 기능 (2주)
- [ ] 노트 공유 기능 (링크 공유, 공개/비공개 설정)
- [ ] 커뮤니티 플래시카드 덱 (다른 사용자 카드 가져오기)
- [ ] 다크 모드 지원 (DESIGN_RULES.md 8번 항목 참조)
- [ ] 모바일 앱 고려 (React Native 또는 PWA)

**Phase 3 완료 기준:**
- 인터랙티브 시뮬레이션으로 PK/PD 개념을 직접 실험하고, RAG 기반 AI가 교재 근거를 제시하며 답변함

---

## 4. 데이터베이스 스키마

### 4.1 전체 ERD 개요

```
users ──< notes ──< review_cards ──< review_logs
  │
  └──< user_chapter_progress
```

### 4.2 테이블 상세 정의

```sql
-- ============================================
-- 1. 사용자 (Supabase Auth와 연동)
-- ============================================
CREATE TABLE users (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id      UUID UNIQUE NOT NULL,   -- Supabase auth.users.id
    email        VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 2. 챕터 (정적 콘텐츠 메타데이터)
-- ============================================
CREATE TABLE chapters (
    id           SERIAL PRIMARY KEY,
    number       INTEGER UNIQUE NOT NULL,   -- Katzung 챕터 번호
    title_ko     VARCHAR(200) NOT NULL,     -- 한국어 제목
    category     VARCHAR(100),             -- 예: '자율신경계', '심혈관계'
    content_path VARCHAR(300),             -- Markdown 파일 경로
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- 3. 개인 노트
-- ============================================
CREATE TABLE notes (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id   INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    title        VARCHAR(300) NOT NULL,
    content      TEXT NOT NULL,            -- 저장된 AI 답변 또는 요약 텍스트
    source_type  VARCHAR(20) NOT NULL      -- 'ai_chat' | 'chapter_summary' | 'manual'
                 CHECK (source_type IN ('ai_chat', 'chapter_summary', 'manual')),
    tags         TEXT[],                   -- 예: {'β-차단제', '고혈압', '부작용'}
    is_public    BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notes_user_id ON notes(user_id);
CREATE INDEX idx_notes_tags    ON notes USING GIN(tags);

-- ============================================
-- 4. 복습 카드 (간격 반복 시스템 핵심)
-- ============================================
CREATE TABLE review_cards (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note_id       UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,

    -- 카드 내용
    front         TEXT NOT NULL,           -- 질문 면
    back          TEXT NOT NULL,           -- 답변 면

    -- SM-2 알고리즘 파라미터
    easiness      FLOAT DEFAULT 2.5,       -- EF (Easiness Factor), 최소 1.3
    interval      INTEGER DEFAULT 1,       -- 다음 복습까지 일수
    repetitions   INTEGER DEFAULT 0,       -- 연속 성공 복습 횟수

    -- 스케줄링
    due_date      TIMESTAMPTZ DEFAULT NOW(),  -- 다음 복습 예정 시각
    last_reviewed TIMESTAMPTZ,

    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_review_cards_user_due
    ON review_cards(user_id, due_date)
    WHERE is_active = TRUE;

-- ============================================
-- 5. 복습 기록 (SM-2 계산 및 통계용)
-- ============================================
CREATE TABLE review_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id     UUID NOT NULL REFERENCES review_cards(id) ON DELETE CASCADE,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- 복습 결과
    quality     SMALLINT NOT NULL          -- SM-2 품질 점수 (0~5)
                CHECK (quality BETWEEN 0 AND 5),
    -- 복습 전 상태 스냅샷 (분석용)
    prev_easiness   FLOAT,
    prev_interval   INTEGER,
    -- 복습 후 새 값
    new_easiness    FLOAT,
    new_interval    INTEGER,
    next_due_date   TIMESTAMPTZ,

    reviewed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_review_logs_card_id   ON review_logs(card_id);
CREATE INDEX idx_review_logs_user_date ON review_logs(user_id, reviewed_at DESC);

-- ============================================
-- 6. 챕터 학습 진도
-- ============================================
CREATE TABLE user_chapter_progress (
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id    INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    is_completed  BOOLEAN DEFAULT FALSE,
    last_visited  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, chapter_id)
);
```

### 4.3 SM-2 데이터 흐름

```
사용자가 복습 카드 평가
        │
        ▼
review_logs에 결과 INSERT
(quality, prev_*, new_*, next_due_date)
        │
        ▼
review_cards UPDATE
(easiness, interval, repetitions, due_date)
        │
        ▼
다음 복습 시 due_date <= NOW() 조건으로 카드 조회
```

### 4.4 핵심 쿼리 예시

```sql
-- 오늘 복습할 카드 조회
SELECT rc.*, n.title as note_title, n.chapter_id
FROM review_cards rc
JOIN notes n ON rc.note_id = n.id
WHERE rc.user_id = $1
  AND rc.due_date <= NOW()
  AND rc.is_active = TRUE
ORDER BY rc.due_date ASC
LIMIT 50;

-- 사용자 학습 통계
SELECT
    COUNT(*) FILTER (WHERE reviewed_at::date = CURRENT_DATE) AS today_reviews,
    COUNT(*) FILTER (WHERE quality >= 4)::float / NULLIF(COUNT(*), 0) AS accuracy,
    COUNT(DISTINCT reviewed_at::date) AS total_study_days
FROM review_logs
WHERE user_id = $1;

-- 취약 개념 카드 (낮은 easiness)
SELECT rc.*, n.title
FROM review_cards rc
JOIN notes n ON rc.note_id = n.id
WHERE rc.user_id = $1
  AND rc.easiness < 1.8
ORDER BY rc.easiness ASC
LIMIT 10;
```

---

## 5. LLM 통합 전략

### 5.1 System Prompt 설계

```python
SYSTEM_PROMPT = """
당신은 Katzung 약리학 교재를 전문으로 하는 한국어 약리학 튜터입니다.

[역할]
- 의대생과 약대생이 약리학 개념을 이해하도록 돕습니다.
- Katzung 교재의 내용을 기반으로 정확하고 체계적인 설명을 제공합니다.

[언어 규칙]
- 모든 답변은 반드시 한국어로 작성합니다.
- 의학 용어는 한국어 명칭을 주로 사용하고, 필요 시 괄호 안에 영문을 병기합니다.
  예: 베타 차단제(beta-blocker), 반감기(half-life)

[답변 형식]
- 복잡한 개념은 단계적으로 설명합니다.
- 임상적 연관성을 반드시 포함합니다.
- 핵심 사항은 볼드체로 강조합니다.
- 적절한 경우 표나 목록을 활용합니다.

[안전 지침]
- 실제 환자 치료를 위한 처방 조언은 제공하지 않습니다.
- 교육 목적의 정보임을 명시합니다.
"""
```

### 5.2 스트리밍 구현 (FastAPI + SSE)

```python
# backend/api/chat.py
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import anthropic

router = APIRouter()
client = anthropic.Anthropic()

@router.post("/api/chat")
async def chat_stream(request: ChatRequest):
    async def generate():
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            messages=request.messages
        ) as stream:
            for text in stream.text_stream:
                yield f"data: {json.dumps({'text': text})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
```

### 5.3 Phase 3 RAG 구조 (pgvector)

```sql
-- pgvector 확장 설치 (Supabase에서 활성화)
CREATE EXTENSION IF NOT EXISTS vector;

-- 챕터 내용 임베딩 저장
CREATE TABLE chapter_embeddings (
    id           SERIAL PRIMARY KEY,
    chapter_id   INTEGER REFERENCES chapters(id),
    chunk_index  INTEGER,
    chunk_text   TEXT,
    embedding    vector(1536),  -- text-embedding-3-small 차원
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- 유사도 검색 (코사인 유사도)
SELECT chunk_text, 1 - (embedding <=> $1) AS similarity
FROM chapter_embeddings
ORDER BY embedding <=> $1
LIMIT 5;
```

---

## 6. 폴더 구조

```
Mednote/
├── DESIGN_RULES.md          ← UI/UX 디자인 규칙
├── ARCHITECTURE_AND_ROADMAP.md
├── docker-compose.yml
│
├── frontend/                ← React + TypeScript + Vite
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/          ← 공통 컴포넌트 (Button, Card, Badge)
│   │   │   ├── chat/        ← 챗봇 UI
│   │   │   ├── chapters/    ← 챕터 목록/상세
│   │   │   ├── notes/       ← 노트 관리
│   │   │   ├── review/      ← 복습 카드 UI
│   │   │   └── visualizations/  ← PK/PD 시뮬레이터
│   │   ├── pages/
│   │   │   ├── HomePage.tsx
│   │   │   ├── ChaptersPage.tsx
│   │   │   ├── ChapterDetailPage.tsx
│   │   │   ├── ChatPage.tsx
│   │   │   ├── NotesPage.tsx
│   │   │   └── ReviewPage.tsx
│   │   ├── hooks/           ← 커스텀 훅
│   │   ├── stores/          ← Zustand 상태 관리
│   │   ├── lib/
│   │   │   ├── supabase.ts  ← Supabase 클라이언트
│   │   │   └── api.ts       ← API 호출 유틸
│   │   └── types/           ← TypeScript 타입 정의
│   ├── tailwind.config.ts   ← DESIGN_RULES 기반 Tailwind 설정
│   └── package.json
│
├── backend/                 ← FastAPI (Python)
│   ├── api/
│   │   ├── chat.py          ← LLM 스트리밍 엔드포인트
│   │   ├── notes.py         ← 노트 CRUD
│   │   └── review.py        ← SRS 스케줄링
│   ├── algorithms/
│   │   └── sm2.py           ← SM-2 알고리즘 구현
│   ├── db/
│   │   └── schema.sql       ← DB 스키마
│   ├── main.py
│   └── requirements.txt
│
└── .github/
    └── workflows/
        └── deploy.yml       ← CI/CD (GitHub Actions)
```

---

## 7. 주요 마일스톤 요약

| 마일스톤 | 목표 | 완료 기준 |
|---------|------|---------|
| **M1** Phase 1 완료 | 읽기 → 질문 → 저장 루프 | 로그인 후 챕터 읽기, AI 질문, 노트 저장 가능 |
| **M2** Phase 2 완료 | 스마트 복습 시스템 | SM-2 기반 복습 알림 및 카드 평가 작동 |
| **M3** Phase 3 완료 | 고급 시뮬레이션 & RAG | PK/PD 인터랙티브 시뮬레이터 + RAG 챗봇 |

---

*최종 업데이트: 2026-03-08*
*모든 UI 작업 시 반드시 DESIGN_RULES.md를 참조하세요.*

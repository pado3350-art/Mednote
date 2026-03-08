-- ============================================================
-- Mednote PostgreSQL 스키마 (Supabase 적용용)
-- ARCHITECTURE_AND_ROADMAP.md Section 4 참조
-- ============================================================

-- pgvector (Phase 3 RAG용 — Supabase에서 활성화 필요)
-- CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- 1. 사용자 (Supabase Auth와 연동)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    auth_id      UUID UNIQUE NOT NULL,
    email        VARCHAR(255) UNIQUE NOT NULL,
    display_name VARCHAR(100),
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 2. 챕터 (정적 콘텐츠 메타데이터)
-- ============================================================
CREATE TABLE IF NOT EXISTS chapters (
    id           SERIAL PRIMARY KEY,
    number       INTEGER UNIQUE NOT NULL,
    title_ko     VARCHAR(200) NOT NULL,
    category     VARCHAR(100),
    content_path VARCHAR(300),
    created_at   TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- 3. 개인 노트
-- ============================================================
CREATE TABLE IF NOT EXISTS notes (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id      UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id   INTEGER REFERENCES chapters(id) ON DELETE SET NULL,
    title        VARCHAR(300) NOT NULL,
    content      TEXT NOT NULL,
    source_type  VARCHAR(20) NOT NULL
                 CHECK (source_type IN ('ai_chat', 'chapter_summary', 'manual')),
    tags         TEXT[] DEFAULT '{}',
    is_public    BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMPTZ DEFAULT NOW(),
    updated_at   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notes_user_id ON notes(user_id);
CREATE INDEX IF NOT EXISTS idx_notes_tags    ON notes USING GIN(tags);

-- ============================================================
-- 4. 복습 카드 (SM-2 핵심 파라미터 저장)
-- ============================================================
CREATE TABLE IF NOT EXISTS review_cards (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    note_id       UUID NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    front         TEXT NOT NULL,
    back          TEXT NOT NULL,
    -- SM-2 파라미터
    easiness      FLOAT DEFAULT 2.5,
    interval      INTEGER DEFAULT 1,
    repetitions   INTEGER DEFAULT 0,
    -- 스케줄링
    due_date      TIMESTAMPTZ DEFAULT NOW(),
    last_reviewed TIMESTAMPTZ,
    is_active     BOOLEAN DEFAULT TRUE,
    created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- 오늘 복습할 카드 조회 최적화 인덱스
CREATE INDEX IF NOT EXISTS idx_review_cards_user_due
    ON review_cards(user_id, due_date)
    WHERE is_active = TRUE;

-- ============================================================
-- 5. 복습 기록 (통계 및 SM-2 히스토리)
-- ============================================================
CREATE TABLE IF NOT EXISTS review_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    card_id         UUID NOT NULL REFERENCES review_cards(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quality         SMALLINT NOT NULL CHECK (quality BETWEEN 0 AND 5),
    prev_easiness   FLOAT,
    prev_interval   INTEGER,
    new_easiness    FLOAT,
    new_interval    INTEGER,
    next_due_date   TIMESTAMPTZ,
    reviewed_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_review_logs_card_id
    ON review_logs(card_id);
CREATE INDEX IF NOT EXISTS idx_review_logs_user_date
    ON review_logs(user_id, reviewed_at DESC);

-- ============================================================
-- 6. 챕터 학습 진도
-- ============================================================
CREATE TABLE IF NOT EXISTS user_chapter_progress (
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    chapter_id    INTEGER NOT NULL REFERENCES chapters(id) ON DELETE CASCADE,
    is_completed  BOOLEAN DEFAULT FALSE,
    last_visited  TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (user_id, chapter_id)
);

-- ============================================================
-- 핵심 쿼리 예시
-- ============================================================

-- 오늘 복습할 카드
-- SELECT rc.*, n.title AS note_title
-- FROM review_cards rc
-- JOIN notes n ON rc.note_id = n.id
-- WHERE rc.user_id = $1
--   AND rc.due_date <= NOW()
--   AND rc.is_active = TRUE
-- ORDER BY rc.due_date ASC
-- LIMIT 50;

-- 사용자 학습 통계
-- SELECT
--     COUNT(*) FILTER (WHERE reviewed_at::date = CURRENT_DATE) AS today_reviews,
--     COUNT(*) FILTER (WHERE quality >= 4)::float / NULLIF(COUNT(*), 0) AS accuracy,
--     COUNT(DISTINCT reviewed_at::date) AS total_study_days
-- FROM review_logs
-- WHERE user_id = $1;

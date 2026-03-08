// ============================================================
// 공통 타입 정의
// ============================================================

export interface User {
  id: string
  email: string
  displayName?: string
  createdAt: string
}

export interface Chapter {
  id: number
  number: number
  titleKo: string
  category: string
  contentPath?: string
}

export interface Note {
  id: string
  userId: string
  chapterId?: number
  title: string
  content: string
  sourceType: 'ai_chat' | 'chapter_summary' | 'manual'
  tags: string[]
  isPublic: boolean
  createdAt: string
  updatedAt: string
}

export interface ReviewCard {
  id: string
  userId: string
  noteId: string
  front: string
  back: string
  easiness: number
  interval: number
  repetitions: number
  dueDate: string
  lastReviewed?: string
  isActive: boolean
  createdAt: string
  // 조인 데이터
  noteTitle?: string
}

export interface ReviewLog {
  id: string
  cardId: string
  userId: string
  quality: 0 | 1 | 2 | 3 | 4 | 5
  prevEasiness: number
  prevInterval: number
  newEasiness: number
  newInterval: number
  nextDueDate: string
  reviewedAt: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface ReviewStats {
  todayReviews: number
  accuracy: number
  totalStudyDays: number
  dueToday: number
}

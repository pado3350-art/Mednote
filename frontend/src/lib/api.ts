/**
 * API 클라이언트
 * - REST: axios 기반 CRUD
 * - SSE: fetch 기반 스트리밍 (챗봇)
 */

import axios from 'axios'
import type { Note, ReviewCard, ReviewStats } from '@/types'

const BASE = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

export const api = axios.create({
  baseURL: BASE,
  headers: { 'Content-Type': 'application/json' },
})

// ── 노트 API ───────────────────────────────────────────────────────

export const notesApi = {
  list: (userId = 'demo-user') =>
    api.get<Note[]>('/api/notes', { params: { user_id: userId } }).then((r) => r.data),

  create: (data: {
    title: string
    content: string
    source_type: Note['sourceType']
    chapter_id?: number
    tags?: string[]
  }, userId = 'demo-user') =>
    api.post<Note>('/api/notes', data, { params: { user_id: userId } }).then((r) => r.data),

  update: (id: string, data: { title?: string; content?: string; tags?: string[]; is_public?: boolean }) =>
    api.patch<Note>(`/api/notes/${id}`, data).then((r) => r.data),

  delete: (id: string) =>
    api.delete(`/api/notes/${id}`),
}

// ── 복습 카드 API ──────────────────────────────────────────────────

export const reviewApi = {
  getDue: (userId = 'demo-user') =>
    api.get<ReviewCard[]>('/api/review/due', { params: { user_id: userId } }).then((r) => r.data),

  createCard: (data: { note_id: string; front: string; back: string }, userId = 'demo-user') =>
    api.post<ReviewCard>('/api/review/cards', data, { params: { user_id: userId } }).then((r) => r.data),

  submitResult: (cardId: string, quality: number, userId = 'demo-user') =>
    api.post('/api/review/result', { card_id: cardId, quality }, { params: { user_id: userId } }).then((r) => r.data),

  getStats: (userId = 'demo-user') =>
    api.get<ReviewStats>('/api/review/stats', { params: { user_id: userId } }).then((r) => r.data),
}

// ── SSE 스트리밍 챗봇 ──────────────────────────────────────────────

export interface StreamMessage {
  text?: string
  error?: string
  done?: boolean
}

/**
 * Claude API SSE 스트리밍 채팅
 * @param messages 대화 이력 (role + content)
 * @param onChunk  텍스트 청크를 받을 때마다 호출되는 콜백
 * @param onDone   스트리밍 완료 콜백
 * @param onError  에러 콜백
 * @returns AbortController — 스트리밍 취소 시 controller.abort() 호출
 */
export function streamChat(
  messages: { role: string; content: string }[],
  onChunk: (text: string) => void,
  onDone: () => void,
  onError: (err: string) => void,
): AbortController {
  const controller = new AbortController()

  const run = async () => {
    try {
      const res = await fetch(`${BASE}/api/chat/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ messages }),
        signal: controller.signal,
      })

      if (!res.ok) {
        onError(`서버 오류: ${res.status}`)
        return
      }

      const reader = res.body?.getReader()
      if (!reader) { onError('스트림을 읽을 수 없습니다.'); return }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          const data = line.slice(6).trim()

          if (data === '[DONE]') {
            onDone()
            return
          }

          try {
            const parsed: StreamMessage = JSON.parse(data)
            if (parsed.error) { onError(parsed.error); return }
            if (parsed.text)  { onChunk(parsed.text) }
          } catch {
            // JSON 파싱 실패 무시
          }
        }
      }
      onDone()
    } catch (err) {
      if ((err as Error).name !== 'AbortError') {
        onError('연결이 끊어졌습니다. 다시 시도해주세요.')
      }
    }
  }

  run()
  return controller
}

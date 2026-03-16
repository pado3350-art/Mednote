import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { ChatMessage } from '@/types'

interface ChatState {
  messages: ChatMessage[]
  isStreaming: boolean
  streamingText: string   // 현재 스트리밍 중인 텍스트 (누적)

  addUserMessage: (content: string) => ChatMessage
  startStreaming: () => void
  appendChunk: (chunk: string) => void
  finalizeAssistantMessage: () => ChatMessage
  setStreaming: (v: boolean) => void
  clearMessages: () => void
}

const WELCOME: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content:
    '안녕하세요! 저는 Katzung 약리학 전문 AI 튜터입니다.\n\n' +
    '약리학에 관한 어떤 질문이든 한국어로 정확하게 답변해 드립니다. ' +
    '궁금한 약물, 기전, 부작용, 임상 적용 등 무엇이든 질문하세요.',
  timestamp: new Date().toISOString(),
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      messages: [WELCOME],
      isStreaming: false,
      streamingText: '',

      addUserMessage: (content) => {
        const msg: ChatMessage = {
          id: `user-${Date.now()}`,
          role: 'user',
          content,
          timestamp: new Date().toISOString(),
        }
        set((s) => ({ messages: [...s.messages, msg] }))
        return msg
      },

      startStreaming: () => {
        set({ isStreaming: true, streamingText: '' })
      },

      appendChunk: (chunk) => {
        set((s) => ({ streamingText: s.streamingText + chunk }))
      },

      finalizeAssistantMessage: () => {
        const { streamingText } = get()
        const msg: ChatMessage = {
          id: `assistant-${Date.now()}`,
          role: 'assistant',
          content: streamingText,
          timestamp: new Date().toISOString(),
        }
        set((s) => ({
          messages: [...s.messages, msg],
          isStreaming: false,
          streamingText: '',
        }))
        return msg
      },

      setStreaming: (v) => set({ isStreaming: v }),

      clearMessages: () =>
        set({ messages: [WELCOME], isStreaming: false, streamingText: '' }),
    }),
    {
      name: 'mednote-chat',
      // 세션 초기화 후에도 대화 이력 유지 (최근 50개까지)
      partialize: (s) => ({ messages: s.messages.slice(-50) }),
    },
  ),
)

import { useState, useRef, useEffect } from 'react'
import { Button, Input, Spinner } from '@/components/ui'
import { cn } from '@/lib/cn'
import type { ChatMessage } from '@/types'

// Phase 1: 로컬 상태 기반 챗봇 (Phase 2에서 API SSE 스트리밍 연동)
const WELCOME_MESSAGE: ChatMessage = {
  id: 'welcome',
  role: 'assistant',
  content: '안녕하세요! 저는 Katzung 약리학 전문 AI 튜터입니다. 약리학에 관한 어떤 질문이든 한국어로 답변해 드립니다. 무엇이 궁금하신가요?',
  timestamp: new Date().toISOString(),
}

const SUGGESTED_QUESTIONS = [
  'β-차단제의 작용 메커니즘을 설명해주세요',
  'ACE 억제제와 ARB의 차이점은?',
  '약동학에서 반감기(t½)란 무엇인가요?',
  '스타틴 계열 약물의 부작용은?',
]

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setIsLoading(true)

    // Phase 1 플레이스홀더: 실제 API 연동 전 모의 응답
    // Phase 2에서 /api/chat SSE 스트리밍으로 교체 예정
    await new Promise((r) => setTimeout(r, 1200))
    const assistantMsg: ChatMessage = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `"${text}"에 대한 답변입니다.\n\n⚠️ 현재 Phase 1 개발 중입니다. Phase 2에서 실제 Claude API (claude-sonnet-4-6)와 연동하여 정확한 약리학 답변을 제공합니다.\n\n**연동 예정 기능:**\n- Anthropic Claude API SSE 스트리밍\n- 한국어 전용 System Prompt\n- 노트 저장 버튼`,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, assistantMsg])
    setIsLoading(false)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(input)
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col h-[calc(100vh-8rem)]">
      <div className="mb-4">
        <h1 className="text-2xl font-bold text-[#111827]">AI 약리학 챗봇</h1>
        <p className="text-sm text-[#6B7280]">Katzung 교재 기반 전문 약리학 튜터 · 한국어 전용</p>
      </div>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={cn('flex', msg.role === 'user' ? 'justify-end' : 'justify-start')}
          >
            <div
              className={cn(
                'max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed',
                msg.role === 'user'
                  // DESIGN_RULES: 파란 계열 배경 + 진한 파란 텍스트 (흰 배경 아닐 때)
                  ? 'bg-[#EFF6FF] text-[#1E40AF] rounded-br-sm'
                  : 'bg-[#F3F4F6] text-[#111827] rounded-bl-sm',
              )}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              {msg.role === 'assistant' && (
                <div className="mt-2 pt-2 border-t border-[#E5E7EB] flex gap-2">
                  <button className="text-xs text-[#2563EB] hover:underline">
                    📝 노트에 저장
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-[#F3F4F6] rounded-2xl rounded-bl-sm px-4 py-3 flex items-center gap-2">
              <Spinner size="sm" />
              <span className="text-sm text-[#6B7280]">답변 작성 중...</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* 추천 질문 */}
      {messages.length === 1 && (
        <div className="mb-3 flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="text-xs px-3 py-1.5 bg-white border border-[#E5E7EB] rounded-full text-[#374151] hover:border-[#2563EB] hover:text-[#2563EB] transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* 입력 폼 */}
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1">
          <Input
            placeholder="약리학에 대해 무엇이든 질문하세요..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isLoading}
          />
        </div>
        <Button type="submit" disabled={!input.trim() || isLoading} loading={isLoading}>
          전송
        </Button>
      </form>
    </div>
  )
}

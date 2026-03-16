import { useRef, useEffect, useCallback } from 'react'
import { Button, Input, Spinner } from '@/components/ui'
import { cn } from '@/lib/cn'
import { streamChat } from '@/lib/api'
import { useChatStore } from '@/stores/chatStore'
import { useNotesStore } from '@/stores/notesStore'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

const SUGGESTED_QUESTIONS = [
  'β-차단제의 작용 메커니즘을 설명해주세요',
  'ACE 억제제와 ARB의 차이점은?',
  '약동학에서 반감기(t½)란 무엇인가요?',
  '스타틴 계열 약물의 부작용과 금기증은?',
]

export default function ChatPage() {
  const {
    messages,
    isStreaming,
    streamingText,
    addUserMessage,
    startStreaming,
    appendChunk,
    finalizeAssistantMessage,
    setStreaming,
    clearMessages,
  } = useChatStore()

  const { openSaveModal } = useNotesStore()

  const inputRef = useRef<HTMLInputElement>(null)
  const bottomRef = useRef<HTMLDivElement>(null)
  const abortRef = useRef<AbortController | null>(null)

  // 새 메시지가 추가될 때마다 스크롤
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingText])

  const sendMessage = useCallback((text: string) => {
    const trimmed = text.trim()
    if (!trimmed || isStreaming) return

    addUserMessage(trimmed)
    startStreaming()

    // 대화 이력 구성 (welcome 메시지 제외)
    const history = messages
      .filter((m) => m.id !== 'welcome')
      .map((m) => ({ role: m.role, content: m.content }))
    history.push({ role: 'user', content: trimmed })

    abortRef.current = streamChat(
      history,
      appendChunk,
      finalizeAssistantMessage,
      (err) => {
        // 에러 시 에러 메시지를 어시스턴트 메시지로 추가
        appendChunk(`⚠️ 오류가 발생했습니다: ${err}\n\n백엔드 서버가 실행 중인지 확인하세요.`)
        finalizeAssistantMessage()
        setStreaming(false)
      },
    )
  }, [messages, isStreaming, addUserMessage, startStreaming, appendChunk, finalizeAssistantMessage, setStreaming])

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const val = inputRef.current?.value ?? ''
    if (inputRef.current) inputRef.current.value = ''
    sendMessage(val)
  }

  const handleStop = () => {
    abortRef.current?.abort()
    finalizeAssistantMessage()
  }

  return (
    <div className="max-w-3xl mx-auto flex flex-col" style={{ height: 'calc(100vh - 8rem)' }}>
      {/* 헤더 */}
      <div className="flex items-start justify-between mb-4 flex-wrap gap-2">
        <div>
          <h1 className="text-2xl font-bold text-[#111827]">AI 약리학 챗봇</h1>
          <p className="text-sm text-[#6B7280]">
            Katzung 교재 기반 전문 약리학 튜터 · Claude {import.meta.env.VITE_CLAUDE_MODEL ?? 'claude-sonnet-4-6'} · 한국어 전용
          </p>
        </div>
        <Button variant="ghost" size="sm" onClick={clearMessages}>
          대화 초기화
        </Button>
      </div>

      {/* 메시지 목록 */}
      <div className="flex-1 overflow-y-auto space-y-4 pb-2 pr-1">
        {messages.map((msg) => (
          <MessageBubble
            key={msg.id}
            role={msg.role}
            content={msg.content}
            onSave={
              msg.role === 'assistant' && msg.id !== 'welcome'
                ? () =>
                    openSaveModal({
                      content: msg.content,
                      sourceType: 'ai_chat',
                      suggestedTitle: msg.content.split('\n')[0].replace(/^#+\s*/, '').slice(0, 60),
                    })
                : undefined
            }
          />
        ))}

        {/* 스트리밍 중인 AI 응답 */}
        {isStreaming && (
          <div className="flex justify-start">
            <div className="max-w-[80%] bg-[#F3F4F6] text-[#111827] rounded-2xl rounded-bl-sm px-4 py-3">
              {streamingText ? (
                <MarkdownContent content={streamingText} />
              ) : (
                <div className="flex items-center gap-2 text-sm text-[#6B7280]">
                  <Spinner size="sm" />
                  <span>답변 작성 중...</span>
                </div>
              )}
              {/* 깜빡이는 커서 */}
              {streamingText && (
                <span className="inline-block w-0.5 h-4 bg-[#2563EB] ml-0.5 animate-pulse" />
              )}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* 추천 질문 (환영 메시지만 있을 때) */}
      {messages.length === 1 && !isStreaming && (
        <div className="mb-3 flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map((q) => (
            <button
              key={q}
              onClick={() => sendMessage(q)}
              className="text-xs px-3 py-1.5 bg-white border border-[#E5E7EB] rounded-full
                         text-[#374151] hover:border-[#2563EB] hover:text-[#2563EB] transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      )}

      {/* 입력 폼 */}
      <form onSubmit={handleSubmit} className="flex gap-2 pt-3 border-t border-[#E5E7EB]">
        <div className="flex-1">
          <Input
            ref={inputRef}
            placeholder="약리학에 대해 무엇이든 질문하세요..."
            disabled={isStreaming}
            autoFocus
          />
        </div>
        {isStreaming ? (
          <Button type="button" variant="danger" onClick={handleStop}>
            중단
          </Button>
        ) : (
          <Button type="submit">전송</Button>
        )}
      </form>
    </div>
  )
}

// ── 말풍선 컴포넌트 ────────────────────────────────────────────────

function MessageBubble({
  role,
  content,
  onSave,
}: {
  role: 'user' | 'assistant'
  content: string
  onSave?: () => void
}) {
  if (role === 'user') {
    return (
      <div className="flex justify-end">
        {/* DESIGN_RULES: 파란 계열 배경 + 진한 파란 텍스트 */}
        <div className="max-w-[80%] bg-[#EFF6FF] text-[#1E40AF] rounded-2xl rounded-br-sm px-4 py-3 text-sm leading-relaxed">
          {content}
        </div>
      </div>
    )
  }

  return (
    <div className="flex justify-start">
      <div className="max-w-[80%] bg-[#F3F4F6] text-[#111827] rounded-2xl rounded-bl-sm px-4 py-3">
        <MarkdownContent content={content} />

        {onSave && (
          <div className="mt-3 pt-2.5 border-t border-[#E5E7EB] flex items-center gap-3">
            <button
              onClick={onSave}
              className="flex items-center gap-1.5 text-xs text-[#2563EB] hover:text-[#1D4ED8] font-medium transition-colors"
            >
              <span>📝</span> 노트에 저장
            </button>
            <button
              onClick={() => navigator.clipboard?.writeText(content)}
              className="text-xs text-[#6B7280] hover:text-[#374151] transition-colors"
            >
              복사
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// ── 마크다운 인라인 렌더러 ─────────────────────────────────────────
// 채팅 말풍선 안의 AI 응답을 마크다운으로 렌더링

function MarkdownContent({ content }: { content: string }) {
  return (
    <div className={cn('text-sm leading-relaxed')}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
          strong: ({ children }) => <strong className="font-semibold text-[#111827]">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          h1: ({ children }) => <p className="font-bold text-base mb-2 text-[#111827]">{children}</p>,
          h2: ({ children }) => <p className="font-semibold text-[#111827] mb-1.5 mt-3">{children}</p>,
          h3: ({ children }) => <p className="font-semibold text-[#374151] mb-1 mt-2">{children}</p>,
          ul: ({ children }) => <ul className="mb-2 space-y-1">{children}</ul>,
          ol: ({ children }) => <ol className="mb-2 space-y-1 list-decimal list-inside">{children}</ol>,
          li: ({ children }) => (
            <li className="flex items-start gap-1.5">
              <span className="mt-1.5 w-1 h-1 rounded-full bg-[#2563EB] flex-shrink-0" />
              <span>{children}</span>
            </li>
          ),
          code: ({ children, className }) => {
            const isBlock = !!className
            if (isBlock) {
              return (
                <pre className="bg-[#1E293B] text-[#E2E8F0] rounded-lg p-3 overflow-x-auto text-xs font-mono my-2">
                  <code>{children}</code>
                </pre>
              )
            }
            return (
              <code className="bg-[#E5E7EB] text-[#DC2626] px-1 py-0.5 rounded text-xs font-mono">
                {children}
              </code>
            )
          },
          blockquote: ({ children }) => (
            <blockquote className="border-l-2 border-[#2563EB] pl-3 my-2 text-[#374151] italic">
              {children}
            </blockquote>
          ),
          table: ({ children }) => (
            <div className="overflow-x-auto my-2">
              <table className="w-full text-xs border-collapse">{children}</table>
            </div>
          ),
          // DESIGN_RULES: 파란 헤더 + 흰 텍스트
          thead: ({ children }) => <thead className="bg-[#2563EB] text-white">{children}</thead>,
          th: ({ children }) => <th className="px-2 py-1.5 text-left font-semibold text-white">{children}</th>,
          tbody: ({ children }) => <tbody className="divide-y divide-[#E5E7EB]">{children}</tbody>,
          tr: ({ children }) => <tr className="hover:bg-[#F9FAFB]">{children}</tr>,
          td: ({ children }) => <td className="px-2 py-1.5 text-[#374151]">{children}</td>,
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

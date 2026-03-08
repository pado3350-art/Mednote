import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { cn } from '@/lib/cn'

interface MarkdownRendererProps {
  content: string
  className?: string
}

export function MarkdownRenderer({ content, className }: MarkdownRendererProps) {
  return (
    <div className={cn('prose-mednote', className)}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          // 제목
          h1: ({ children }) => (
            <h1 className="text-3xl font-bold text-[#111827] mt-0 mb-6 leading-tight">{children}</h1>
          ),
          h2: ({ children }) => (
            <h2 className="text-xl font-semibold text-[#111827] mt-8 mb-3 pb-2 border-b border-[#E5E7EB]">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="text-lg font-semibold text-[#374151] mt-6 mb-2">{children}</h3>
          ),

          // 단락
          p: ({ children }) => (
            <p className="text-[#374151] leading-[1.85] mb-4">{children}</p>
          ),

          // 강조
          strong: ({ children }) => (
            <strong className="font-semibold text-[#111827]">{children}</strong>
          ),
          em: ({ children }) => (
            <em className="italic text-[#374151]">{children}</em>
          ),

          // 목록 — DESIGN_RULES: 검정 배경 없음
          ul: ({ children }) => (
            <ul className="list-none pl-0 mb-4 space-y-1.5">{children}</ul>
          ),
          ol: ({ children }) => (
            <ol className="list-decimal list-inside mb-4 space-y-1.5 text-[#374151]">{children}</ol>
          ),
          li: ({ children }) => (
            <li className="flex items-start gap-2 text-[#374151] leading-relaxed">
              <span className="mt-2 w-1.5 h-1.5 rounded-full bg-[#2563EB] flex-shrink-0" />
              <span>{children}</span>
            </li>
          ),

          // 표 — DESIGN_RULES: 파란 헤더 + 흰 텍스트
          table: ({ children }) => (
            <div className="overflow-x-auto mb-6 rounded-xl border border-[#E5E7EB]">
              <table className="w-full text-sm">{children}</table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-[#2563EB] text-white">{children}</thead>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left font-semibold text-white">{children}</th>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-[#E5E7EB]">{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr className="hover:bg-[#F9FAFB] transition-colors">{children}</tr>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-[#374151]">{children}</td>
          ),

          // 코드
          code: ({ children, className }) => {
            const isBlock = className?.startsWith('language-')
            if (isBlock) {
              return (
                <div className="mb-4">
                  <pre className="bg-[#1E293B] text-[#E2E8F0] rounded-xl p-4 overflow-x-auto text-sm font-mono leading-relaxed">
                    <code>{children}</code>
                  </pre>
                </div>
              )
            }
            return (
              <code className="bg-[#F1F5F9] text-[#DC2626] px-1.5 py-0.5 rounded text-sm font-mono">
                {children}
              </code>
            )
          },

          // 인용구 — 파란 계열 강조 (경고/팁)
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-[#2563EB] bg-[#EFF6FF] pl-4 pr-4 py-3 rounded-r-xl mb-4 text-[#1E40AF]">
              {children}
            </blockquote>
          ),

          // 구분선
          hr: () => <hr className="my-8 border-[#E5E7EB]" />,

          // 링크
          a: ({ href, children }) => (
            <a href={href} className="text-[#2563EB] hover:text-[#1D4ED8] underline underline-offset-2">
              {children}
            </a>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}

import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Button, Badge, Spinner } from '@/components/ui'
import { MarkdownRenderer } from '@/components/chapters/MarkdownRenderer'
import { PKSimulator } from '@/components/visualizations/PKSimulator'
import { PDSimulator } from '@/components/visualizations/PDSimulator'
import { CHAPTERS, CHAPTER_CONTENT } from '@/content/chapters'

export default function ChapterDetailPage() {
  const { id } = useParams()
  const chapterId = parseInt(id ?? '0', 10)

  const chapter = CHAPTERS.find((c) => c.id === chapterId)
  const [content, setContent] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    setContent(null)

    const loader = CHAPTER_CONTENT[chapterId]
    if (loader) {
      loader()
        .then((mod) => setContent(mod.default))
        .catch(() => setContent(null))
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [chapterId])

  if (!chapter) {
    return (
      <div className="text-center py-20">
        <p className="text-[#6B7280]">챕터를 찾을 수 없습니다.</p>
        <Link to="/chapters" className="text-[#2563EB] hover:underline mt-2 inline-block">
          챕터 목록으로 돌아가기
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* 브레드크럼 */}
      <nav className="text-sm text-[#6B7280]">
        <Link to="/chapters" className="hover:text-[#2563EB]">챕터 목록</Link>
        <span className="mx-2">›</span>
        <span className="text-[#111827]">Chapter {chapter.number}</span>
      </nav>

      {/* 챕터 헤더 */}
      <div className="space-y-3">
        <div className="flex items-center gap-3 flex-wrap">
          <Badge variant="primary">Chapter {chapter.number}</Badge>
          <Badge variant="default">{chapter.category}</Badge>
          {chapter.hasPkSim && <Badge variant="success">PK 시뮬레이터</Badge>}
          {chapter.hasPdSim && <Badge variant="success">PD 시뮬레이터</Badge>}
        </div>
        <h1 className="text-3xl font-bold text-[#111827] leading-tight">{chapter.titleKo}</h1>
      </div>

      {/* 빠른 액션 */}
      <div className="flex gap-3 flex-wrap">
        <Button variant="secondary" size="sm" asChild>
          <Link to="/chat">🤖 AI에게 질문하기</Link>
        </Button>
        <Button variant="ghost" size="sm">
          📝 챕터 요약 저장
        </Button>
      </div>

      {/* PK 시뮬레이터 (Chapter 2) */}
      {chapter.hasPkSim && (
        <section>
          <PKSimulator />
        </section>
      )}

      {/* PD 시뮬레이터 (Chapter 1) */}
      {chapter.hasPdSim && (
        <section>
          <PDSimulator />
        </section>
      )}

      {/* 챕터 내용 */}
      <section>
        {loading ? (
          <div className="flex items-center justify-center py-24">
            <div className="text-center space-y-3">
              <Spinner size="lg" />
              <p className="text-sm text-[#6B7280]">챕터 내용을 불러오는 중...</p>
            </div>
          </div>
        ) : content ? (
          <div className="bg-white border border-[#E5E7EB] rounded-2xl p-8">
            <MarkdownRenderer content={content} />
          </div>
        ) : (
          <div className="bg-white border border-[#E5E7EB] rounded-2xl p-8 space-y-5">
            <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl p-5 text-sm text-[#1E40AF]">
              <p className="font-medium mb-1">📚 콘텐츠 준비 중</p>
              <p>
                Chapter {chapter.number} "{chapter.titleKo}"의 상세 내용은 현재 준비 중입니다.
                AI 챗봇에서 이 챕터에 대한 질문을 자유롭게 할 수 있습니다.
              </p>
            </div>
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-[#111827]">주요 학습 포인트</h2>
              <ul className="space-y-2">
                {[
                  `${chapter.titleKo}의 기본 개념 이해`,
                  '주요 약물 분류와 작용 기전',
                  '임상 적용 및 부작용',
                  '약물 상호작용 주의사항',
                ].map((point) => (
                  <li key={point} className="flex items-start gap-2 text-[#374151]">
                    <span className="mt-2 w-1.5 h-1.5 rounded-full bg-[#2563EB] flex-shrink-0" />
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </section>

      {/* 하단 챕터 네비게이션 */}
      <div className="flex justify-between gap-4 pt-4 border-t border-[#E5E7EB]">
        {chapterId > 1 && (
          <Button variant="secondary" size="sm" asChild>
            <Link to={`/chapters/${chapterId - 1}`}>← 이전 챕터</Link>
          </Button>
        )}
        <span className="flex-1" />
        {chapterId < 20 && (
          <Button variant="secondary" size="sm" asChild>
            <Link to={`/chapters/${chapterId + 1}`}>다음 챕터 →</Link>
          </Button>
        )}
      </div>
    </div>
  )
}

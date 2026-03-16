import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Card, CardBody, CardHeader, CardTitle, Spinner, Badge } from '@/components/ui'
import { reviewApi } from '@/lib/api'
import type { ReviewCard, ReviewStats } from '@/types'

type ReviewPhase = 'dashboard' | 'reviewing' | 'done'

// ── 난이도 버튼 정의 ───────────────────────────────────────────────
const QUALITY_BUTTONS = [
  { quality: 0, label: '완전히 잊음', sub: '다시 (1일)', bg: 'bg-[#DC2626] hover:bg-[#B91C1C]' },
  { quality: 3, label: '어려움',     sub: '짧은 간격',  bg: 'bg-[#D97706] hover:bg-[#B45309]' },
  { quality: 4, label: '보통',       sub: '적절',       bg: 'bg-[#2563EB] hover:bg-[#1D4ED8]' },
  { quality: 5, label: '쉬움',       sub: '간격 증가',  bg: 'bg-[#16A34A] hover:bg-[#15803D]' },
]

export default function ReviewPage() {
  const [phase, setPhase] = useState<ReviewPhase>('dashboard')
  const [queue, setQueue] = useState<ReviewCard[]>([])
  const [currentIdx, setCurrentIdx] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [sessionResults, setSessionResults] = useState<{ quality: number; cardId: string }[]>([])

  const queryClient = useQueryClient()

  // 오늘 복습할 카드 조회
  const { data: dueCards = [], isLoading: isDueLoading } = useQuery({
    queryKey: ['review-due'],
    queryFn: () => reviewApi.getDue(),
  })

  // 통계 조회
  const { data: stats } = useQuery<ReviewStats>({
    queryKey: ['review-stats'],
    queryFn: () => reviewApi.getStats(),
  })

  // 복습 결과 제출
  const { mutate: submitResult } = useMutation({
    mutationFn: ({ cardId, quality }: { cardId: string; quality: number }) =>
      reviewApi.submitResult(cardId, quality),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['review-due'] })
      queryClient.invalidateQueries({ queryKey: ['review-stats'] })
    },
  })

  const startReview = () => {
    setQueue([...dueCards])
    setCurrentIdx(0)
    setShowAnswer(false)
    setSessionResults([])
    setPhase('reviewing')
  }

  const handleQuality = (quality: number) => {
    const card = queue[currentIdx]
    submitResult({ cardId: card.id, quality })
    setSessionResults((p) => [...p, { quality, cardId: card.id }])

    const next = currentIdx + 1
    if (next >= queue.length) {
      setPhase('done')
    } else {
      setCurrentIdx(next)
      setShowAnswer(false)
    }
  }

  // ── 완료 화면 ────────────────────────────────────────────────────
  if (phase === 'done') {
    const total   = sessionResults.length
    const correct = sessionResults.filter((r) => r.quality >= 4).length
    const rate    = total > 0 ? Math.round((correct / total) * 100) : 0

    return (
      <div className="max-w-lg mx-auto text-center py-16 space-y-6">
        <div className="text-6xl">{rate >= 80 ? '🎉' : rate >= 50 ? '📚' : '💪'}</div>
        <h2 className="text-2xl font-bold text-[#111827]">복습 세션 완료!</h2>

        <div className="grid grid-cols-3 gap-4">
          {[
            { label: '총 카드',  value: total,           color: 'text-[#111827]' },
            { label: '정확도',   value: `${rate}%`,      color: rate >= 70 ? 'text-[#16A34A]' : 'text-[#D97706]' },
            { label: '잘 기억', value: correct,          color: 'text-[#2563EB]' },
          ].map((s) => (
            <div key={s.label} className="bg-white border border-[#E5E7EB] rounded-xl p-4">
              <div className={`text-2xl font-bold ${s.color}`}>{s.value}</div>
              <div className="text-xs text-[#6B7280] mt-1">{s.label}</div>
            </div>
          ))}
        </div>

        {/* 세션 결과 상세 */}
        <div className="bg-[#F9FAFB] rounded-xl p-4 text-left space-y-2">
          <p className="text-sm font-semibold text-[#374151]">카드별 결과</p>
          {sessionResults.map((r, i) => {
            const btn = QUALITY_BUTTONS.find((b) => b.quality === r.quality)
            const card = queue[i]
            return (
              <div key={r.cardId} className="flex items-center justify-between text-sm">
                <span className="text-[#374151] truncate flex-1 mr-2">{card?.front ?? '—'}</span>
                <span className={`px-2 py-0.5 rounded-full text-xs text-white ${btn?.bg.split(' ')[0] ?? 'bg-gray-400'}`}>
                  {btn?.label}
                </span>
              </div>
            )
          })}
        </div>

        <div className="bg-[#F0FDF4] border border-[#BBF7D0] rounded-xl p-4 text-sm text-[#15803D]">
          <p className="font-medium">SM-2 알고리즘이 다음 복습 일정을 계산했습니다.</p>
          <p className="mt-1 text-[#16A34A]">꾸준한 복습이 장기 기억으로 이어집니다!</p>
        </div>

        <Button size="lg" onClick={() => setPhase('dashboard')}>
          대시보드로 돌아가기
        </Button>
      </div>
    )
  }

  // ── 복습 카드 화면 ───────────────────────────────────────────────
  if (phase === 'reviewing') {
    const card = queue[currentIdx]
    if (!card) return null
    const progress = Math.round((currentIdx / queue.length) * 100)

    return (
      <div className="max-w-2xl mx-auto space-y-6">
        {/* 진행 바 */}
        <div>
          <div className="flex justify-between text-sm text-[#6B7280] mb-2">
            <span>복습 진행 중</span>
            <span className="font-medium">{currentIdx + 1} / {queue.length}</span>
          </div>
          <div className="w-full bg-[#E5E7EB] rounded-full h-2.5">
            <div
              className="bg-[#2563EB] h-2.5 rounded-full transition-all duration-500"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* 플래시카드 */}
        <Card padding="lg" className="min-h-[300px] flex flex-col">
          <CardHeader>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="default">{card.noteTitle ?? '노트'}</Badge>
            </div>
            <CardTitle className="text-xl font-semibold text-[#111827] leading-snug">
              {card.front}
            </CardTitle>
          </CardHeader>

          <CardBody className="flex-1 flex flex-col">
            {showAnswer ? (
              <div className="border-t border-[#E5E7EB] pt-4 mt-4 flex-1">
                <p className="text-xs font-semibold text-[#6B7280] mb-3 uppercase tracking-wide">정답</p>
                <p className="text-[#111827] whitespace-pre-line leading-relaxed">{card.back}</p>
              </div>
            ) : (
              <div className="flex-1 flex items-center justify-center py-8">
                <Button variant="secondary" onClick={() => setShowAnswer(true)} size="lg">
                  정답 확인하기
                </Button>
              </div>
            )}
          </CardBody>
        </Card>

        {/* 난이도 버튼 */}
        {showAnswer && (
          <div>
            <p className="text-sm text-center text-[#6B7280] mb-3 font-medium">
              이 카드가 얼마나 기억났나요?
            </p>
            <div className="grid grid-cols-4 gap-3">
              {QUALITY_BUTTONS.map(({ quality, label, sub, bg }) => (
                <button
                  key={quality}
                  onClick={() => handleQuality(quality)}
                  className={`${bg} text-white rounded-xl py-3 px-2 text-center transition-colors`}
                >
                  <div className="font-semibold text-sm">{label}</div>
                  <div className="text-xs opacity-80 mt-0.5">{sub}</div>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* SM-2 현황 */}
        <div className="flex gap-4 text-xs text-[#9CA3AF]">
          <span>EF: {card.easiness.toFixed(2)}</span>
          <span>간격: {card.interval}일</span>
          <span>반복: {card.repetitions}회</span>
        </div>
      </div>
    )
  }

  // ── 대시보드 ─────────────────────────────────────────────────────
  const dueCount   = dueCards.length
  const todayDone  = stats?.todayReviews ?? 0
  const accuracy   = stats?.accuracy ?? 0
  const studyDays  = stats?.totalStudyDays ?? 0

  return (
    <div className="space-y-8">
      {/* 헤더 */}
      <div>
        <h1 className="text-3xl font-bold text-[#111827]">간격 반복 복습</h1>
        <p className="text-[#6B7280] mt-1">
          SM-2 알고리즘 기반 · Ebbinghaus 망각 곡선 최적화
        </p>
      </div>

      {/* 통계 카드 4개 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '오늘 복습할 카드', value: isDueLoading ? '…' : dueCount,    color: dueCount > 0 ? 'text-[#2563EB]' : 'text-[#16A34A]', icon: '📋' },
          { label: '오늘 완료',        value: isDueLoading ? '…' : todayDone,   color: 'text-[#16A34A]',                                   icon: '✅' },
          { label: '정확도',           value: isDueLoading ? '…' : `${accuracy}%`, color: accuracy >= 70 ? 'text-[#16A34A]' : 'text-[#D97706]', icon: '🎯' },
          { label: '연속 학습일',      value: isDueLoading ? '…' : `${studyDays}일`, color: 'text-[#D97706]',                              icon: '🔥' },
        ].map((s) => (
          <div key={s.label} className="bg-white border border-[#E5E7EB] rounded-xl p-5 text-center">
            <div className="text-2xl mb-1">{s.icon}</div>
            <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-xs text-[#6B7280] mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* 복습 시작 카드 */}
      {isDueLoading ? (
        <div className="flex justify-center py-12">
          <Spinner size="lg" />
        </div>
      ) : dueCount > 0 ? (
        <Card>
          <CardBody className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div>
              <p className="font-semibold text-[#111827] text-lg">
                오늘 복습할 카드가 {dueCount}개 있습니다.
              </p>
              <p className="text-sm text-[#6B7280] mt-1">
                지금 복습하면 SM-2 알고리즘이 각 카드의 다음 복습 일정을 자동 계산합니다.
              </p>
            </div>
            <Button size="lg" onClick={startReview} className="flex-shrink-0">
              복습 시작하기 →
            </Button>
          </CardBody>
        </Card>
      ) : (
        <Card>
          <CardBody className="text-center py-10 space-y-3">
            <div className="text-4xl">🎉</div>
            <p className="font-semibold text-[#111827]">오늘 복습할 카드가 없습니다!</p>
            <p className="text-sm text-[#6B7280]">
              새 노트를 저장하고 복습 카드를 만들어 학습을 시작하세요.
            </p>
            <Button variant="secondary" size="sm" asChild>
              <a href="/notes">노트에서 카드 만들기</a>
            </Button>
          </CardBody>
        </Card>
      )}

      {/* 카드 목록 미리보기 */}
      {dueCards.length > 0 && (
        <div>
          <h2 className="text-lg font-semibold text-[#111827] mb-3">복습 대기 카드</h2>
          <div className="space-y-2">
            {dueCards.slice(0, 5).map((card) => (
              <div key={card.id}
                   className="flex items-center justify-between bg-white border border-[#E5E7EB] rounded-xl px-4 py-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[#111827] truncate">{card.front}</p>
                  <p className="text-xs text-[#9CA3AF] mt-0.5">
                    EF {card.easiness.toFixed(2)} · 간격 {card.interval}일 · {card.repetitions}회 복습
                  </p>
                </div>
                <div className="ml-4 flex-shrink-0">
                  {card.easiness < 1.8 ? (
                    <Badge variant="error">취약</Badge>
                  ) : card.easiness < 2.2 ? (
                    <Badge variant="warning">보통</Badge>
                  ) : (
                    <Badge variant="success">안정</Badge>
                  )}
                </div>
              </div>
            ))}
            {dueCards.length > 5 && (
              <p className="text-center text-sm text-[#6B7280] py-2">
                외 {dueCards.length - 5}개 카드
              </p>
            )}
          </div>
        </div>
      )}

      {/* 망각 곡선 설명 */}
      <div className="bg-white border border-[#E5E7EB] rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-[#111827] mb-4">📈 SM-2 알고리즘 이해하기</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          {[
            {
              title: 'Ebbinghaus 망각 곡선',
              desc: '학습 후 시간이 지날수록 기억이 지수적으로 감소합니다. 적절한 시점에 복습하면 기억이 강화됩니다.',
              icon: '📉',
            },
            {
              title: 'SM-2 간격 계산',
              desc: '처음: 1일 → 6일 → EF × 이전간격. 어려울수록 짧은 간격, 쉬울수록 긴 간격으로 조정됩니다.',
              icon: '⏱️',
            },
            {
              title: 'EF (Easiness Factor)',
              desc: '기억 용이도 지수 (최소 1.3). 쉬움(5)일 때 증가, 어려움(0~2)일 때 감소합니다.',
              icon: '⚖️',
            },
          ].map((item) => (
            <div key={item.title} className="bg-[#F9FAFB] rounded-xl p-4">
              <div className="text-2xl mb-2">{item.icon}</div>
              <p className="font-semibold text-[#111827] mb-1">{item.title}</p>
              <p className="text-[#6B7280] text-xs leading-relaxed">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

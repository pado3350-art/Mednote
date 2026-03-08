import { useState } from 'react'
import { Button, Card, CardBody, CardHeader, CardTitle } from '@/components/ui'

type ReviewPhase = 'dashboard' | 'reviewing' | 'done'

interface MockCard {
  id: string
  front: string
  back: string
  noteTitle: string
}

const MOCK_CARDS: MockCard[] = [
  {
    id: '1',
    front: 'β-차단제의 주요 부작용 3가지는 무엇인가요?',
    back: '1. 서맥(Bradycardia)\n2. 기관지수축 (비선택적 β-차단제에서, 천식 주의)\n3. 피로감 및 운동 능력 저하\n\n추가: 갑작스러운 중단 시 반동 효과(rebound effect) 주의',
    noteTitle: 'β-차단제 작용 메커니즘',
  },
  {
    id: '2',
    front: '약물 반감기(t½) 공식은 무엇인가요?',
    back: 't½ = 0.693 × Vd / CL\n\n- Vd: 분포용적 (Volume of distribution)\n- CL: 청소율 (Clearance)\n- 반감기 후 약물 농도는 50% 감소\n- 정상 상태(Steady state)는 약 4~5 반감기 후 도달',
    noteTitle: '약동학 핵심 파라미터',
  },
]

const QUALITY_BUTTONS = [
  { quality: 0, label: '완전히 잊음', color: 'bg-[#DC2626] text-white hover:bg-[#B91C1C]', desc: '다시' },
  { quality: 3, label: '어려움', color: 'bg-[#D97706] text-white hover:bg-[#B45309]', desc: '1일 후' },
  { quality: 4, label: '보통', color: 'bg-[#2563EB] text-white hover:bg-[#1D4ED8]', desc: '적절' },
  { quality: 5, label: '쉬움', color: 'bg-[#16A34A] text-white hover:bg-[#15803D]', desc: '간격 증가' },
]

export default function ReviewPage() {
  const [phase, setPhase] = useState<ReviewPhase>('dashboard')
  const [currentIndex, setCurrentIndex] = useState(0)
  const [showAnswer, setShowAnswer] = useState(false)
  const [completed, setCompleted] = useState(0)

  const currentCard = MOCK_CARDS[currentIndex]

  const handleQuality = (quality: number) => {
    console.log(`Card ${currentCard.id}: quality=${quality}`)
    const next = currentIndex + 1
    if (next >= MOCK_CARDS.length) {
      setCompleted(next)
      setPhase('done')
    } else {
      setCurrentIndex(next)
      setShowAnswer(false)
    }
  }

  if (phase === 'done') {
    return (
      <div className="max-w-lg mx-auto text-center py-16 space-y-6">
        <div className="text-5xl">🎉</div>
        <h2 className="text-2xl font-bold text-[#111827]">오늘 복습 완료!</h2>
        <p className="text-[#6B7280]">{completed}개의 카드를 복습했습니다.</p>
        <div className="bg-[#F0FDF4] border border-[#BBF7D0] rounded-xl p-6 text-sm text-[#15803D] space-y-1">
          <p>다음 복습은 SM-2 알고리즘에 따라 자동 스케줄됩니다.</p>
          <p className="font-medium">계속 꾸준히 복습하면 장기 기억으로 전환됩니다!</p>
        </div>
        <Button onClick={() => { setPhase('dashboard'); setCurrentIndex(0); setShowAnswer(false) }}>
          대시보드로 돌아가기
        </Button>
      </div>
    )
  }

  if (phase === 'reviewing' && currentCard) {
    return (
      <div className="max-w-2xl mx-auto space-y-6">
        {/* 진행 바 */}
        <div>
          <div className="flex justify-between text-sm text-[#6B7280] mb-2">
            <span>복습 중</span>
            <span>{currentIndex + 1} / {MOCK_CARDS.length}</span>
          </div>
          <div className="w-full bg-[#E5E7EB] rounded-full h-2">
            <div
              className="bg-[#2563EB] h-2 rounded-full transition-all duration-300"
              style={{ width: `${((currentIndex) / MOCK_CARDS.length) * 100}%` }}
            />
          </div>
        </div>

        {/* 카드 */}
        <Card padding="lg" className="min-h-[280px] flex flex-col">
          <CardHeader>
            <p className="text-xs text-[#6B7280]">노트: {currentCard.noteTitle}</p>
            <CardTitle className="mt-2 text-lg font-semibold">{currentCard.front}</CardTitle>
          </CardHeader>

          {showAnswer ? (
            <CardBody>
              <div className="border-t border-[#E5E7EB] pt-4 mt-4">
                <p className="text-xs font-semibold text-[#6B7280] mb-2">정답</p>
                <p className="text-[#111827] whitespace-pre-line leading-relaxed">{currentCard.back}</p>
              </div>
            </CardBody>
          ) : (
            <CardBody>
              <div className="flex-1 flex items-center justify-center py-8">
                <Button variant="secondary" onClick={() => setShowAnswer(true)}>
                  정답 확인하기
                </Button>
              </div>
            </CardBody>
          )}
        </Card>

        {/* 난이도 버튼 */}
        {showAnswer && (
          <div>
            <p className="text-sm text-center text-[#6B7280] mb-3">이 카드가 얼마나 기억났나요?</p>
            <div className="grid grid-cols-4 gap-3">
              {QUALITY_BUTTONS.map(({ quality, label, color, desc }) => (
                <button
                  key={quality}
                  onClick={() => handleQuality(quality)}
                  className={`${color} rounded-xl py-3 px-2 text-center transition-colors`}
                >
                  <div className="font-semibold text-sm">{label}</div>
                  <div className="text-xs opacity-80 mt-0.5">{desc}</div>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // 대시보드
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#111827]">간격 반복 복습</h1>
        <p className="text-[#6B7280] mt-1">SM-2 알고리즘 기반 최적 복습 스케줄 · Ebbinghaus 망각 곡선</p>
      </div>

      {/* 통계 카드 */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: '오늘 복습할 카드', value: MOCK_CARDS.length, color: 'text-[#2563EB]' },
          { label: '전체 카드 수', value: MOCK_CARDS.length, color: 'text-[#111827]' },
          { label: '오늘 완료', value: 0, color: 'text-[#16A34A]' },
          { label: '연속 학습일', value: 1, color: 'text-[#D97706]' },
        ].map((s) => (
          <div key={s.label} className="bg-white border border-[#E5E7EB] rounded-xl p-4 text-center">
            <div className={`text-3xl font-bold ${s.color}`}>{s.value}</div>
            <div className="text-xs text-[#6B7280] mt-1">{s.label}</div>
          </div>
        ))}
      </div>

      {/* 복습 시작 */}
      <Card>
        <CardBody className="flex flex-col sm:flex-row items-center justify-between gap-4">
          <div>
            <p className="font-semibold text-[#111827]">오늘 복습할 카드가 {MOCK_CARDS.length}개 있습니다.</p>
            <p className="text-sm text-[#6B7280] mt-1">완료하면 SM-2 알고리즘이 다음 복습 일정을 계산합니다.</p>
          </div>
          <Button size="lg" onClick={() => setPhase('reviewing')}>
            복습 시작하기
          </Button>
        </CardBody>
      </Card>

      {/* Phase 2 예고 */}
      <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-xl p-4 text-sm text-[#1E40AF]">
        <p className="font-medium mb-1">🔜 Phase 2에서 추가 예정</p>
        <ul className="space-y-1 text-[#3B82F6]">
          <li>• Supabase 연동 — 실제 복습 기록 저장 및 SM-2 계산</li>
          <li>• 망각 곡선 진행 시각화 (D3.js)</li>
          <li>• 브라우저 Push 알림 (복습 리마인더)</li>
          <li>• 취약 개념 자동 식별</li>
        </ul>
      </div>
    </div>
  )
}

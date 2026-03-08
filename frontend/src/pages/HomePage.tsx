import { Link } from 'react-router-dom'
import { Button, Card, CardBody, CardHeader, CardTitle } from '@/components/ui'

const features = [
  {
    icon: '📖',
    title: '챕터 요약 & 시각화',
    description: 'Katzung 교재 기반 핵심 약리학 개념 요약과 인터랙티브 PK/PD 시뮬레이션을 제공합니다.',
    to: '/chapters',
    cta: '챕터 보기',
  },
  {
    icon: '🤖',
    title: 'AI 챗봇 Q&A',
    description: '약리학 전문 AI 튜터에게 언제든지 질문하세요. 교재 기반의 정확하고 상세한 한국어 답변을 제공합니다.',
    to: '/chat',
    cta: '질문하기',
  },
  {
    icon: '📝',
    title: '개인 노트',
    description: 'AI 답변과 챕터 요약을 원클릭으로 저장하고 나만의 약리학 노트를 만들어보세요.',
    to: '/notes',
    cta: '노트 보기',
  },
  {
    icon: '🔁',
    title: '간격 반복 복습',
    description: 'Ebbinghaus 망각 곡선 기반 SM-2 알고리즘으로 최적의 시점에 복습을 알려드립니다.',
    to: '/review',
    cta: '복습 시작',
  },
]

export default function HomePage() {
  return (
    <div className="space-y-16">
      {/* 히어로 섹션 */}
      <section className="text-center py-16 space-y-6">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-[#EFF6FF] text-[#2563EB] rounded-full text-sm font-medium">
          <span>✨</span> Katzung 약리학 기반 AI 학습 플랫폼
        </div>
        <h1 className="text-4xl md:text-5xl font-bold text-[#111827] leading-tight">
          약리학, 더 스마트하게<br />
          <span className="text-[#2563EB]">이해하고 기억하세요</span>
        </h1>
        <p className="text-lg text-[#6B7280] max-w-2xl mx-auto leading-relaxed">
          AI 챗봇으로 즉시 질문하고, 간격 반복 시스템으로 효율적으로 암기하세요.
          의대생·약대생을 위한 맞춤형 약리학 학습 플랫폼입니다.
        </p>
        <div className="flex items-center justify-center gap-4 flex-wrap">
          <Button size="lg" asChild>
            <Link to="/chapters">학습 시작하기</Link>
          </Button>
          <Button size="lg" variant="secondary" asChild>
            <Link to="/chat">AI에게 질문하기</Link>
          </Button>
        </div>
      </section>

      {/* 기능 카드 */}
      <section>
        <h2 className="text-2xl font-semibold text-[#111827] text-center mb-8">핵심 기능</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature) => (
            <Card key={feature.to} hoverable>
              <CardHeader>
                <div className="text-3xl mb-3">{feature.icon}</div>
                <CardTitle className="text-lg">{feature.title}</CardTitle>
              </CardHeader>
              <CardBody>
                <p className="text-sm text-[#6B7280] leading-relaxed mb-4">{feature.description}</p>
                <Button variant="ghost" size="sm" asChild>
                  <Link to={feature.to}>{feature.cta} →</Link>
                </Button>
              </CardBody>
            </Card>
          ))}
        </div>
      </section>

      {/* 통계 섹션 */}
      <section className="bg-[#EFF6FF] rounded-2xl p-8 text-center">
        <h2 className="text-xl font-semibold text-[#1E40AF] mb-6">학습 효과</h2>
        <div className="grid grid-cols-3 gap-8">
          {[
            { value: '60+', label: 'Katzung 챕터' },
            { value: 'SM-2', label: '과학적 복습 알고리즘' },
            { value: '100%', label: '한국어 지원' },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-3xl font-bold text-[#2563EB]">{stat.value}</div>
              <div className="text-sm text-[#4B5563] mt-1">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

import { useParams, Link } from 'react-router-dom'
import { Button, Badge } from '@/components/ui'

// Phase 1 플레이스홀더 — Phase 2에서 API + Markdown 렌더링 + PK 시각화 추가
export default function ChapterDetailPage() {
  const { id } = useParams()

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* 브레드크럼 */}
      <nav className="text-sm text-[#6B7280]">
        <Link to="/chapters" className="hover:text-[#2563EB]">챕터 목록</Link>
        <span className="mx-2">›</span>
        <span className="text-[#111827]">Chapter {id}</span>
      </nav>

      {/* 헤더 */}
      <div className="space-y-2">
        <div className="flex items-center gap-2">
          <Badge variant="default">약동학</Badge>
          <span className="text-sm text-[#6B7280]">Chapter {id}</span>
        </div>
        <h1 className="text-3xl font-bold text-[#111827]">
          약동학: 흡수, 분포, 대사, 배설
        </h1>
        <p className="text-[#6B7280]">
          약물이 체내에서 어떻게 이동하는지 이해하는 핵심 개념들을 다룹니다.
        </p>
      </div>

      {/* 콘텐츠 영역 (Phase 1 플레이스홀더) */}
      <div className="bg-white border border-[#E5E7EB] rounded-xl p-8 space-y-6">
        <div className="bg-[#EFF6FF] border border-[#BFDBFE] rounded-lg p-4 text-sm text-[#1E40AF]">
          📚 이 챕터의 상세 내용은 Phase 1 Sprint 3–4에서 Markdown 렌더링과 함께 추가됩니다.
        </div>

        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-[#111827]">핵심 개념</h2>
          <ul className="space-y-2 text-[#374151]">
            {['ADME (흡수, 분포, 대사, 배설)', '생체이용률 (Bioavailability, F)', '분포용적 (Volume of distribution, Vd)',
              '청소율 (Clearance, CL)', '반감기 (Half-life, t½)', '정상 상태 (Steady state)'].map((item) => (
              <li key={item} className="flex items-start gap-2">
                <span className="text-[#2563EB] mt-0.5">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* PK 시각화 플레이스홀더 */}
        <div className="border-2 border-dashed border-[#E5E7EB] rounded-xl p-8 text-center space-y-2">
          <div className="text-2xl">📈</div>
          <p className="font-medium text-[#374151]">PK 인터랙티브 시뮬레이터</p>
          <p className="text-sm text-[#9CA3AF]">Phase 1 Sprint 3–4에서 혈중 농도-시간 곡선 시각화가 추가됩니다.</p>
        </div>
      </div>

      {/* 액션 버튼 */}
      <div className="flex gap-3 flex-wrap">
        <Button variant="secondary" asChild>
          <Link to="/chat">이 챕터에 대해 AI에게 질문하기</Link>
        </Button>
        <Button variant="ghost">노트에 요약 저장</Button>
      </div>
    </div>
  )
}

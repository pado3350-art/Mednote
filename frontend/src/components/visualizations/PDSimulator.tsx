/**
 * 약력학(PD) 인터랙티브 시뮬레이터
 * - 용량-반응 곡선 (Emax 모델)
 * - 효능제 + 경쟁적/비경쟁적 길항제 비교
 * - EC50, Emax, Hill 계수(n) 조절
 */

import { useState, useMemo } from 'react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, ReferenceLine, ResponsiveContainer,
} from 'recharts'

interface PDParams {
  emax: number       // 최대 효과 (%)
  ec50: number       // EC50 (nM)
  hillN: number      // Hill 계수
  antagonistType: 'none' | 'competitive' | 'noncompetitive'
  antagonistConc: number   // 길항제 농도 (nM)
  antagonistKi: number     // 길항제 Ki (nM)
}

const DEFAULTS: PDParams = {
  emax: 100,
  ec50: 10,
  hillN: 1,
  antagonistType: 'none',
  antagonistConc: 20,
  antagonistKi: 5,
}

// Hill 방정식 (시그모이드 Emax 모델)
function hillEffect(c: number, emax: number, ec50: number, n: number): number {
  if (c <= 0) return 0
  const cn = Math.pow(c, n)
  const ec50n = Math.pow(ec50, n)
  return (emax * cn) / (ec50n + cn)
}

function calcPDCurve(p: PDParams) {
  const points: { logConc: number; conc: number; agonist: number; withAntagonist?: number }[] = []

  // 0.01 nM ~ 10000 nM 로그 스케일
  for (let i = 0; i <= 80; i++) {
    const logC = -2 + (i / 80) * 6   // -2 ~ 4 (log10 nM)
    const c = Math.pow(10, logC)

    const agonistEffect = hillEffect(c, p.emax, p.ec50, p.hillN)

    let antagonistEffect: number | undefined
    if (p.antagonistType === 'competitive') {
      // 경쟁적 길항제: EC50 apparent = EC50 × (1 + [B]/Ki)
      const apparentEC50 = p.ec50 * (1 + p.antagonistConc / p.antagonistKi)
      antagonistEffect = hillEffect(c, p.emax, apparentEC50, p.hillN)
    } else if (p.antagonistType === 'noncompetitive') {
      // 비경쟁적 길항제: Emax apparent = Emax / (1 + [B]/Ki)
      const apparentEmax = p.emax / (1 + p.antagonistConc / p.antagonistKi)
      antagonistEffect = hillEffect(c, apparentEmax, p.ec50, p.hillN)
    }

    points.push({
      logConc: parseFloat(logC.toFixed(2)),
      conc: parseFloat(c.toFixed(4)),
      agonist: parseFloat(agonistEffect.toFixed(2)),
      ...(antagonistEffect !== undefined ? { withAntagonist: parseFloat(antagonistEffect.toFixed(2)) } : {}),
    })
  }
  return points
}

function ParamSlider({
  label, value, min, max, step, unit, onChange, logScale = false,
}: {
  label: string; value: number; min: number; max: number
  step: number; unit: string; onChange: (v: number) => void; logScale?: boolean
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-[#374151]">{label}</label>
        <span className="text-sm font-semibold text-[#2563EB] tabular-nums">
          {logScale ? value.toFixed(0) : value} {unit}
        </span>
      </div>
      <input
        type="range" min={min} max={max} step={step} value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-[#E5E7EB] rounded-full appearance-none cursor-pointer
                   [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4
                   [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full
                   [&::-webkit-slider-thumb]:bg-[#2563EB] [&::-webkit-slider-thumb]:cursor-pointer"
      />
      <div className="flex justify-between text-xs text-[#9CA3AF]">
        <span>{min}</span><span>{max}</span>
      </div>
    </div>
  )
}

const ANTAGONIST_COLORS = {
  agonist: '#2563EB',
  withAntagonist: '#DC2626',
}

export function PDSimulator() {
  const [params, setParams] = useState<PDParams>(DEFAULTS)
  const update = (key: keyof PDParams) => (v: number | string) =>
    setParams((p) => ({ ...p, [key]: v }))

  const curve = useMemo(() => calcPDCurve(params), [params])

  const antagonistLabel: Record<PDParams['antagonistType'], string> = {
    none: '없음',
    competitive: '경쟁적 길항제',
    noncompetitive: '비경쟁적 길항제',
  }

  return (
    <div className="bg-white border border-[#E5E7EB] rounded-2xl overflow-hidden">
      {/* 헤더 */}
      <div className="bg-[#16A34A] px-6 py-4">
        <h3 className="text-lg font-semibold text-white">💊 약력학(PD) 인터랙티브 시뮬레이터</h3>
        <p className="text-sm text-[#BBF7D0] mt-0.5">용량-반응 곡선과 길항제 효과를 실시간으로 비교하세요.</p>
      </div>

      <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 파라미터 패널 */}
        <div className="space-y-5 lg:col-span-1">
          <p className="text-sm font-semibold text-[#374151]">효능제 파라미터</p>
          <ParamSlider label="Emax (최대 효과)" value={params.emax} min={10} max={100} step={5} unit="%" onChange={update('emax')} />
          <ParamSlider label="EC₅₀" value={params.ec50} min={1} max={200} step={1} unit="nM" onChange={update('ec50')} />
          <ParamSlider label="Hill 계수 (n)" value={params.hillN} min={0.5} max={4} step={0.1} unit="" onChange={update('hillN')} />

          <div className="pt-2 border-t border-[#E5E7EB]">
            <p className="text-sm font-semibold text-[#374151] mb-2">길항제</p>
            <div className="flex flex-col gap-1.5">
              {(['none', 'competitive', 'noncompetitive'] as const).map((type) => (
                <button
                  key={type}
                  onClick={() => update('antagonistType')(type)}
                  className={`py-2 px-3 rounded-lg text-sm text-left transition-colors ${
                    params.antagonistType === type
                      ? 'bg-[#DC2626] text-white font-medium'
                      : 'bg-[#F3F4F6] text-[#374151] hover:bg-[#E5E7EB]'
                  }`}
                >
                  {antagonistLabel[type]}
                </button>
              ))}
            </div>

            {params.antagonistType !== 'none' && (
              <div className="mt-4 space-y-4">
                <ParamSlider label="길항제 농도 [B]" value={params.antagonistConc} min={1} max={200} step={1} unit="nM" onChange={update('antagonistConc')} />
                <ParamSlider label="길항제 Ki" value={params.antagonistKi} min={1} max={100} step={1} unit="nM" onChange={update('antagonistKi')} />
              </div>
            )}
          </div>
        </div>

        {/* 차트 */}
        <div className="lg:col-span-2 space-y-3">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={curve} margin={{ top: 10, right: 30, left: 0, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F0" />
                <XAxis
                  dataKey="logConc"
                  label={{ value: 'log [농도] (log nM)', position: 'insideBottomRight', offset: -5, style: { fontSize: 12, fill: '#6B7280' } }}
                  tick={{ fontSize: 11, fill: '#6B7280' }}
                  tickFormatter={(v) => `10^${v}`}
                />
                <YAxis
                  domain={[0, 110]}
                  label={{ value: '효과 (%)', angle: -90, position: 'insideLeft', offset: 10, style: { fontSize: 12, fill: '#6B7280' } }}
                  tick={{ fontSize: 11, fill: '#6B7280' }}
                />
                <Tooltip
                  contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}
                  formatter={(v, name) => [
                    `${(v as number).toFixed(1)}%`,
                    name === 'agonist' ? '효능제 단독' : `+ ${antagonistLabel[params.antagonistType]}`,
                  ]}
                  labelFormatter={(l) => `농도: 10^${l} nM`}
                />
                <Legend
                  formatter={(v) => v === 'agonist' ? '효능제 단독' : `+ ${antagonistLabel[params.antagonistType]}`}
                />
                {/* Emax 50% 기준선 */}
                <ReferenceLine y={params.emax / 2} stroke="#6B7280" strokeDasharray="4 4"
                  label={{ value: `EC₅₀ 기준 (${(params.emax / 2).toFixed(0)}%)`, position: 'insideTopRight', fontSize: 10, fill: '#6B7280' }} />

                <Line type="monotone" dataKey="agonist" stroke={ANTAGONIST_COLORS.agonist}
                  strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
                {params.antagonistType !== 'none' && (
                  <Line type="monotone" dataKey="withAntagonist" stroke={ANTAGONIST_COLORS.withAntagonist}
                    strokeWidth={2.5} strokeDasharray="6 3" dot={false} activeDot={{ r: 4 }} />
                )}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* 개념 설명 */}
          {params.antagonistType !== 'none' && (
            <div className="bg-[#FEF2F2] rounded-xl p-4 text-sm text-[#991B1B] space-y-1">
              <p className="font-medium">
                {params.antagonistType === 'competitive' ? '⚡ 경쟁적 길항제 효과' : '🚫 비경쟁적 길항제 효과'}
              </p>
              {params.antagonistType === 'competitive' ? (
                <>
                  <p>• EC₅₀ 증가 → 곡선이 <strong>오른쪽으로 이동</strong> (Emax 유지)</p>
                  <p>• 효능제 농도를 높이면 길항 효과 <strong>극복 가능</strong></p>
                </>
              ) : (
                <>
                  <p>• Emax 감소 → 곡선이 <strong>아래로 이동</strong> (EC₅₀ 유지)</p>
                  <p>• 효능제 농도를 높여도 <strong>극복 불가</strong></p>
                </>
              )}
            </div>
          )}

          <div className="bg-[#EFF6FF] rounded-xl p-4 text-sm text-[#1E40AF] space-y-1">
            <p className="font-medium">💡 Hill 계수(n) 의미</p>
            <p>• n = 1: 단순 쌍곡선 (1개 결합 부위)</p>
            <p>• n &gt; 1: 가파른 S자형 (협동성, 예: 헤모글로빈)</p>
            <p>• n &lt; 1: 완만한 곡선 (음성 협동성)</p>
          </div>
        </div>
      </div>
    </div>
  )
}

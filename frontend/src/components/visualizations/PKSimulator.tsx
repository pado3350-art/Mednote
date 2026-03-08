/**
 * 약동학(PK) 인터랙티브 시뮬레이터
 * - 혈중 농도-시간 곡선 (단회 경구/정맥 투여)
 * - 슬라이더로 Vd, CL, F, Dose 실시간 조절
 * - Tmax, Cmax, t½, AUC 자동 계산 및 표시
 */

import { useState, useMemo } from 'react'
import {
  XAxis, YAxis, CartesianGrid, Tooltip,
  ReferenceLine, ResponsiveContainer, Area, AreaChart,
} from 'recharts'

// ── PK 파라미터 기본값 ──────────────────────────────────────────
interface PKParams {
  dose: number   // mg
  vd: number     // L/kg × 70 kg (→ L)
  cl: number     // L/h
  f: number      // 0~1 (생체이용률)
  ka: number     // h⁻¹ (흡수 속도 상수)
  route: 'oral' | 'iv'
}

const DEFAULTS: PKParams = {
  dose: 500,
  vd: 42,
  cl: 3.5,
  f: 0.8,
  ka: 1.2,
  route: 'oral',
}

// ── 수치 계산 ────────────────────────────────────────────────────
function calcPKCurve(p: PKParams): { time: number; conc: number }[] {
  const ke = p.cl / p.vd          // 소실 속도 상수 (h⁻¹)
  const points: { time: number; conc: number }[] = []
  const tMax = 48                  // 시뮬레이션 시간 (h)
  const steps = 200

  for (let i = 0; i <= steps; i++) {
    const t = (i / steps) * tMax
    let conc: number

    if (p.route === 'iv') {
      // 단회 정맥 투여: C(t) = (Dose/Vd) × e^(-ke×t)
      conc = (p.dose / p.vd) * Math.exp(-ke * t)
    } else {
      // 단회 경구 투여: C(t) = (F×Dose×ka) / (Vd×(ka-ke)) × (e^(-ke×t) - e^(-ka×t))
      if (Math.abs(p.ka - ke) < 0.001) {
        // ka ≈ ke 특수 케이스 방지
        conc = (p.f * p.dose * ke * t / p.vd) * Math.exp(-ke * t)
      } else {
        conc =
          (p.f * p.dose * p.ka) /
          (p.vd * (p.ka - ke)) *
          (Math.exp(-ke * t) - Math.exp(-p.ka * t))
      }
    }

    points.push({ time: parseFloat(t.toFixed(2)), conc: parseFloat(Math.max(0, conc).toFixed(4)) })
  }
  return points
}

function calcMetrics(p: PKParams, curve: { time: number; conc: number }[]) {
  const ke = p.cl / p.vd
  const halfLife = parseFloat((0.693 / ke).toFixed(1))

  const cmax = Math.max(...curve.map((d) => d.conc))
  const tmax = curve.find((d) => d.conc === cmax)?.time ?? 0

  // AUC via trapezoidal rule
  let auc = 0
  for (let i = 1; i < curve.length; i++) {
    const dt = curve[i].time - curve[i - 1].time
    auc += ((curve[i].conc + curve[i - 1].conc) / 2) * dt
  }

  return {
    halfLife,
    cmax: parseFloat(cmax.toFixed(3)),
    tmax: parseFloat(tmax.toFixed(1)),
    auc: parseFloat(auc.toFixed(1)),
  }
}

// ── 슬라이더 컴포넌트 ─────────────────────────────────────────────
function ParamSlider({
  label, value, min, max, step, unit, onChange,
}: {
  label: string; value: number; min: number; max: number
  step: number; unit: string; onChange: (v: number) => void
}) {
  return (
    <div className="space-y-1">
      <div className="flex justify-between items-center">
        <label className="text-sm font-medium text-[#374151]">{label}</label>
        <span className="text-sm font-semibold text-[#2563EB] tabular-nums">
          {value} {unit}
        </span>
      </div>
      <input
        type="range"
        min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-2 bg-[#E5E7EB] rounded-full appearance-none cursor-pointer
                   [&::-webkit-slider-thumb]:appearance-none
                   [&::-webkit-slider-thumb]:w-4
                   [&::-webkit-slider-thumb]:h-4
                   [&::-webkit-slider-thumb]:rounded-full
                   [&::-webkit-slider-thumb]:bg-[#2563EB]
                   [&::-webkit-slider-thumb]:cursor-pointer"
      />
      <div className="flex justify-between text-xs text-[#9CA3AF]">
        <span>{min}</span><span>{max}</span>
      </div>
    </div>
  )
}

// ── 메인 컴포넌트 ─────────────────────────────────────────────────
export function PKSimulator() {
  const [params, setParams] = useState<PKParams>(DEFAULTS)

  const update = (key: keyof PKParams) => (v: number | string) =>
    setParams((p) => ({ ...p, [key]: v }))

  const curve = useMemo(() => calcPKCurve(params), [params])
  const metrics = useMemo(() => calcMetrics(params, curve), [params, curve])

  const MEC = 5   // 최소 유효 농도 (예시, mg/L)
  const MTC = 30  // 최소 독성 농도 (예시, mg/L)

  return (
    <div className="bg-white border border-[#E5E7EB] rounded-2xl overflow-hidden">
      {/* 헤더 */}
      <div className="bg-[#2563EB] px-6 py-4">
        <h3 className="text-lg font-semibold text-white">📈 약동학(PK) 인터랙티브 시뮬레이터</h3>
        <p className="text-sm text-[#BFDBFE] mt-0.5">파라미터를 조절하여 혈중 농도-시간 곡선을 실시간으로 확인하세요.</p>
      </div>

      <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 왼쪽: 파라미터 슬라이더 */}
        <div className="space-y-5 lg:col-span-1">
          {/* 투여 경로 선택 */}
          <div>
            <p className="text-sm font-medium text-[#374151] mb-2">투여 경로</p>
            <div className="flex gap-2">
              {(['oral', 'iv'] as const).map((r) => (
                <button
                  key={r}
                  onClick={() => update('route')(r)}
                  className={`flex-1 py-2 rounded-lg text-sm font-medium transition-colors ${
                    params.route === r
                      ? 'bg-[#2563EB] text-white'
                      : 'bg-[#F3F4F6] text-[#374151] hover:bg-[#E5E7EB]'
                  }`}
                >
                  {r === 'oral' ? '경구 (PO)' : '정맥 (IV)'}
                </button>
              ))}
            </div>
          </div>

          <ParamSlider label="용량 (Dose)" value={params.dose} min={50} max={1000} step={50} unit="mg" onChange={update('dose')} />
          <ParamSlider label="분포용적 (Vd)" value={params.vd} min={5} max={200} step={5} unit="L" onChange={update('vd')} />
          <ParamSlider label="청소율 (CL)" value={params.cl} min={0.5} max={20} step={0.5} unit="L/h" onChange={update('cl')} />
          {params.route === 'oral' && (
            <>
              <ParamSlider label="생체이용률 (F)" value={params.f} min={0.1} max={1.0} step={0.05} unit="" onChange={update('f')} />
              <ParamSlider label="흡수 속도 (ka)" value={params.ka} min={0.1} max={5.0} step={0.1} unit="h⁻¹" onChange={update('ka')} />
            </>
          )}

          {/* 계산된 지표 */}
          <div className="bg-[#F9FAFB] rounded-xl p-4 space-y-2.5 border border-[#E5E7EB]">
            <p className="text-xs font-semibold text-[#6B7280] uppercase tracking-wide">계산된 파라미터</p>
            {[
              { label: 'Cmax', value: `${metrics.cmax} mg/L`, color: '#2563EB' },
              { label: 'Tmax', value: `${metrics.tmax} h`, color: '#2563EB' },
              { label: 't½ (반감기)', value: `${metrics.halfLife} h`, color: '#16A34A' },
              { label: 'AUC₀→∞', value: `${metrics.auc} mg·h/L`, color: '#D97706' },
            ].map(({ label, value, color }) => (
              <div key={label} className="flex justify-between items-center">
                <span className="text-sm text-[#6B7280]">{label}</span>
                <span className="text-sm font-bold tabular-nums" style={{ color }}>{value}</span>
              </div>
            ))}
          </div>
        </div>

        {/* 오른쪽: 차트 */}
        <div className="lg:col-span-2 space-y-3">
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={curve} margin={{ top: 10, right: 20, left: 0, bottom: 10 }}>
                <defs>
                  <linearGradient id="pkGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#2563EB" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#2563EB" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F0F0F0" />
                <XAxis
                  dataKey="time"
                  label={{ value: '시간 (h)', position: 'insideBottomRight', offset: -5, style: { fontSize: 12, fill: '#6B7280' } }}
                  tick={{ fontSize: 11, fill: '#6B7280' }}
                />
                <YAxis
                  label={{ value: '농도 (mg/L)', angle: -90, position: 'insideLeft', offset: 10, style: { fontSize: 12, fill: '#6B7280' } }}
                  tick={{ fontSize: 11, fill: '#6B7280' }}
                />
                <Tooltip
                  contentStyle={{ fontSize: 12, borderRadius: 8, border: '1px solid #E5E7EB' }}
                  formatter={(v) => [`${(v as number).toFixed(3)} mg/L`, '혈중 농도']}
                  labelFormatter={(l) => `시간: ${l}h`}
                />
                {/* MEC / MTC 기준선 */}
                <ReferenceLine y={MEC} stroke="#16A34A" strokeDasharray="5 3"
                  label={{ value: 'MEC', position: 'right', fontSize: 11, fill: '#16A34A' }} />
                <ReferenceLine y={MTC} stroke="#DC2626" strokeDasharray="5 3"
                  label={{ value: 'MTC', position: 'right', fontSize: 11, fill: '#DC2626' }} />
                <Area
                  type="monotone" dataKey="conc"
                  stroke="#2563EB" strokeWidth={2.5}
                  fill="url(#pkGradient)"
                  dot={false} activeDot={{ r: 4, fill: '#2563EB' }}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* 범례 설명 */}
          <div className="flex flex-wrap gap-4 text-xs text-[#6B7280]">
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-0.5 bg-[#2563EB] inline-block" /> 혈중 농도-시간 곡선
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-0.5 bg-[#16A34A] inline-block border-dashed border" /> MEC (최소 유효 농도)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-4 h-0.5 bg-[#DC2626] inline-block" /> MTC (최소 독성 농도)
            </span>
          </div>

          {/* 개념 설명 */}
          <div className="bg-[#EFF6FF] rounded-xl p-4 text-sm text-[#1E40AF] space-y-1">
            <p className="font-medium">💡 조절 팁</p>
            <p>• <strong>Vd 증가</strong> → Cmax 감소, t½ 증가 (조직 분포 증가)</p>
            <p>• <strong>CL 증가</strong> → t½ 감소, AUC 감소 (빠른 제거)</p>
            {params.route === 'oral' && <p>• <strong>ka 증가</strong> → Tmax 단축, Cmax 증가 (빠른 흡수)</p>}
          </div>
        </div>
      </div>
    </div>
  )
}

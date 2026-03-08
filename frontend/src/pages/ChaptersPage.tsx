import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardBody, CardHeader, CardTitle, Badge, Input } from '@/components/ui'
import { CHAPTERS } from '@/content/chapters'

const CATEGORIES = [
  { id: 'other',          label: '기초약리학' },
  { id: 'autonomic',      label: '자율신경계' },
  { id: 'cardiovascular', label: '심혈관계' },
  { id: 'cns',            label: '중추신경계' },
]

export default function ChaptersPage() {
  const [search, setSearch] = useState('')
  const [activeCat, setActiveCat] = useState<string | null>(null)

  const filtered = CHAPTERS.filter((ch) => {
    const matchSearch =
      ch.titleKo.includes(search) ||
      String(ch.number).includes(search) ||
      ch.category.includes(search)
    const matchCat = !activeCat || ch.categoryId === activeCat
    return matchSearch && matchCat
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#111827]">챕터 목록</h1>
        <p className="text-[#6B7280] mt-1">
          Katzung 약리학 교재 기반 · {CHAPTERS.length}개 챕터
        </p>
      </div>

      {/* 검색 */}
      <Input
        placeholder="챕터 제목, 번호, 카테고리로 검색..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {/* 카테고리 필터 */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveCat(null)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            !activeCat ? 'bg-[#2563EB] text-white' : 'bg-[#F3F4F6] text-[#374151] hover:bg-[#E5E7EB]'
          }`}
        >
          전체 ({CHAPTERS.length})
        </button>
        {CATEGORIES.map((cat) => {
          const count = CHAPTERS.filter((c) => c.categoryId === cat.id).length
          return (
            <button
              key={cat.id}
              onClick={() => setActiveCat(activeCat === cat.id ? null : cat.id)}
              className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
                activeCat === cat.id
                  ? 'bg-[#2563EB] text-white'
                  : 'bg-[#F3F4F6] text-[#374151] hover:bg-[#E5E7EB]'
              }`}
            >
              {cat.label} ({count})
            </button>
          )
        })}
      </div>

      {/* 챕터 그리드 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((chapter) => (
          <Link key={chapter.id} to={`/chapters/${chapter.id}`}>
            <Card hoverable padding="md" className="h-full">
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-semibold text-[#6B7280]">
                    Chapter {chapter.number}
                  </span>
                  <div className="flex gap-1 flex-wrap justify-end">
                    <Badge variant="default">{chapter.category}</Badge>
                    {(chapter.hasPkSim || chapter.hasPdSim) && (
                      <Badge variant="success">시뮬레이터</Badge>
                    )}
                  </div>
                </div>
                <CardTitle className="mt-2 text-base leading-snug">{chapter.titleKo}</CardTitle>
              </CardHeader>
              <CardBody>
                <span className="text-xs text-[#2563EB] font-medium">자세히 보기 →</span>
              </CardBody>
            </Card>
          </Link>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 space-y-2">
          <p className="text-[#9CA3AF]">검색 결과가 없습니다.</p>
          <button
            onClick={() => { setSearch(''); setActiveCat(null) }}
            className="text-sm text-[#2563EB] hover:underline"
          >
            필터 초기화
          </button>
        </div>
      )}
    </div>
  )
}

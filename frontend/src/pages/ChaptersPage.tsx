import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Card, CardBody, CardHeader, CardTitle, Badge, Input } from '@/components/ui'

// Phase 1: 정적 챕터 목록 (추후 API 연동)
const CHAPTER_CATEGORIES = [
  { id: 'autonomic', label: '자율신경계' },
  { id: 'cardiovascular', label: '심혈관계' },
  { id: 'cns', label: '중추신경계' },
  { id: 'antimicrobial', label: '항미생물제' },
  { id: 'endocrine', label: '내분비계' },
  { id: 'other', label: '기타' },
]

const CHAPTERS = [
  { id: 1, number: 1, titleKo: '약리학 입문: 수용체와 약력학', category: 'other' },
  { id: 2, number: 2, titleKo: '약동학: 흡수, 분포, 대사, 배설', category: 'other' },
  { id: 3, number: 3, titleKo: '자율신경 약리학 개요', category: 'autonomic' },
  { id: 4, number: 4, titleKo: '콜린수용체 효능제', category: 'autonomic' },
  { id: 5, number: 5, titleKo: '항콜린에스테라제 약물', category: 'autonomic' },
  { id: 6, number: 6, titleKo: '콜린수용체 차단제', category: 'autonomic' },
  { id: 7, number: 7, titleKo: '아드레날린 작용약물 합성, 저장, 분비', category: 'autonomic' },
  { id: 8, number: 8, titleKo: '아드레날린 효능제 및 교감신경 흥분제', category: 'autonomic' },
  { id: 9, number: 9, titleKo: '아드레날린 수용체 차단제', category: 'autonomic' },
  { id: 10, number: 10, titleKo: '항고혈압제', category: 'cardiovascular' },
  { id: 11, number: 11, titleKo: '혈관확장제와 협심증 치료', category: 'cardiovascular' },
  { id: 12, number: 12, titleKo: '심부전 약물치료', category: 'cardiovascular' },
  { id: 13, number: 13, titleKo: '항부정맥제', category: 'cardiovascular' },
  { id: 14, number: 14, titleKo: '이뇨제', category: 'cardiovascular' },
  { id: 15, number: 15, titleKo: '진정 수면제', category: 'cns' },
  { id: 16, number: 16, titleKo: '알코올', category: 'cns' },
  { id: 17, number: 17, titleKo: '항경련제', category: 'cns' },
  { id: 18, number: 18, titleKo: '파킨슨병 치료제', category: 'cns' },
  { id: 19, number: 19, titleKo: '마약성 진통제', category: 'cns' },
  { id: 20, number: 20, titleKo: '항정신병약 및 리튬', category: 'cns' },
]

export default function ChaptersPage() {
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState<string | null>(null)

  const filtered = CHAPTERS.filter((ch) => {
    const matchSearch = ch.titleKo.includes(search) || String(ch.number).includes(search)
    const matchCategory = !activeCategory || ch.category === activeCategory
    return matchSearch && matchCategory
  })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#111827]">챕터 목록</h1>
        <p className="text-[#6B7280] mt-1">Katzung 약리학 교재 기반 챕터를 선택하세요.</p>
      </div>

      {/* 검색 & 필터 */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="flex-1">
          <Input
            placeholder="챕터 제목 또는 번호로 검색..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => setActiveCategory(null)}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            !activeCategory
              ? 'bg-[#2563EB] text-white'
              : 'bg-[#F3F4F6] text-[#374151] hover:bg-[#E5E7EB]'
          }`}
        >
          전체
        </button>
        {CHAPTER_CATEGORIES.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id === activeCategory ? null : cat.id)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              activeCategory === cat.id
                ? 'bg-[#2563EB] text-white'
                : 'bg-[#F3F4F6] text-[#374151] hover:bg-[#E5E7EB]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* 챕터 그리드 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((chapter) => {
          const category = CHAPTER_CATEGORIES.find((c) => c.id === chapter.category)
          return (
            <Link key={chapter.id} to={`/chapters/${chapter.id}`}>
              <Card hoverable padding="md">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <span className="text-xs font-semibold text-[#6B7280]">
                      Chapter {chapter.number}
                    </span>
                    {category && <Badge variant="default">{category.label}</Badge>}
                  </div>
                  <CardTitle className="mt-2 text-base">{chapter.titleKo}</CardTitle>
                </CardHeader>
                <CardBody>
                  <span className="text-xs text-[#2563EB] font-medium">자세히 보기 →</span>
                </CardBody>
              </Card>
            </Link>
          )
        })}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 text-[#9CA3AF]">
          검색 결과가 없습니다.
        </div>
      )}
    </div>
  )
}

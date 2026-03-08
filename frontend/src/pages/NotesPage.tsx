import { useState } from 'react'
import { Card, CardBody, CardHeader, CardTitle, CardFooter, Button, Badge, Input } from '@/components/ui'
import type { Note } from '@/types'

// Phase 1: 로컬 상태 기반 (Phase 2에서 Supabase API 연동)
const MOCK_NOTES: Note[] = [
  {
    id: '1',
    userId: 'user1',
    chapterId: 10,
    title: 'β-차단제 작용 메커니즘',
    content: 'β-차단제는 교감신경계의 β-아드레날린 수용체를 차단하여 심박수 감소, 심근 수축력 감소, 혈압 하강 효과를 나타냅니다. β1 선택적 차단제(아테놀롤, 메토프롤롤)와 비선택적 차단제(프로프라놀롤)로 분류됩니다.',
    sourceType: 'ai_chat',
    tags: ['β-차단제', '항고혈압', '심혈관'],
    isPublic: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    userId: 'user1',
    chapterId: 2,
    title: '약동학 핵심 파라미터',
    content: '생체이용률(F): 경구 투여 후 전신 순환에 도달하는 약물의 분율. 분포용적(Vd): 약물이 체내에 분포되어 있다고 가상할 때의 용적. 청소율(CL): 단위 시간당 약물이 제거되는 혈장 용적. 반감기(t½) = 0.693 × Vd / CL',
    sourceType: 'chapter_summary',
    tags: ['약동학', 'ADME', '반감기'],
    isPublic: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
]

const SOURCE_LABELS: Record<Note['sourceType'], { label: string; variant: 'primary' | 'success' | 'default' }> = {
  ai_chat:          { label: 'AI 답변', variant: 'primary' },
  chapter_summary:  { label: '챕터 요약', variant: 'success' },
  manual:           { label: '직접 작성', variant: 'default' },
}

export default function NotesPage() {
  const [notes] = useState<Note[]>(MOCK_NOTES)
  const [search, setSearch] = useState('')

  const filtered = notes.filter(
    (n) =>
      n.title.includes(search) ||
      n.content.includes(search) ||
      n.tags.some((t) => t.includes(search)),
  )

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-[#111827]">내 노트</h1>
          <p className="text-[#6B7280] mt-1">저장된 AI 답변과 챕터 요약을 관리하세요.</p>
        </div>
        <Button>+ 새 노트 작성</Button>
      </div>

      <div className="flex gap-4">
        <div className="flex-1">
          <Input
            placeholder="노트 검색 (제목, 내용, 태그)..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
      </div>

      {/* 통계 */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: '전체 노트', value: notes.length },
          { label: 'AI 답변', value: notes.filter((n) => n.sourceType === 'ai_chat').length },
          { label: '복습 카드', value: 0 },
        ].map((stat) => (
          <div key={stat.label} className="bg-white border border-[#E5E7EB] rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-[#2563EB]">{stat.value}</div>
            <div className="text-xs text-[#6B7280] mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* 노트 목록 */}
      <div className="space-y-4">
        {filtered.map((note) => {
          const src = SOURCE_LABELS[note.sourceType]
          return (
            <Card key={note.id}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2 flex-wrap">
                  <CardTitle className="text-lg">{note.title}</CardTitle>
                  <Badge variant={src.variant}>{src.label}</Badge>
                </div>
              </CardHeader>
              <CardBody>
                <p className="text-sm text-[#374151] leading-relaxed line-clamp-3">{note.content}</p>
                {note.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {note.tags.map((tag) => (
                      <Badge key={tag} variant="outline">#{tag}</Badge>
                    ))}
                  </div>
                )}
              </CardBody>
              <CardFooter>
                <Button variant="ghost" size="sm">편집</Button>
                <Button variant="ghost" size="sm">복습 카드 생성</Button>
                <Button variant="ghost" size="sm" className="ml-auto text-[#DC2626] hover:bg-red-50">삭제</Button>
              </CardFooter>
            </Card>
          )
        })}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16 space-y-2">
          <div className="text-4xl">📝</div>
          <p className="text-[#6B7280]">아직 저장된 노트가 없습니다.</p>
          <p className="text-sm text-[#9CA3AF]">챕터 요약이나 AI 답변을 저장해보세요.</p>
        </div>
      )}
    </div>
  )
}

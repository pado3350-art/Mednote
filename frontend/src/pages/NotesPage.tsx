import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardBody, CardHeader, CardTitle, CardFooter, Button, Badge, Input, Spinner } from '@/components/ui'
import { notesApi } from '@/lib/api'
import { useNotesStore } from '@/stores/notesStore'
import type { Note } from '@/types'

const SOURCE_LABELS: Record<Note['sourceType'], { label: string; variant: 'primary' | 'success' | 'default' }> = {
  ai_chat:         { label: 'AI 답변',   variant: 'primary' },
  chapter_summary: { label: '챕터 요약', variant: 'success' },
  manual:          { label: '직접 작성', variant: 'default' },
}

export default function NotesPage() {
  const [search, setSearch] = useState('')
  const { openSaveModal } = useNotesStore()
  const queryClient = useQueryClient()

  // 노트 목록 조회
  const { data: notes = [], isLoading, isError } = useQuery({
    queryKey: ['notes'],
    queryFn: () => notesApi.list(),
  })

  // 노트 삭제
  const { mutate: deleteNote, isPending: isDeleting } = useMutation({
    mutationFn: (id: string) => notesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['notes'] }),
  })

  const [confirmDeleteId, setConfirmDeleteId] = useState<string | null>(null)

  const filtered = notes.filter(
    (n) =>
      n.title.toLowerCase().includes(search.toLowerCase()) ||
      n.content.toLowerCase().includes(search.toLowerCase()) ||
      n.tags.some((t) => t.toLowerCase().includes(search.toLowerCase())),
  )

  const handleDelete = (id: string) => {
    if (confirmDeleteId === id) {
      deleteNote(id)
      setConfirmDeleteId(null)
    } else {
      setConfirmDeleteId(id)
      // 3초 뒤 확인 초기화
      setTimeout(() => setConfirmDeleteId((prev) => (prev === id ? null : prev)), 3000)
    }
  }

  return (
    <div className="space-y-6">
      {/* 헤더 */}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-bold text-[#111827]">내 노트</h1>
          <p className="text-[#6B7280] mt-1">저장된 AI 답변과 챕터 요약을 관리하세요.</p>
        </div>
        <Button
          onClick={() =>
            openSaveModal({
              content: '',
              sourceType: 'manual',
              suggestedTitle: '',
            })
          }
        >
          + 새 노트 작성
        </Button>
      </div>

      {/* 검색 */}
      <Input
        placeholder="제목, 내용, 태그로 검색..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      {/* 통계 */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: '전체 노트', value: notes.length },
          { label: 'AI 답변',  value: notes.filter((n) => n.sourceType === 'ai_chat').length },
          { label: '챕터 요약', value: notes.filter((n) => n.sourceType === 'chapter_summary').length },
        ].map((stat) => (
          <div key={stat.label} className="bg-white border border-[#E5E7EB] rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-[#2563EB]">{stat.value}</div>
            <div className="text-xs text-[#6B7280] mt-1">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* 로딩 */}
      {isLoading && (
        <div className="flex justify-center py-16">
          <div className="text-center space-y-3">
            <Spinner size="lg" />
            <p className="text-sm text-[#6B7280]">노트를 불러오는 중...</p>
          </div>
        </div>
      )}

      {/* 에러 */}
      {isError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-sm text-[#DC2626]">
          ⚠️ 노트를 불러오지 못했습니다. 백엔드 서버가 실행 중인지 확인하세요.
        </div>
      )}

      {/* 노트 목록 */}
      {!isLoading && !isError && (
        <div className="space-y-4">
          {filtered.map((note) => {
            const src = SOURCE_LABELS[note.sourceType]
            const isConfirming = confirmDeleteId === note.id

            return (
              <Card key={note.id}>
                <CardHeader>
                  <div className="flex items-start justify-between gap-2 flex-wrap">
                    <CardTitle className="text-lg">{note.title}</CardTitle>
                    <div className="flex gap-2 items-center flex-shrink-0">
                      <Badge variant={src.variant}>{src.label}</Badge>
                      {note.tags.length > 0 && (
                        <span className="text-xs text-[#9CA3AF]">{note.tags.length}개 태그</span>
                      )}
                    </div>
                  </div>
                </CardHeader>

                <CardBody>
                  <p className="text-sm text-[#374151] leading-relaxed line-clamp-3 whitespace-pre-wrap">
                    {note.content}
                  </p>
                  {note.tags.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-3">
                      {note.tags.map((tag) => (
                        <Badge key={tag} variant="outline">#{tag}</Badge>
                      ))}
                    </div>
                  )}
                  <p className="text-xs text-[#9CA3AF] mt-3">
                    {new Date(note.createdAt).toLocaleDateString('ko-KR', {
                      year: 'numeric', month: 'long', day: 'numeric',
                    })}
                  </p>
                </CardBody>

                <CardFooter>
                  <Button variant="ghost" size="sm">편집</Button>
                  <Button variant="ghost" size="sm">🔁 복습 카드 생성</Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    disabled={isDeleting}
                    className={`ml-auto transition-colors ${
                      isConfirming
                        ? 'bg-[#FEE2E2] text-[#DC2626] hover:bg-[#FECACA]'
                        : 'text-[#DC2626] hover:bg-red-50'
                    }`}
                    onClick={() => handleDelete(note.id)}
                  >
                    {isConfirming ? '한 번 더 클릭하면 삭제됩니다' : '삭제'}
                  </Button>
                </CardFooter>
              </Card>
            )
          })}
        </div>
      )}

      {/* 빈 상태 */}
      {!isLoading && !isError && filtered.length === 0 && (
        <div className="text-center py-20 space-y-3">
          <div className="text-5xl">📝</div>
          <p className="text-lg font-medium text-[#374151]">
            {search ? '검색 결과가 없습니다' : '아직 저장된 노트가 없습니다'}
          </p>
          <p className="text-sm text-[#9CA3AF]">
            {search
              ? '다른 검색어를 입력해보세요.'
              : 'AI 챗봇 답변 아래의 "📝 노트에 저장" 버튼으로 저장하세요.'}
          </p>
          {search && (
            <button
              onClick={() => setSearch('')}
              className="text-sm text-[#2563EB] hover:underline"
            >
              검색 초기화
            </button>
          )}
        </div>
      )}
    </div>
  )
}

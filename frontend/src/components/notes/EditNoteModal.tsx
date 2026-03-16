import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Input, Textarea } from '@/components/ui'
import { notesApi } from '@/lib/api'
import { useNotesStore } from '@/stores/notesStore'

export function EditNoteModal() {
  const { editModalOpen, editingNote, closeEditModal } = useNotesStore()
  const queryClient = useQueryClient()

  const [title, setTitle]     = useState('')
  const [content, setContent] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [tags, setTags]       = useState<string[]>([])
  const [error, setError]     = useState('')

  useEffect(() => {
    if (editModalOpen && editingNote) {
      setTitle(editingNote.title)
      setContent(editingNote.content)
      setTags(editingNote.tags)
      setTagInput('')
      setError('')
    }
  }, [editModalOpen, editingNote])

  const { mutate: save, isPending } = useMutation({
    mutationFn: () =>
      notesApi.update(editingNote!.id, {
        title: title.trim(),
        content: content.trim(),
        tags,
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notes'] })
      closeEditModal()
    },
    onError: () => setError('저장에 실패했습니다. 다시 시도해주세요.'),
  })

  const handleTagKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if ((e.key === 'Enter' || e.key === ',') && tagInput.trim()) {
      e.preventDefault()
      const t = tagInput.trim().replace(/^#/, '')
      if (t && !tags.includes(t)) setTags((p) => [...p, t])
      setTagInput('')
    } else if (e.key === 'Backspace' && !tagInput && tags.length > 0) {
      setTags((p) => p.slice(0, -1))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim())   { setError('제목을 입력해주세요.'); return }
    if (!content.trim()) { setError('내용을 입력해주세요.'); return }
    setError('')
    save()
  }

  if (!editModalOpen || !editingNote) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm" onClick={closeEditModal} aria-hidden />
      <div role="dialog" aria-modal="true" aria-label="노트 편집"
           className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col">

          {/* 헤더 */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#E5E7EB]">
            <h2 className="text-lg font-semibold text-[#111827]">노트 편집</h2>
            <button onClick={closeEditModal} aria-label="닫기"
                    className="p-2 rounded-lg text-[#6B7280] hover:bg-[#F3F4F6] transition-colors">✕</button>
          </div>

          {/* 폼 */}
          <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            <Input label="제목" value={title} onChange={(e) => setTitle(e.target.value)} autoFocus />

            <Textarea label="내용" value={content}
                      onChange={(e) => setContent(e.target.value)}
                      className="min-h-[180px] text-xs leading-relaxed" />

            {/* 태그 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-[#374151]">
                태그 <span className="text-[#9CA3AF] font-normal">(Enter 또는 쉼표로 추가)</span>
              </label>
              <div
                className="min-h-[44px] w-full px-3 py-2 rounded-lg border border-[#D1D5DB] bg-white
                           flex flex-wrap gap-1.5 items-center cursor-text
                           focus-within:border-[#2563EB] focus-within:outline-2 focus-within:outline-[#2563EB]/20"
                onClick={(e) => (e.currentTarget.querySelector('input') as HTMLInputElement)?.focus()}
              >
                {tags.map((tag) => (
                  <span key={tag}
                        className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#EFF6FF] text-[#2563EB] rounded-full text-xs font-medium">
                    #{tag}
                    <button type="button" onClick={() => setTags((p) => p.filter((t) => t !== tag))}
                            className="hover:text-[#1D4ED8]" aria-label={`${tag} 제거`}>×</button>
                  </span>
                ))}
                <input
                  value={tagInput} onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  placeholder={tags.length === 0 ? '태그 입력...' : ''}
                  className="flex-1 min-w-[120px] outline-none text-sm text-[#111827] bg-transparent placeholder:text-[#9CA3AF]"
                />
              </div>
            </div>

            {error && <p className="text-sm text-[#DC2626] bg-red-50 px-3 py-2 rounded-lg">{error}</p>}
          </form>

          {/* 푸터 */}
          <div className="px-6 py-4 border-t border-[#E5E7EB] flex gap-3 justify-end">
            <Button variant="secondary" onClick={closeEditModal} disabled={isPending}>취소</Button>
            <Button onClick={handleSubmit as never} loading={isPending}>저장하기</Button>
          </div>
        </div>
      </div>
    </>
  )
}

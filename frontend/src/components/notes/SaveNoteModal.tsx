/**
 * SaveNoteModal — AI 답변 / 챕터 요약을 노트로 저장하는 모달
 * useMutation(notesApi.create) + useNotesStore
 */

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Input, Textarea } from '@/components/ui'
import { notesApi } from '@/lib/api'
import { useNotesStore } from '@/stores/notesStore'
import type { Note } from '@/types'

const SOURCE_LABELS: Record<Note['sourceType'], string> = {
  ai_chat:         'AI 답변',
  chapter_summary: '챕터 요약',
  manual:          '직접 작성',
}

export function SaveNoteModal() {
  const { saveModalOpen, pendingSave, closeSaveModal } = useNotesStore()
  const queryClient = useQueryClient()

  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tagInput, setTagInput] = useState('')
  const [tags, setTags] = useState<string[]>([])
  const [error, setError] = useState('')

  // 모달이 열릴 때 초기값 설정
  useEffect(() => {
    if (saveModalOpen && pendingSave) {
      setTitle(pendingSave.suggestedTitle ?? '')
      setContent(pendingSave.content)
      setTags([])
      setTagInput('')
      setError('')
    }
  }, [saveModalOpen, pendingSave])

  const { mutate: saveNote, isPending } = useMutation({
    mutationFn: () =>
      notesApi.create({
        title: title.trim(),
        content: content.trim(),
        source_type: pendingSave?.sourceType ?? 'manual',
        chapter_id: pendingSave?.chapterId,
        tags,
      }),
    onSuccess: () => {
      // 노트 목록 캐시 무효화
      queryClient.invalidateQueries({ queryKey: ['notes'] })
      closeSaveModal()
    },
    onError: () => {
      setError('저장에 실패했습니다. 서버 연결을 확인해주세요.')
    },
  })

  const handleTagKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if ((e.key === 'Enter' || e.key === ',') && tagInput.trim()) {
      e.preventDefault()
      const newTag = tagInput.trim().replace(/^#/, '')
      if (newTag && !tags.includes(newTag)) {
        setTags((prev) => [...prev, newTag])
      }
      setTagInput('')
    } else if (e.key === 'Backspace' && !tagInput && tags.length > 0) {
      setTags((prev) => prev.slice(0, -1))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!title.trim()) { setError('제목을 입력해주세요.'); return }
    if (!content.trim()) { setError('내용을 입력해주세요.'); return }
    setError('')
    saveNote()
  }

  if (!saveModalOpen) return null

  return (
    <>
      {/* 오버레이 */}
      <div
        className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
        onClick={closeSaveModal}
        aria-hidden
      />

      {/* 모달 */}
      <div
        role="dialog"
        aria-modal="true"
        aria-label="노트 저장"
        className="fixed inset-0 z-50 flex items-center justify-center p-4"
      >
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col">
          {/* 헤더 */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#E5E7EB]">
            <div>
              <h2 className="text-lg font-semibold text-[#111827]">노트에 저장</h2>
              {pendingSave && (
                <p className="text-xs text-[#6B7280] mt-0.5">
                  출처: {SOURCE_LABELS[pendingSave.sourceType]}
                </p>
              )}
            </div>
            <button
              onClick={closeSaveModal}
              aria-label="닫기"
              className="p-2 rounded-lg text-[#6B7280] hover:bg-[#F3F4F6] transition-colors"
            >
              ✕
            </button>
          </div>

          {/* 폼 */}
          <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            <Input
              label="제목"
              placeholder="예: β-차단제 작용 메커니즘"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              autoFocus
            />

            <Textarea
              label="내용"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="min-h-[160px] text-xs leading-relaxed"
            />

            {/* 태그 입력 */}
            <div className="space-y-1.5">
              <label className="text-sm font-medium text-[#374151]">
                태그 <span className="text-[#9CA3AF] font-normal">(Enter 또는 쉼표로 추가)</span>
              </label>
              <div
                className="min-h-[44px] w-full px-3 py-2 rounded-lg border border-[#D1D5DB] bg-white
                           flex flex-wrap gap-1.5 items-center cursor-text
                           focus-within:border-[#2563EB] focus-within:outline-2 focus-within:outline-[#2563EB]/20"
                onClick={(e) => {
                  const input = (e.currentTarget as HTMLElement).querySelector('input')
                  input?.focus()
                }}
              >
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center gap-1 px-2 py-0.5 bg-[#EFF6FF] text-[#2563EB]
                               rounded-full text-xs font-medium"
                  >
                    #{tag}
                    <button
                      type="button"
                      onClick={() => setTags((prev) => prev.filter((t) => t !== tag))}
                      className="hover:text-[#1D4ED8] leading-none"
                      aria-label={`${tag} 태그 제거`}
                    >
                      ×
                    </button>
                  </span>
                ))}
                <input
                  type="text"
                  value={tagInput}
                  onChange={(e) => setTagInput(e.target.value)}
                  onKeyDown={handleTagKeyDown}
                  placeholder={tags.length === 0 ? 'β-차단제, 항고혈압, 심혈관...' : ''}
                  className="flex-1 min-w-[120px] outline-none text-sm text-[#111827] bg-transparent placeholder:text-[#9CA3AF]"
                />
              </div>
            </div>

            {error && (
              <p className="text-sm text-[#DC2626] bg-red-50 px-3 py-2 rounded-lg">{error}</p>
            )}
          </form>

          {/* 푸터 */}
          <div className="px-6 py-4 border-t border-[#E5E7EB] flex gap-3 justify-end">
            <Button variant="secondary" onClick={closeSaveModal} disabled={isPending}>
              취소
            </Button>
            <Button onClick={handleSubmit as never} loading={isPending}>
              저장하기
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}

/**
 * CreateCardModal — 노트에서 SM-2 복습 카드 생성
 * front(질문) / back(답변) 편집 후 POST /api/review/cards
 */

import { useState, useEffect } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { Button, Textarea } from '@/components/ui'
import { reviewApi } from '@/lib/api'
import { useNotesStore } from '@/stores/notesStore'

export function CreateCardModal() {
  const { createCardModalOpen, cardSourceNote, closeCreateCardModal } = useNotesStore()
  const queryClient = useQueryClient()

  const [front, setFront] = useState('')
  const [back, setBack]   = useState('')
  const [error, setError] = useState('')

  // 노트 내용을 기반으로 초기 front/back 자동 제안
  useEffect(() => {
    if (createCardModalOpen && cardSourceNote) {
      setFront(cardSourceNote.title)
      // 첫 200자를 back으로 제안
      setBack(cardSourceNote.content.slice(0, 300).trim())
      setError('')
    }
  }, [createCardModalOpen, cardSourceNote])

  const { mutate: createCard, isPending } = useMutation({
    mutationFn: () =>
      reviewApi.createCard({
        note_id: cardSourceNote!.id,
        front: front.trim(),
        back: back.trim(),
      }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['review-due'] })
      queryClient.invalidateQueries({ queryKey: ['review-stats'] })
      closeCreateCardModal()
    },
    onError: () => setError('카드 생성에 실패했습니다. 다시 시도해주세요.'),
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!front.trim()) { setError('앞면(질문)을 입력해주세요.'); return }
    if (!back.trim())  { setError('뒷면(답변)을 입력해주세요.'); return }
    setError('')
    createCard()
  }

  if (!createCardModalOpen || !cardSourceNote) return null

  return (
    <>
      <div className="fixed inset-0 bg-black/40 z-40 backdrop-blur-sm"
           onClick={closeCreateCardModal} aria-hidden />

      <div role="dialog" aria-modal="true" aria-label="복습 카드 생성"
           className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl w-full max-w-lg max-h-[90vh] flex flex-col">

          {/* 헤더 */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-[#E5E7EB]">
            <div>
              <h2 className="text-lg font-semibold text-[#111827]">복습 카드 생성</h2>
              <p className="text-xs text-[#6B7280] mt-0.5">
                노트: <span className="text-[#374151]">{cardSourceNote.title}</span>
              </p>
            </div>
            <button onClick={closeCreateCardModal} aria-label="닫기"
                    className="p-2 rounded-lg text-[#6B7280] hover:bg-[#F3F4F6] transition-colors">✕</button>
          </div>

          {/* SM-2 안내 */}
          <div className="px-6 pt-4">
            <div className="bg-[#EFF6FF] rounded-xl px-4 py-3 text-xs text-[#1E40AF] flex gap-2">
              <span className="text-base">🔁</span>
              <div>
                <p className="font-medium mb-0.5">SM-2 간격 반복 알고리즘</p>
                <p>저장 후 복습 탭에서 기억 강도에 따라 다음 복습 일정이 자동 계산됩니다.</p>
              </div>
            </div>
          </div>

          {/* 폼 */}
          <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto px-6 py-4 space-y-4">

            {/* 앞면 — 질문 */}
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-[#2563EB] text-white text-xs flex items-center justify-center font-bold flex-shrink-0">앞</div>
                <span className="text-sm font-medium text-[#374151]">질문 (카드 앞면)</span>
              </div>
              <Textarea
                value={front}
                onChange={(e) => setFront(e.target.value)}
                placeholder="예: β-차단제의 주요 부작용 3가지는?"
                className="min-h-[90px] text-sm"
              />
            </div>

            {/* 뒷면 — 답변 */}
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-full bg-[#16A34A] text-white text-xs flex items-center justify-center font-bold flex-shrink-0">뒤</div>
                <span className="text-sm font-medium text-[#374151]">답변 (카드 뒷면)</span>
              </div>
              <Textarea
                value={back}
                onChange={(e) => setBack(e.target.value)}
                placeholder="예: 1. 서맥 2. 기관지수축 3. 피로감"
                className="min-h-[140px] text-sm"
              />
            </div>

            {error && <p className="text-sm text-[#DC2626] bg-red-50 px-3 py-2 rounded-lg">{error}</p>}
          </form>

          {/* 푸터 */}
          <div className="px-6 py-4 border-t border-[#E5E7EB] flex gap-3 justify-end">
            <Button variant="secondary" onClick={closeCreateCardModal} disabled={isPending}>취소</Button>
            <Button onClick={handleSubmit as never} loading={isPending}>
              카드 생성하기
            </Button>
          </div>
        </div>
      </div>
    </>
  )
}

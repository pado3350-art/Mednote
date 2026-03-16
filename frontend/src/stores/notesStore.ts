import { create } from 'zustand'
import type { Note } from '@/types'

interface NotesState {
  // "노트에 저장" 모달
  saveModalOpen: boolean
  pendingSave: {
    content: string
    sourceType: Note['sourceType']
    chapterId?: number
    suggestedTitle?: string
  } | null

  // "노트 편집" 모달
  editModalOpen: boolean
  editingNote: Note | null

  // "복습 카드 생성" 모달
  createCardModalOpen: boolean
  cardSourceNote: Note | null

  openSaveModal:       (data: NotesState['pendingSave']) => void
  closeSaveModal:      () => void
  openEditModal:       (note: Note) => void
  closeEditModal:      () => void
  openCreateCardModal: (note: Note) => void
  closeCreateCardModal: () => void
}

export const useNotesStore = create<NotesState>((set) => ({
  saveModalOpen:  false,
  pendingSave:    null,
  editModalOpen:  false,
  editingNote:    null,
  createCardModalOpen: false,
  cardSourceNote: null,

  openSaveModal:  (data) => set({ saveModalOpen: true, pendingSave: data }),
  closeSaveModal: ()     => set({ saveModalOpen: false, pendingSave: null }),

  openEditModal:  (note) => set({ editModalOpen: true, editingNote: note }),
  closeEditModal: ()     => set({ editModalOpen: false, editingNote: null }),

  openCreateCardModal:  (note) => set({ createCardModalOpen: true, cardSourceNote: note }),
  closeCreateCardModal: ()     => set({ createCardModalOpen: false, cardSourceNote: null }),
}))

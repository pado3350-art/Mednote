import { create } from 'zustand'
import type { Note } from '@/types'

interface NotesState {
  // "노트에 저장" 모달 상태
  saveModalOpen: boolean
  pendingSave: {
    content: string
    sourceType: Note['sourceType']
    chapterId?: number
    suggestedTitle?: string
  } | null

  openSaveModal: (data: NotesState['pendingSave']) => void
  closeSaveModal: () => void
}

export const useNotesStore = create<NotesState>((set) => ({
  saveModalOpen: false,
  pendingSave: null,

  openSaveModal: (data) => set({ saveModalOpen: true, pendingSave: data }),
  closeSaveModal: () => set({ saveModalOpen: false, pendingSave: null }),
}))

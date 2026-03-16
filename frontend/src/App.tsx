import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Layout } from '@/components/layout/Layout'
import { SaveNoteModal } from '@/components/notes/SaveNoteModal'
import { EditNoteModal } from '@/components/notes/EditNoteModal'
import { CreateCardModal } from '@/components/notes/CreateCardModal'
import HomePage from '@/pages/HomePage'
import ChaptersPage from '@/pages/ChaptersPage'
import ChapterDetailPage from '@/pages/ChapterDetailPage'
import ChatPage from '@/pages/ChatPage'
import NotesPage from '@/pages/NotesPage'
import ReviewPage from '@/pages/ReviewPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      retry: 1,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {/* 전역 모달 — 라우트와 무관하게 항상 마운트 */}
        <SaveNoteModal />
        <EditNoteModal />
        <CreateCardModal />
        <Routes>
          <Route element={<Layout />}>
            <Route index element={<HomePage />} />
            <Route path="chapters" element={<ChaptersPage />} />
            <Route path="chapters/:id" element={<ChapterDetailPage />} />
            <Route path="chat" element={<ChatPage />} />
            <Route path="notes" element={<NotesPage />} />
            <Route path="review" element={<ReviewPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

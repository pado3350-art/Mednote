import { Outlet } from 'react-router-dom'
import { Navbar } from './Navbar'

export function Layout() {
  return (
    <div className="min-h-screen bg-[#F9FAFB]">
      <Navbar />
      <main className="pt-16 max-w-[1280px] mx-auto px-4 md:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}

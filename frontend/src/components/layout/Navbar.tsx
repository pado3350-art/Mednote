import { NavLink } from 'react-router-dom'
import { cn } from '@/lib/cn'

const navItems = [
  { to: '/chapters', label: '챕터' },
  { to: '/chat',     label: 'AI 챗봇' },
  { to: '/notes',    label: '내 노트' },
  { to: '/review',   label: '복습' },
]

export function Navbar() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white border-b border-[#E5E7EB] h-16">
      <div className="max-w-[1280px] mx-auto px-4 md:px-8 h-full flex items-center justify-between">
        <NavLink to="/" className="flex items-center gap-2">
          <span className="text-xl font-bold text-[#2563EB]">Mednote</span>
          <span className="text-xs text-[#6B7280] hidden sm:inline">약리학 학습</span>
        </NavLink>

        <nav className="flex items-center gap-1">
          {navItems.map(({ to, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-colors duration-150',
                  isActive
                    ? 'bg-[#EFF6FF] text-[#2563EB]'
                    : 'text-[#374151] hover:bg-[#F9FAFB] hover:text-[#111827]',
                )
              }
            >
              {label}
            </NavLink>
          ))}
        </nav>
      </div>
    </header>
  )
}

import { type HTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

type BadgeVariant = 'default' | 'primary' | 'success' | 'warning' | 'error' | 'outline'

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  variant?: BadgeVariant
}

// DESIGN_RULES: 색상 배지엔 항상 흰색 텍스트
const variantClasses: Record<BadgeVariant, string> = {
  default:  'bg-[#F3F4F6] text-[#374151]',
  primary:  'bg-[#2563EB] text-white',
  success:  'bg-[#16A34A] text-white',
  warning:  'bg-[#D97706] text-white',
  error:    'bg-[#DC2626] text-white',
  outline:  'bg-transparent text-[#374151] border border-[#D1D5DB]',
}

function Badge({ className, variant = 'default', children, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
        variantClasses[variant],
        className,
      )}
      {...props}
    >
      {children}
    </span>
  )
}

export { Badge }
export type { BadgeVariant }

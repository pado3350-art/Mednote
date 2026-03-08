import { cn } from '@/lib/cn'

interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

const sizeClasses = {
  sm: 'w-4 h-4 border-2',
  md: 'w-6 h-6 border-2',
  lg: 'w-8 h-8 border-[3px]',
}

function Spinner({ size = 'md', className }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label="로딩 중"
      className={cn(
        'inline-block rounded-full border-[#E5E7EB] border-t-[#2563EB] animate-spin',
        sizeClasses[size],
        className,
      )}
    />
  )
}

export { Spinner }

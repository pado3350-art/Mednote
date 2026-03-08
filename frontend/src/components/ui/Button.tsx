import { forwardRef, type ButtonHTMLAttributes, type ReactElement, cloneElement } from 'react'
import { cn } from '@/lib/cn'

type ButtonVariant = 'primary' | 'secondary' | 'danger' | 'ghost'
type ButtonSize = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  /** Render styles onto child element (e.g. <Link>) */
  asChild?: boolean
}

const variantClasses: Record<ButtonVariant, string> = {
  // DESIGN_RULES: 파란 버튼에는 반드시 흰색 텍스트
  primary:   'bg-[#2563EB] text-white font-semibold hover:bg-[#1D4ED8] active:bg-[#1E40AF]',
  secondary: 'bg-white text-[#374151] font-medium border border-[#D1D5DB] hover:bg-[#F9FAFB]',
  danger:    'bg-[#DC2626] text-white font-semibold hover:bg-[#B91C1C]',
  ghost:     'bg-transparent text-[#2563EB] font-medium hover:bg-[#EFF6FF]',
}

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm rounded-lg min-h-[36px]',
  md: 'px-4 py-2.5 text-sm rounded-lg min-h-[44px]',
  lg: 'px-6 py-3 text-base rounded-xl min-h-[52px]',
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', size = 'md', loading, disabled, children, asChild, ...props }, ref) => {
    const classes = cn(
      'inline-flex items-center justify-center gap-2 transition-colors duration-150',
      'focus-visible:outline-2 focus-visible:outline-[#2563EB] focus-visible:outline-offset-2',
      variantClasses[variant],
      sizeClasses[size],
      (disabled || loading) && 'opacity-50 cursor-not-allowed pointer-events-none',
      className,
    )

    if (asChild && children) {
      const child = children as ReactElement<{ className?: string }>
      return cloneElement(child, { className: cn(classes, child.props.className) })
    }

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={classes}
        {...props}
      >
        {loading && (
          <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        )}
        {children}
      </button>
    )
  }
)
Button.displayName = 'Button'

export { Button }
export type { ButtonProps, ButtonVariant, ButtonSize }

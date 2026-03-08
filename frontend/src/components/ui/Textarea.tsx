import { forwardRef, type TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  hint?: string
}

const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, hint, id, ...props }, ref) => {
    const inputId = id ?? label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-sm font-medium text-[#374151]">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          className={cn(
            'w-full px-3.5 py-2.5 rounded-lg border text-[#111827] bg-white text-sm resize-y min-h-[120px]',
            'placeholder:text-[#9CA3AF] leading-relaxed',
            'transition-colors duration-150',
            error
              ? 'border-[#DC2626] focus:border-[#DC2626] focus:outline-2 focus:outline-[#DC2626]/20'
              : 'border-[#D1D5DB] focus:border-[#2563EB] focus:outline-2 focus:outline-[#2563EB]/20',
            className,
          )}
          {...props}
        />
        {error && <p className="text-xs text-[#DC2626]">{error}</p>}
        {hint && !error && <p className="text-xs text-[#6B7280]">{hint}</p>}
      </div>
    )
  }
)
Textarea.displayName = 'Textarea'

export { Textarea }

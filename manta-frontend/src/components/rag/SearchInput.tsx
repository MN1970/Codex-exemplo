import { Loader2, Search, X } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchInputProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  isLoading?: boolean
  autoFocus?: boolean
  className?: string
}

/**
 * Controlled search box with a leading search icon, a trailing clear
 * button (when there's text) and a trailing spinner while a request is
 * in flight. Debouncing lives in the parent (RAGSearch) — this
 * component only renders the raw, immediate value.
 */
export function SearchInput({
  value,
  onChange,
  placeholder = 'Buscar na base de conhecimento…',
  isLoading = false,
  autoFocus = false,
  className,
}: SearchInputProps) {
  return (
    <div className={cn('relative', className)}>
      <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
      <input
        type="search"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        autoFocus={autoFocus}
        aria-label="Buscar"
        className={cn(
          'flex h-11 w-full rounded-md border border-input bg-transparent pl-9 pr-9 text-sm',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          '[&::-webkit-search-cancel-button]:appearance-none',
        )}
      />
      {isLoading ? (
        <Loader2 className="absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 animate-spin text-muted-foreground" />
      ) : (
        value.length > 0 && (
          <button
            type="button"
            onClick={() => onChange('')}
            aria-label="Limpar busca"
            className="absolute right-2.5 top-1/2 -translate-y-1/2 rounded-sm p-0.5 text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4" />
          </button>
        )
      )}
    </div>
  )
}

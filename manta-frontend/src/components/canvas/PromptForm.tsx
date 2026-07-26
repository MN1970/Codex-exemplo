import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { Send, Square } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export interface PromptFormProps {
  disabled?: boolean
  isStreaming?: boolean
  onSubmit: (prompt: string) => void
  onCancel?: () => void
  placeholder?: string
}

/** Prompt textarea + submit/stop button for the Canvas main panel. */
export function PromptForm({
  disabled = false,
  isStreaming = false,
  onSubmit,
  onCancel,
  placeholder,
}: PromptFormProps) {
  const [prompt, setPrompt] = useState('')

  function submit() {
    const trimmed = prompt.trim()
    if (!trimmed || disabled) return
    onSubmit(trimmed)
    setPrompt('')
  }

  function handleFormSubmit(event: FormEvent) {
    event.preventDefault()
    submit()
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      submit()
    }
  }

  return (
    <form
      onSubmit={handleFormSubmit}
      className="flex flex-col gap-2 sm:flex-row sm:items-end"
    >
      <textarea
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder ?? 'Digite seu prompt… (Enter envia, Shift+Enter quebra linha)'}
        disabled={disabled}
        rows={3}
        aria-label="Prompt para o agente"
        className={cn(
          'flex-1 resize-none rounded-md border border-input bg-transparent px-3 py-2 text-sm',
          'placeholder:text-muted-foreground',
          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
          'disabled:cursor-not-allowed disabled:opacity-50',
        )}
      />
      {isStreaming ? (
        <Button type="button" variant="destructive" onClick={onCancel} className="sm:w-28">
          <Square className="h-4 w-4" />
          Parar
        </Button>
      ) : (
        <Button type="submit" disabled={disabled || !prompt.trim()} className="sm:w-28">
          <Send className="h-4 w-4" />
          Enviar
        </Button>
      )}
    </form>
  )
}

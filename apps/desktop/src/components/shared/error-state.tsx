import { AlertCircle } from "lucide-react"
import { Button } from "@/components/ui/button"

export interface ErrorStateProps {
  title?: string
  description?: string
  onRetry?: () => void
  retryLabel?: string
}

export function ErrorState({
  title = "Ocorreu um erro",
  description = "Não conseguimos carregar as informações solicitadas. Tente novamente.",
  onRetry,
  retryLabel = "Tentar novamente"
}: ErrorStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center min-h-[300px] animate-fade-in">
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-500/10 text-red-500 mb-4 border border-red-500/20">
        <AlertCircle className="h-8 w-8" />
      </div>
      <h3 className="text-lg font-semibold text-white tracking-tight">{title}</h3>
      <p className="mt-2 text-sm text-surface-400 max-w-sm">{description}</p>
      {onRetry && (
        <Button 
          variant="secondary" 
          onClick={onRetry} 
          className="mt-6 border border-surface-700"
        >
          {retryLabel}
        </Button>
      )}
    </div>
  )
}

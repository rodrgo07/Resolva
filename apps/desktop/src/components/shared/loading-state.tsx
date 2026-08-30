import { Loader2 } from "lucide-react"

export interface LoadingStateProps {
  message?: string
}

export function LoadingState({ message = "Carregando informações..." }: LoadingStateProps) {
  return (
    <div className="flex flex-col items-center justify-center p-8 min-h-[300px] text-center animate-fade-in">
      <Loader2 className="h-8 w-8 animate-spin text-accent mb-4" />
      <p className="text-sm font-medium text-text-secondary">{message}</p>
    </div>
  )
}

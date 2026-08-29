import * as React from "react"
import { Loader2 } from "lucide-react"

export function LoadingState({ message = "Carregando..." }: { message?: string }) {
  return (
    <div className="flex flex-col items-center justify-center h-full w-full min-h-[300px] text-surface-400">
      <Loader2 className="h-8 w-8 animate-spin mb-4 text-accent-500" />
      <p className="text-sm">{message}</p>
    </div>
  )
}

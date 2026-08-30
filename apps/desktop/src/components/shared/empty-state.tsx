import * as React from "react"
import { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

export interface EmptyStateProps {
  icon: LucideIcon
  title: string
  description?: string
  action?: React.ReactNode
  className?: string
}

export function EmptyState({ icon: Icon, title, description, action, className }: EmptyStateProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center p-8 text-center h-full min-h-[300px]", className)}>
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-surface-elevated/50 mb-4 ring-1 ring-surface-700">
        <Icon className="h-8 w-8 text-text-secondary" />
      </div>
      <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
      {description && <p className="text-sm text-text-secondary max-w-sm mb-6">{description}</p>}
      {action && <div>{action}</div>}
    </div>
  )
}

import * as React from "react"
import { cn } from "@/lib/utils"

export interface ProgressProps extends React.HTMLAttributes<HTMLDivElement> {
  value: number
  label?: string
  size?: "sm" | "md"
  showLabel?: boolean
}

export const Progress = React.forwardRef<HTMLDivElement, ProgressProps>(
  ({ className, value, label, size = "md", showLabel, ...props }, ref) => {
    const safeValue = Math.min(Math.max(value, 0), 100)
    
    return (
      <div ref={ref} className={cn("w-full", className)} {...props}>
        {(label || showLabel) && (
          <div className="flex justify-between items-center mb-1 text-sm">
            {label && <span className="font-medium text-surface-200">{label}</span>}
            {showLabel && <span className="text-surface-400">{Math.round(safeValue)}%</span>}
          </div>
        )}
        <div 
          className={cn(
            "w-full bg-surface-800 overflow-hidden rounded-full",
            size === "sm" ? "h-1.5" : "h-3"
          )}
        >
          <div
            className="h-full bg-accent-600 transition-all duration-500 ease-in-out shadow-[0_0_10px_rgba(var(--color-accent-600),0.5)]"
            style={{ width: `${safeValue}%` }}
          />
        </div>
      </div>
    )
  }
)
Progress.displayName = "Progress"

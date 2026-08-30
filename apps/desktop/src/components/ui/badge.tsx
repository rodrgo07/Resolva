import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-accent text-text-primary hover:bg-accent",
        secondary:
          "border-transparent bg-surface-hover text-text-primary hover:bg-surface-hover",
        success:
          "border-transparent bg-green-600 text-text-primary hover:bg-green-700",
        warning:
          "border-transparent bg-yellow-600 text-text-primary hover:bg-yellow-700",
        error:
          "border-transparent bg-red-600 text-text-primary hover:bg-red-700",
        outline: "text-text-primary border-border",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }

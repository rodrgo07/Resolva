import { useState, useRef, ReactNode } from "react"
import { createPortal } from "react-dom"

export interface TooltipProps {
  children: ReactNode
  content: string
  position?: "top" | "bottom" | "left" | "right"
}

export function Tooltip({ children, content, position = "top" }: TooltipProps) {
  const [isVisible, setIsVisible] = useState(false)
  const [coords, setCoords] = useState({ x: 0, y: 0 })
  const childRef = useRef<HTMLDivElement>(null)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)

  const showTooltip = () => {
    timeoutRef.current = setTimeout(() => {
      if (childRef.current) {
        const rect = childRef.current.getBoundingClientRect()
        setCoords({
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2,
        })
        setIsVisible(true)
      }
    }, 300)
  }

  const hideTooltip = () => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    setIsVisible(false)
  }

  const getPositionStyles = () => {
    switch (position) {
      case "top":
        return { bottom: `calc(100vh - ${coords.y - 20}px)`, left: coords.x, transform: 'translateX(-50%)' }
      case "bottom":
        return { top: coords.y + 20, left: coords.x, transform: 'translateX(-50%)' }
      case "left":
        return { right: `calc(100vw - ${coords.x - 20}px)`, top: coords.y, transform: 'translateY(-50%)' }
      case "right":
        return { left: coords.x + 20, top: coords.y, transform: 'translateY(-50%)' }
    }
  }

  return (
    <>
      <div
        ref={childRef}
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        className="inline-block"
      >
        {children}
      </div>
      {isVisible && typeof document !== "undefined" && createPortal(
        <div
          className="fixed z-50 animate-fade-in pointer-events-none"
          style={getPositionStyles()}
        >
          <div className="rounded-md bg-surface-800 px-2.5 py-1.5 text-xs font-medium text-white shadow-xl border border-surface-700">
            {content}
          </div>
        </div>,
        document.body
      )}
    </>
  )
}

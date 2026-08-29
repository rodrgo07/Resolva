import { createContext, useContext, useState, useRef, useEffect, ReactNode, isValidElement, cloneElement, ReactElement, MouseEvent as ReactMouseEvent } from "react"
import { cn } from "@/lib/utils"

interface DropdownContextType {
  isOpen: boolean
  setIsOpen: (val: boolean) => void
  toggle: () => void
}

const DropdownContext = createContext<DropdownContextType>({
  isOpen: false,
  setIsOpen: () => {},
  toggle: () => {}
})

export function Dropdown({ children }: { children: ReactNode }) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  return (
    <DropdownContext.Provider value={{ isOpen, setIsOpen, toggle: () => setIsOpen(!isOpen) }}>
      <div className="relative inline-block text-left" ref={dropdownRef}>
        {children}
      </div>
    </DropdownContext.Provider>
  )
}

export function DropdownTrigger({ children, asChild }: { children: ReactNode, asChild?: boolean }) {
  const { toggle } = useContext(DropdownContext)
  
  if (asChild && isValidElement(children)) {
    const childElement = children as ReactElement<{ onClick?: (e: ReactMouseEvent) => void }>
    return cloneElement(childElement, {
      onClick: (e: ReactMouseEvent) => {
        if (childElement.props?.onClick) childElement.props.onClick(e)
        toggle()
      }
    })
  }

  return (
    <div onClick={toggle} className="cursor-pointer">
      {children}
    </div>
  )
}

export function DropdownContent({ children, className, align = "end" }: { children: ReactNode, className?: string, align?: "start"|"end" }) {
  const { isOpen } = useContext(DropdownContext)

  if (!isOpen) return null

  return (
    <div 
      className={cn(
        "absolute z-50 mt-2 min-w-[8rem] overflow-hidden rounded-md border border-surface-700 bg-surface-900/95 glass-card p-1 text-white shadow-md animate-slide-up",
        align === "end" ? "right-0" : "left-0",
        className
      )}
    >
      {children}
    </div>
  )
}

export function DropdownItem({ 
  children, 
  onClick, 
  className,
  disabled
}: { 
  children: ReactNode, 
  onClick?: () => void, 
  className?: string,
  disabled?: boolean
}) {
  const { setIsOpen } = useContext(DropdownContext)

  return (
    <button
      disabled={disabled}
      onClick={() => {
        if (disabled) return
        if (onClick) onClick()
        setIsOpen(false)
      }}
      className={cn(
        "relative flex w-full cursor-pointer select-none items-center rounded-sm px-2 py-1.5 text-sm outline-none transition-colors hover:bg-surface-800 focus:bg-surface-800 disabled:pointer-events-none disabled:opacity-50",
        className
      )}
    >
      {children}
    </button>
  )
}

export function DropdownSeparator({ className }: { className?: string }) {
  return <div className={cn("-mx-1 my-1 h-px bg-surface-800", className)} />
}

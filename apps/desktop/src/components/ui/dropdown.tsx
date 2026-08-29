import * as React from "react"
import { createPortal } from "react-dom"
import { cn } from "@/lib/utils"

interface DropdownContextType {
  isOpen: boolean
  setIsOpen: (val: boolean) => void
  toggle: () => void
}

const DropdownContext = React.createContext<DropdownContextType>({
  isOpen: false,
  setIsOpen: () => {},
  toggle: () => {}
})

export function Dropdown({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = React.useState(false)
  const dropdownRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
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

export function DropdownTrigger({ children, asChild }: { children: React.ReactNode, asChild?: boolean }) {
  const { toggle } = React.useContext(DropdownContext)
  
  if (asChild && React.isValidElement(children)) {
    return React.cloneElement(children as React.ReactElement, {
      onClick: (e: any) => {
        if (children.props.onClick) children.props.onClick(e)
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

export function DropdownContent({ children, className, align = "end" }: { children: React.ReactNode, className?: string, align?: "start"|"end" }) {
  const { isOpen } = React.useContext(DropdownContext)
  
  if (!isOpen) return null

  return (
    <div 
      className={cn(
        "absolute z-50 mt-2 min-w-[8rem] rounded-md border border-surface-700 bg-surface-900/95 glass-card shadow-lg animate-fade-in p-1",
        align === "end" ? "right-0" : "left-0",
        className
      )}
    >
      {children}
    </div>
  )
}

export function DropdownItem({ children, onClick, icon, className }: { children: React.ReactNode, onClick?: () => void, icon?: React.ReactNode, className?: string }) {
  const { setIsOpen } = React.useContext(DropdownContext)
  
  return (
    <button
      className={cn(
        "flex w-full items-center gap-2 rounded-sm px-2 py-1.5 text-sm text-surface-200 outline-none hover:bg-surface-800 hover:text-white transition-colors focus:bg-surface-800",
        className
      )}
      onClick={(e) => {
        if(onClick) onClick()
        setIsOpen(false)
      }}
    >
      {icon && <span className="text-surface-400">{icon}</span>}
      {children}
    </button>
  )
}

export function DropdownSeparator() {
  return <div className="my-1 h-px bg-surface-800" />
}

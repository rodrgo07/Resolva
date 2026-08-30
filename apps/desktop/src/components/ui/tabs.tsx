import * as React from "react"
import { cn } from "@/lib/utils"

const TabsContext = React.createContext<{
  activeTab: string
  setActiveTab: (value: string) => void
}>({ activeTab: "", setActiveTab: () => {} })

export function Tabs({ 
  defaultValue, 
  children, 
  className 
}: { 
  defaultValue: string
  children: React.ReactNode
  className?: string 
}) {
  const [activeTab, setActiveTab] = React.useState(defaultValue)

  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={cn("w-full", className)}>{children}</div>
    </TabsContext.Provider>
  )
}

export function TabsList({ className, children }: { className?: string, children: React.ReactNode }) {
  return (
    <div className={cn("flex items-center gap-4 border-b border-border", className)}>
      {children}
    </div>
  )
}

export function TabsTrigger({ 
  value, 
  children,
  className 
}: { 
  value: string
  children: React.ReactNode
  className?: string
}) {
  const { activeTab, setActiveTab } = React.useContext(TabsContext)
  const isActive = activeTab === value

  return (
    <button
      onClick={() => setActiveTab(value)}
      className={cn(
        "relative pb-3 text-sm font-medium transition-colors hover:text-text-primary",
        isActive ? "text-accent" : "text-text-secondary",
        className
      )}
    >
      {children}
      {isActive && (
        <div className="absolute bottom-0 left-0 h-0.5 w-full bg-accent rounded-t-full" />
      )}
    </button>
  )
}

export function TabsContent({ 
  value, 
  children,
  className
}: { 
  value: string
  children: React.ReactNode
  className?: string
}) {
  const { activeTab } = React.useContext(TabsContext)
  
  if (activeTab !== value) return null
  
  return (
    <div className={cn("mt-4 animate-fade-in", className)}>
      {children}
    </div>
  )
}

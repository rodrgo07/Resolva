import * as React from "react"
import { createPortal } from "react-dom"
import { X, CheckCircle, AlertTriangle, Info, XCircle } from "lucide-react"
import { cn } from "@/lib/utils"

type ToastType = "success" | "error" | "warning" | "info"

interface Toast {
  id: string
  title: string
  description?: string
  type: ToastType
}

interface ToastContextType {
  toast: (options: Omit<Toast, "id">) => void
}

const ToastContext = React.createContext<ToastContextType | undefined>(undefined)

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = React.useState<Toast[]>([])

  const toast = React.useCallback((options: Omit<Toast, "id">) => {
    const id = Math.random().toString(36).substring(2, 9)
    setToasts((prev) => [...prev, { id, ...options }])
    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, 5000)
  }, [])

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
      {typeof document !== "undefined" && createPortal(
        <div className="fixed bottom-0 right-0 z-50 m-6 flex flex-col gap-2 w-full max-w-sm">
          {toasts.map((t) => (
            <div
              key={t.id}
              className="relative overflow-hidden rounded-lg border border-surface-700 bg-surface-900/90 glass-card p-4 shadow-lg animate-slide-in-right"
            >
              <div className="flex gap-3">
                <div className="mt-0.5">
                  {t.type === "success" && <CheckCircle className="h-5 w-5 text-green-500" />}
                  {t.type === "error" && <XCircle className="h-5 w-5 text-red-500" />}
                  {t.type === "warning" && <AlertTriangle className="h-5 w-5 text-yellow-500" />}
                  {t.type === "info" && <Info className="h-5 w-5 text-blue-500" />}
                </div>
                <div className="flex-1">
                  <h3 className="font-medium text-white">{t.title}</h3>
                  {t.description && (
                    <p className="mt-1 text-sm text-surface-300">{t.description}</p>
                  )}
                </div>
                <button
                  onClick={() => removeToast(t.id)}
                  className="text-surface-400 hover:text-white"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
              <div
                className={cn(
                  "absolute bottom-0 left-0 h-1 animate-[progress_5s_linear_forwards]",
                  t.type === "success" && "bg-green-500",
                  t.type === "error" && "bg-red-500",
                  t.type === "warning" && "bg-yellow-500",
                  t.type === "info" && "bg-blue-500"
                )}
                style={{ width: '100%' }}
              />
            </div>
          ))}
          <style>{`
            @keyframes progress {
              from { width: 100%; }
              to { width: 0%; }
            }
          `}</style>
        </div>,
        document.body
      )}
    </ToastContext.Provider>
  )
}

export const useToast = () => {
  const context = React.useContext(ToastContext)
  if (!context) throw new Error("useToast must be used within ToastProvider")
  return context
}

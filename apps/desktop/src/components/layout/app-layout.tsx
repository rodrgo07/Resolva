import * as React from "react"
import { Sidebar } from "./sidebar"
import { Topbar } from "./topbar"
import { CommandPalette } from "./command-palette"
import { useAppStore } from "@/stores/app-store"

import { Suspense, lazy } from "react"
import { LoadingState } from "@/components/shared/loading-state"

const DashboardPage = lazy(() => import("@/features/dashboard/page").then(m => ({ default: m.DashboardPage })))
const TasksPage = lazy(() => import("@/features/tasks/page").then(m => ({ default: m.TasksPage })))
const StudiesPage = lazy(() => import("@/features/studies/page").then(m => ({ default: m.StudiesPage })))
const FinancesPage = lazy(() => import("@/features/finances/page").then(m => ({ default: m.FinancesPage })))
const EmailsPage = lazy(() => import("@/features/emails/page").then(m => ({ default: m.EmailsPage })))
const CalendarPage = lazy(() => import("@/features/calendar/page").then(m => ({ default: m.CalendarPage })))
const AutomationsPage = lazy(() => import("@/features/automations/page").then(m => ({ default: m.AutomationsPage })))
const AIPage = lazy(() => import("@/features/ai/page").then(m => ({ default: m.AIPage })))
const ActivityPage = lazy(() => import("@/features/activity/page").then(m => ({ default: m.ActivityPage })))
const SettingsPage = lazy(() => import("@/features/settings/page").then(m => ({ default: m.SettingsPage })))
const NotificationsPage = lazy(() => import("@/features/notifications/page").then(m => ({ default: m.NotificationsPage })))

const pages: Record<string, React.LazyExoticComponent<React.ComponentType<any>>> = {
  dashboard: DashboardPage,
  tasks: TasksPage,
  studies: StudiesPage,
  finances: FinancesPage,
  emails: EmailsPage,
  calendar: CalendarPage,
  automations: AutomationsPage,
  ai: AIPage,
  activity: ActivityPage,
  settings: SettingsPage,
  notifications: NotificationsPage,
}

export function AppLayout() {
  const { currentPage, isSearchOpen, setSearchOpen } = useAppStore()
  const CurrentPageComponent = pages[currentPage] || DashboardPage

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-surface-950 text-white font-sans selection:bg-accent-500/30">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden relative">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-8 relative z-0">
          <div className="max-w-6xl mx-auto">
            <Suspense fallback={<LoadingState message="Carregando módulo..." />}>
              <CurrentPageComponent />
            </Suspense>
          </div>
        </main>
      </div>
      <CommandPalette isOpen={isSearchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  )
}

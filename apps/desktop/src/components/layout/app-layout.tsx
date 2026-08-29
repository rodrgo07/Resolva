import * as React from "react"
import { Sidebar } from "./sidebar"
import { Topbar } from "./topbar"
import { CommandPalette } from "./command-palette"
import { useAppStore } from "@/stores/app-store"

import { DashboardPage } from "@/features/dashboard/page"
import { TasksPage } from "@/features/tasks/page"
import { StudiesPage } from "@/features/studies/page"
import { FinancesPage } from "@/features/finances/page"
import { EmailsPage } from "@/features/emails/page"
import { CalendarPage } from "@/features/calendar/page"
import { AutomationsPage } from "@/features/automations/page"
import { AIPage } from "@/features/ai/page"
import { ActivityPage } from "@/features/activity/page"
import { SettingsPage } from "@/features/settings/page"
import { NotificationsPage } from "@/features/notifications/page"

const pages: Record<string, React.ComponentType> = {
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
            <CurrentPageComponent />
          </div>
        </main>
      </div>
      <CommandPalette isOpen={isSearchOpen} onClose={() => setSearchOpen(false)} />
    </div>
  )
}

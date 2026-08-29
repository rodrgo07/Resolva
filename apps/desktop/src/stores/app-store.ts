import { create } from "zustand";

type Page =
  | "dashboard"
  | "tasks"
  | "studies"
  | "finances"
  | "emails"
  | "calendar"
  | "automations"
  | "ai"
  | "activity"
  | "settings"
  | "notifications";

interface AppState {
  // Navigation
  currentPage: Page;
  setCurrentPage: (page: Page) => void;

  // Search
  isSearchOpen: boolean;
  setSearchOpen: (open: boolean) => void;
  toggleSearch: () => void;

  // Sidebar
  isSidebarCollapsed: boolean;
  setSidebarCollapsed: (collapsed: boolean) => void;
  toggleSidebar: () => void;

  // Backend status
  backendStatus: "connecting" | "connected" | "disconnected";
  setBackendStatus: (status: "connecting" | "connected" | "disconnected") => void;

  // User
  userName: string;
  setUserName: (name: string) => void;
}

export const useAppStore = create<AppState>((set) => ({
  // Navigation
  currentPage: "dashboard",
  setCurrentPage: (page) => set({ currentPage: page }),

  // Search
  isSearchOpen: false,
  setSearchOpen: (open) => set({ isSearchOpen: open }),
  toggleSearch: () => set((s) => ({ isSearchOpen: !s.isSearchOpen })),

  // Sidebar
  isSidebarCollapsed: false,
  setSidebarCollapsed: (collapsed) => set({ isSidebarCollapsed: collapsed }),
  toggleSidebar: () => set((s) => ({ isSidebarCollapsed: !s.isSidebarCollapsed })),

  // Backend status
  backendStatus: "connecting",
  setBackendStatus: (status) => set({ backendStatus: status }),

  // User
  userName: "Rodrigo",
  setUserName: (name) => set({ userName: name }),
}));

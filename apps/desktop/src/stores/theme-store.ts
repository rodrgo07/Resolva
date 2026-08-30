import { create } from "zustand";
import { persist } from "zustand/middleware";

export type ThemeMode = "resolva" | "dark" | "white" | "red" | "green" | "system";

interface ThemeState {
  theme: ThemeMode;
  setTheme: (theme: ThemeMode) => void;
  reduceMotion: boolean;
  setReduceMotion: (reduce: boolean) => void;
  compactSidebar: boolean;
  setCompactSidebar: (compact: boolean) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: "resolva",
      setTheme: (theme) => {
        set({ theme });
        applyThemeClass(theme);
      },
      reduceMotion: false,
      setReduceMotion: (reduceMotion) => set({ reduceMotion }),
      compactSidebar: false,
      setCompactSidebar: (compactSidebar) => set({ compactSidebar })
    }),
    {
      name: "resolva-theme-settings"
    }
  )
);

export function applyThemeClass(theme: ThemeMode) {
  const root = document.documentElement;
  root.classList.remove("theme-resolva", "theme-dark", "theme-white", "theme-red", "theme-green");

  let activeTheme = theme;
  if (theme === "system") {
    activeTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "white";
  }

  root.classList.add("theme-" + activeTheme);
}


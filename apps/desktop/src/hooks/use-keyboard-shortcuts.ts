import { useEffect, useCallback } from "react";
import { useAppStore } from "@/stores/app-store";

export function useKeyboardShortcuts() {
  const { toggleSearch, setCurrentPage } = useAppStore();

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      // Ctrl+K — Open search
      if (e.ctrlKey && e.key === "k") {
        e.preventDefault();
        toggleSearch();
      }

      // Ctrl+N — New task (navigate to tasks)
      if (e.ctrlKey && e.key === "n") {
        e.preventDefault();
        setCurrentPage("tasks");
      }

      // Ctrl+Shift+A — Open AI
      if (e.ctrlKey && e.shiftKey && e.key === "A") {
        e.preventDefault();
        setCurrentPage("ai");
      }
    },
    [toggleSearch, setCurrentPage]
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);
}

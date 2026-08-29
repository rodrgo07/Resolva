import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { useBackendHealth } from "@/hooks/use-backend-health";
import { AppLayout } from "@/components/layout/app-layout";
import { ToastProvider } from "@/components/ui/toast";

export default function App() {
  useKeyboardShortcuts();
  useBackendHealth();

  return (
    <ToastProvider>
      <AppLayout />
    </ToastProvider>
  );
}

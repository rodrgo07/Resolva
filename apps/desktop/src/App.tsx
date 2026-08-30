import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { AppLayout } from "@/components/layout/app-layout";
import { ToastProvider } from "@/components/ui/toast";
import { StartupManager } from "@/components/startup/StartupManager";
import { AuthGuard } from "@/components/auth/AuthGuard";

export default function App() {
  useKeyboardShortcuts();

  return (
    <ToastProvider>
      <StartupManager>
        <AuthGuard>
          <AppLayout />
        </AuthGuard>
      </StartupManager>
    </ToastProvider>
  );
}


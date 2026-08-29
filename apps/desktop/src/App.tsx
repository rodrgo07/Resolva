import { useKeyboardShortcuts } from "@/hooks/use-keyboard-shortcuts";
import { AppLayout } from "@/components/layout/app-layout";
import { ToastProvider } from "@/components/ui/toast";

export default function App() {
  useKeyboardShortcuts();

  return (
    <ToastProvider>
      <AppLayout />
    </ToastProvider>
  );
}

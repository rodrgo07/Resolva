import { ReactNode } from "react";

interface StartupManagerProps {
  children: ReactNode;
}

export function StartupManager({ children }: StartupManagerProps) {
  return <>{children}</>;
}

import { ReactNode } from "react";
import { useAuthStore } from "@/stores/auth-store";

interface AuthGuardProps {
  children: ReactNode;
}

export function AuthGuard({ children }: AuthGuardProps) {
  const { user } = useAuthStore();
  if (!user) return null;
  return <>{children}</>;
}

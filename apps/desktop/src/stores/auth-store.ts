import { create } from "zustand";
import { persist } from "zustand/middleware";

interface User {
  name: string;
  email: string;
}

interface AuthState {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: { name: "Rodrigo", email: "rodrigo@resolva.app" },
      setUser: (user) => set({ user }),
      logout: () => set({ user: null }),
    }),
    {
      name: "resolva-auth",
    }
  )
);

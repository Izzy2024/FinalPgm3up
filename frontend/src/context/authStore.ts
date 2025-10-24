import { create } from "zustand";

interface AuthState {
  token: string | null;
  user: any;
  isAuthenticated: boolean;
  setToken: (token: string) => void;
  setUser: (user: any) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem("access_token"),
  user: null,
  isAuthenticated: !!localStorage.getItem("access_token"),
  setToken: (token: string) => {
    localStorage.setItem("access_token", token);
    set({ token, isAuthenticated: true });
  },
  setUser: (user: any) => set({ user }),
  logout: () => {
    localStorage.removeItem("access_token");
    set({ token: null, user: null, isAuthenticated: false });
  },
}));

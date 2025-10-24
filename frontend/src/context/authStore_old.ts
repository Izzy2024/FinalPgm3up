import { create } from "zustand";

interface AuthState {
  token: string | null;
  user: any;
  isAuthenticated: boolean;
  setToken: (token: string) => void;
  setUser: (user: any) => void;
  logout: () => void;
}

const getInitialToken = () => {
  try {
    return typeof window !== 'undefined' ? localStorage.getItem("access_token") : null;
  } catch {
    return null;
  }
};

export const useAuthStore = create<AuthState>((set) => ({
  token: getInitialToken(),
  user: null,
  isAuthenticated: !!getInitialToken(),
  setToken: (token: string) => {
    try {
      localStorage.setItem("access_token", token);
    } catch {
      // localStorage not available
    }
    set({ token, isAuthenticated: true });
  },
  setUser: (user: any) => set({ user }),
  logout: () => {
    try {
      localStorage.removeItem("access_token");
    } catch {
      // localStorage not available
    }
    set({ token: null, user: null, isAuthenticated: false });
  },
}));

"use client";

import { clearTokens, isAuthenticated as checkAuth } from "@/lib/api/auth";
import { getMe } from "@/lib/api/profiles";
import type { UserResponse } from "@/types/user";
import { useRouter } from "next/navigation";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

interface AuthContextValue {
  user: UserResponse | null;
  isAuthenticated: boolean;
  loading: boolean;
  refreshUser: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<UserResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  const refreshUser = useCallback(async () => {
    if (!checkAuth()) {
      setUser(null);
      setAuthenticated(false);
      setLoading(false);
      return;
    }

    try {
      const data = await getMe();
      setUser(data);
      setAuthenticated(true);
    } catch {
      clearTokens();
      setUser(null);
      setAuthenticated(false);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const logout = useCallback(() => {
    clearTokens();
    setUser(null);
    setAuthenticated(false);
    router.push("/login");
  }, [router]);

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: authenticated,
        loading,
        refreshUser,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}

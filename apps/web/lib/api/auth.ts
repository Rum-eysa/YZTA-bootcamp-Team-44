import api from "../api";
import type { TokenResponse, UserCreate, UserResponse } from "@/types/user";

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/api/auth/login", {
    email,
    password,
  });
  return data;
}

export async function register(userData: UserCreate): Promise<UserResponse> {
  const { data } = await api.post<UserResponse>("/api/auth/register", userData);
  return data;
}

export function saveTokens(tokens: TokenResponse) {
  localStorage.setItem("access_token", tokens.access_token);
  localStorage.setItem("refresh_token", tokens.refresh_token);
}

export function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

export function isAuthenticated(): boolean {
  if (typeof window === "undefined") return false;
  return !!localStorage.getItem("access_token");
}

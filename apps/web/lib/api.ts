import axios, { type AxiosError, type InternalAxiosRequestConfig } from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

type RetryConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken =
    typeof window !== "undefined" ? localStorage.getItem("refresh_token") : null;
  if (!refreshToken) return null;

  try {
    const { data } = await axios.post(
      `${API_URL}/api/auth/refresh`,
      { refresh_token: refreshToken },
      { headers: { "Content-Type": "application/json" } }
    );
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    return data.access_token as string;
  } catch {
    return null;
  }
}

function clearSessionAndRedirect(requestUrl: string) {
  if (typeof window === "undefined") return;
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");

  const isAuthPage =
    window.location.pathname === "/login" || window.location.pathname === "/register";
  const isPublicAuthRequest =
    requestUrl.includes("/api/auth/login") ||
    requestUrl.includes("/api/auth/register") ||
    requestUrl.includes("/api/auth/refresh");

  if (!isAuthPage && !isPublicAuthRequest) {
    const currentTarget = `${window.location.pathname}${window.location.search}`;
    window.location.assign(`/login?redirect=${encodeURIComponent(currentTarget)}`);
  }
}

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // FormData'da varsayılan application/json kalırsa multipart boundary bozulur
  if (typeof FormData !== "undefined" && config.data instanceof FormData) {
    const headers = config.headers;
    if (headers && typeof (headers as { set?: unknown }).set === "function") {
      (headers as { set: (k: string, v: unknown) => void }).set("Content-Type", false);
    } else if (headers) {
      delete (headers as Record<string, unknown>)["Content-Type"];
      delete (headers as Record<string, unknown>)["content-type"];
    }
  }
  return config;
});

// Response interceptor: 401 → refresh → retry once
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as RetryConfig | undefined;
    const requestUrl = original?.url ?? "";
    const isPublicAuthRequest =
      requestUrl.includes("/api/auth/login") ||
      requestUrl.includes("/api/auth/register") ||
      requestUrl.includes("/api/auth/refresh") ||
      requestUrl.includes("/api/auth/logout");

    if (
      error.response?.status === 401 &&
      original &&
      !original._retry &&
      !isPublicAuthRequest &&
      typeof window !== "undefined"
    ) {
      original._retry = true;
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }
      const newToken = await refreshPromise;
      if (newToken) {
        original.headers.Authorization = `Bearer ${newToken}`;
        return api(original);
      }
      clearSessionAndRedirect(requestUrl);
    } else if (
      error.response?.status === 401 &&
      !isPublicAuthRequest &&
      typeof window !== "undefined"
    ) {
      clearSessionAndRedirect(requestUrl);
    }
    return Promise.reject(error);
  }
);

export default api;

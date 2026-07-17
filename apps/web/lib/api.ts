import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor to add auth token
api.interceptors.request.use((config) => {
  const token = typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const requestUrl = error.config?.url ?? "";
    const isPublicAuthRequest =
      requestUrl.includes("/api/auth/login") || requestUrl.includes("/api/auth/register");

    if (
      error.response?.status === 401 &&
      !isPublicAuthRequest &&
      typeof window !== "undefined"
    ) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");

      const currentTarget = `${window.location.pathname}${window.location.search}`;
      const isAuthPage =
        window.location.pathname === "/login" || window.location.pathname === "/register";

      if (!isAuthPage) {
        window.location.assign(`/login?redirect=${encodeURIComponent(currentTarget)}`);
      }
    }
    return Promise.reject(error);
  }
);

export default api;

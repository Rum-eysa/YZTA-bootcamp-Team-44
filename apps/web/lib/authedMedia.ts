const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/** API path veya absolute URL'i tam adrese çevirir. */
export function resolveApiUrl(pathOrUrl: string): string {
  if (pathOrUrl.startsWith("http://") || pathOrUrl.startsWith("https://")) {
    return pathOrUrl;
  }
  const base = API_URL.replace(/\/$/, "");
  const path = pathOrUrl.startsWith("/") ? pathOrUrl : `/${pathOrUrl}`;
  return `${base}${path}`;
}

/**
 * JWT ile korumalı medya (CV/avatar) indirir ve blob URL döner.
 * iframe/img src Authorization gönderemediği için blob kullanılır.
 */
export async function fetchAuthedBlobUrl(pathOrUrl: string): Promise<string> {
  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;
  if (!token) {
    throw new Error("Oturum gerekli");
  }
  const response = await fetch(resolveApiUrl(pathOrUrl), {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    throw new Error(`Dosya alınamadı (${response.status})`);
  }
  const blob = await response.blob();
  return URL.createObjectURL(blob);
}

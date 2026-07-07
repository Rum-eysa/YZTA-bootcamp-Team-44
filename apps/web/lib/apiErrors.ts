type ApiErrorPayload = {
  response?: {
    status?: number;
    data?: {
      detail?: string;
      error_code?: string;
    };
  };
};

const QUOTA_PATTERNS = [
  /rate limit/i,
  /quota exceeded/i,
  /daily ai quota/i,
  /ai service rate limit/i,
];

export function getApiErrorMessage(
  err: unknown,
  fallback: string,
  options?: { serviceUnavailable?: string }
): string {
  const response = (err as ApiErrorPayload)?.response;
  const status = response?.status;
  const detail = response?.data?.detail;
  const errorCode = response?.data?.error_code;

  if (status === 429) {
    return "AI servisi istek limitine ulaştı. Lütfen biraz bekleyip tekrar deneyin.";
  }

  if (status === 503 || errorCode === "CV_GENERATION_ERROR") {
    return (
      options?.serviceUnavailable ??
      "Servis şu an kullanılamıyor. Lütfen daha sonra tekrar deneyin."
    );
  }

  if (typeof detail === "string") {
    if (QUOTA_PATTERNS.some((pattern) => pattern.test(detail))) {
      return "Günlük AI kotası doldu veya istek limiti aşıldı. Lütfen daha sonra tekrar deneyin.";
    }
    return detail;
  }

  return fallback;
}

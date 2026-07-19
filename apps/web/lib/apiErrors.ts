type ApiErrorPayload = {
  response?: {
    status?: number;
    data?: {
      detail?: unknown;
      error_code?: string;
    };
  };
};

type ValidationError = {
  loc?: Array<string | number>;
  msg?: string;
};

const QUOTA_PATTERNS = [
  /rate limit/i,
  /quota exceeded/i,
  /daily ai quota/i,
  /ai service rate limit/i,
];

function parseValidationDetail(detail: unknown): string | undefined {
  if (!Array.isArray(detail)) return undefined;

  const messages = detail
    .map((item) => {
      if (typeof item === "string") return item;
      if (!item || typeof item !== "object") return undefined;

      const validationError = item as ValidationError;
      if (typeof validationError.msg !== "string") return undefined;

      const field = validationError.loc?.filter((part) => part !== "body").at(-1);
      return field ? `${String(field)}: ${validationError.msg}` : validationError.msg;
    })
    .filter((message): message is string => Boolean(message));

  return messages.length > 0 ? messages.join(" ") : undefined;
}

export function getApiErrorStatus(err: unknown): number | undefined {
  return (err as ApiErrorPayload)?.response?.status;
}

export function getApiErrorMessage(
  err: unknown,
  fallback: string,
  options?: { network?: string; serviceUnavailable?: string }
): string {
  const response = (err as ApiErrorPayload)?.response;
  const status = response?.status;
  const detail = response?.data?.detail;
  const errorCode = response?.data?.error_code;

  if (status === 429) {
    return "AI servisi istek limitine ulaştı. Lütfen biraz bekleyip tekrar deneyin.";
  }

  if ((status !== undefined && status >= 500) || errorCode === "CV_GENERATION_ERROR") {
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

  const validationMessage = parseValidationDetail(detail);
  if (validationMessage) return validationMessage;

  if (!response) {
    return options?.network ?? "Sunucuya ulaşılamadı. İnternet bağlantınızı kontrol edin.";
  }

  return fallback;
}

"use client";

import { AlertCircle } from "lucide-react";

const DEFAULT_MESSAGE =
  "Bu veri eski. İlan yeniden analiz edildi; güncellemenizi öneririz.";

interface StaleWarningIconProps {
  message?: string;
}

export function StaleWarningIcon({ message = DEFAULT_MESSAGE }: StaleWarningIconProps) {
  return (
    <span
      className="inline-flex shrink-0 text-red-600"
      title={message}
      aria-label={message}
      role="img"
    >
      <AlertCircle className="h-5 w-5" aria-hidden="true" />
    </span>
  );
}

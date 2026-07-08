"use client";

import { cn } from "@/lib/utils";
import { AlertCircle, CheckCircle2, X } from "lucide-react";
import { useEffect } from "react";

type ToastVariant = "error" | "success";

interface ToastProps {
  message?: string;
  variant?: ToastVariant;
  onClose: () => void;
  duration?: number;
}

export function Toast({ message, variant = "error", onClose, duration = 6000 }: ToastProps) {
  useEffect(() => {
    if (!message) return;
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [message, duration, onClose]);

  if (!message) return null;

  const variants: Record<ToastVariant, string> = {
    error: "bg-error-container text-on-error-container",
    success: "bg-secondary-container text-on-secondary-container",
  };

  const Icon = variant === "error" ? AlertCircle : CheckCircle2;

  return (
    <div
      role="alert"
      aria-live="assertive"
      className={cn(
        "fixed bottom-4 right-4 z-50 flex items-start gap-3 max-w-sm rounded-lg px-4 py-3 shadow-lg",
        variants[variant]
      )}
    >
      <Icon className="w-5 h-5 shrink-0 mt-0.5" />
      <span className="text-body-sm flex-1">{message}</span>
      <button
        type="button"
        onClick={onClose}
        aria-label="Bildirimi kapat"
        className="shrink-0 opacity-70 hover:opacity-100 transition-opacity"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
}

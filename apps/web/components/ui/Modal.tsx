"use client";

import { cn } from "@/lib/utils";
import { X } from "lucide-react";
import { useEffect, type ReactNode } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
  className?: string;
}

export function Modal({ open, onClose, title, children, footer, className }: ModalProps) {
  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };

    document.addEventListener("keydown", handleKeyDown);
    document.body.style.overflow = "hidden";

    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-inverse-surface/40"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-title"
        className={cn(
          "relative w-full max-w-lg bg-surface-container-lowest rounded-xl border border-outline-variant shadow-card-hover max-h-[90vh] flex flex-col",
          className
        )}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-outline-variant">
          <h2 id="modal-title" className="text-title-md font-semibold text-on-surface">
            {title}
          </h2>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-lg text-on-surface-variant hover:text-primary hover:bg-surface-container-low transition-colors"
            aria-label="Kapat"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        <div className="px-6 py-4 overflow-y-auto flex-1">{children}</div>
        {footer && (
          <div className="px-6 py-4 border-t border-outline-variant flex justify-end gap-2">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}

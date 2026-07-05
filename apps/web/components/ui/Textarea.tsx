import { cn } from "@/lib/utils";
import { TextareaHTMLAttributes, forwardRef } from "react";

interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  showCount?: boolean;
  maxLength?: number;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, showCount, maxLength, id, value, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, "-");
    const charCount = typeof value === "string" ? value.length : 0;

    return (
      <div className="space-y-1">
        {label && (
          <label htmlFor={inputId} className="block text-label-md text-on-surface-variant">
            {label}
          </label>
        )}
        <textarea
          ref={ref}
          id={inputId}
          value={value}
          maxLength={maxLength}
          className={cn(
            "input-field resize-none min-h-[120px]",
            error && "border-error focus:border-error focus:ring-error/20",
            className
          )}
          {...props}
        />
        <div className="flex justify-between">
          {error ? (
            <p className="text-body-sm text-error">{error}</p>
          ) : (
            <span />
          )}
          {showCount && (
            <p className="text-body-sm text-on-surface-variant">
              {charCount}
              {maxLength ? ` / ${maxLength}` : ""} karakter
            </p>
          )}
        </div>
      </div>
    );
  }
);

Textarea.displayName = "Textarea";

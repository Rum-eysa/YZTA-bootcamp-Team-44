import { cn } from "@/lib/utils";

interface FormErrorProps {
  message?: string;
  className?: string;
}

export function FormError({ message, className }: FormErrorProps) {
  if (!message) return null;

  return (
    <div
      className={cn(
        "rounded-lg border border-error bg-error-container px-4 py-3 text-body-sm text-on-error-container",
        className
      )}
      role="alert"
    >
      {message}
    </div>
  );
}

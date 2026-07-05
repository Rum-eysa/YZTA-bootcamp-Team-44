import { cn } from "@/lib/utils";
import { ButtonHTMLAttributes, forwardRef } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
  loading?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", loading, disabled, children, ...props }, ref) => {
    const variants = {
      primary: "bg-primary-container text-on-primary hover:opacity-90",
      secondary: "bg-secondary-container text-on-secondary-container hover:opacity-90",
      outline: "border border-primary text-primary hover:bg-primary hover:text-on-primary",
    };

    return (
      <button
        ref={ref}
        disabled={disabled || loading}
        className={cn(
          "inline-flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-semibold text-label-md transition-all disabled:opacity-50 disabled:cursor-not-allowed",
          variants[variant],
          className
        )}
        {...props}
      >
        {loading && (
          <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
        )}
        {children}
      </button>
    );
  }
);

Button.displayName = "Button";

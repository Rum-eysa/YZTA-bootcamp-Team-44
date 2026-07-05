import { cn } from "@/lib/utils";
import { Pencil } from "lucide-react";
import { ButtonHTMLAttributes } from "react";

interface SectionEditButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  label?: string;
  showIcon?: boolean;
}

export function SectionEditButton({
  className,
  label = "Düzenle",
  showIcon = false,
  ...props
}: SectionEditButtonProps) {
  return (
    <button
      type="button"
      className={cn(
        "text-primary flex items-center gap-1 hover:bg-surface-container-low px-2 py-1 rounded transition-colors text-label-md font-semibold border border-transparent hover:border-outline-variant",
        className
      )}
      {...props}
    >
      {showIcon && <Pencil className="w-3.5 h-3.5" />}
      {label}
    </button>
  );
}

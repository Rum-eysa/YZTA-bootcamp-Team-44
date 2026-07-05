import { cn } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface SpinnerProps {
  className?: string;
  label?: string;
}

export function Spinner({ className, label }: SpinnerProps) {
  return (
    <div className={cn("flex flex-col items-center justify-center gap-2", className)}>
      <Loader2 className="w-8 h-8 text-primary animate-spin" />
      {label && <p className="text-body-sm text-on-surface-variant">{label}</p>}
    </div>
  );
}

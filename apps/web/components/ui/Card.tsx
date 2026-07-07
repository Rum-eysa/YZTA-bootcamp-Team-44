import { cn } from "@/lib/utils";
import { HTMLAttributes } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  action?: React.ReactNode;
}

export function Card({ className, title, action, children, ...props }: CardProps) {
  return (
    <section
      className={cn(
        "bg-surface-container-lowest rounded-xl p-4 md:p-6 border border-outline-variant",
        className
      )}
      {...props}
    >
      {(title || action) && (
        <div className={cn("flex items-center gap-2 mb-4", title ? "justify-between" : "justify-end")}>
          {title && <h2 className="section-title min-w-0 break-words">{title}</h2>}
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

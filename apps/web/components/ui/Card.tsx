import { cn } from "@/lib/utils";
import { HTMLAttributes, type ReactNode } from "react";

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  title?: string;
  titleAddon?: ReactNode;
  action?: React.ReactNode;
}

export function Card({ className, title, titleAddon, action, children, ...props }: CardProps) {
  return (
    <section
      className={cn(
        "bg-surface-container-lowest rounded-xl p-4 md:p-6 border border-outline-variant",
        className
      )}
      {...props}
    >
      {(title || action) && (
        <div
          className={cn(
            "mb-4 flex flex-wrap items-start gap-x-2 gap-y-2",
            title ? "justify-between" : "justify-end"
          )}
        >
          {title && (
            <div className="flex min-w-0 max-w-full flex-1 flex-col items-start gap-1 sm:flex-row sm:flex-wrap sm:items-baseline sm:gap-x-1.5">
              <h2 className="section-title min-w-0 break-words">{title}</h2>
              {titleAddon}
            </div>
          )}
          {action && <div className="shrink-0">{action}</div>}
        </div>
      )}
      {children}
    </section>
  );
}

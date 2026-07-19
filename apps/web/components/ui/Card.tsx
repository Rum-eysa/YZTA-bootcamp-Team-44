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
        <div className={cn("flex items-center gap-2 mb-4", title ? "justify-between" : "justify-end")}>
          {title && (
            <div className="flex min-w-0 items-center gap-2">
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

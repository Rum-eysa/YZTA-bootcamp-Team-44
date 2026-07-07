"use client";

import { AuthGuard } from "@/components/auth/AuthGuard";
import { AppHeader } from "@/components/layout/AppHeader";
import { AppSidebar } from "@/components/layout/AppSidebar";
import { useAuth } from "@/hooks/useAuth";
import { X } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";

interface AppLayoutProps {
  children: ReactNode;
  guard?: boolean;
}

export function AppLayout({ children, guard = true }: AppLayoutProps) {
  const { isAuthenticated } = useAuth();
  const [drawerOpen, setDrawerOpen] = useState(false);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setDrawerOpen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, []);

  const showNav = isAuthenticated;
  const inner = guard ? <AuthGuard>{children}</AuthGuard> : children;

  return (
    <div className="min-h-screen bg-surface-bright flex flex-col">
      <AppHeader onMenuClick={showNav ? () => setDrawerOpen(true) : undefined} />

      <div className="flex flex-1 w-full max-w-container-max mx-auto">
        {showNav && drawerOpen && (
          <div className="fixed inset-0 z-50 md:hidden">
            <div
              className="absolute inset-0 bg-black/40"
              onClick={() => setDrawerOpen(false)}
              aria-hidden="true"
            />
            <div className="absolute left-0 top-0 h-full w-72 max-w-[80%] bg-surface-container-lowest border-r border-outline-variant shadow-card-hover">
              <div className="flex items-center justify-between h-16 px-4 border-b border-outline-variant">
                <span className="font-headline-lg text-headline-lg-mobile font-bold text-primary">
                  CareerTrack
                </span>
                <button
                  type="button"
                  onClick={() => setDrawerOpen(false)}
                  aria-label="Menüyü kapat"
                  className="p-1 text-on-surface-variant hover:text-primary transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <AppSidebar onNavigate={() => setDrawerOpen(false)} />
            </div>
          </div>
        )}

        <main className="flex-1 min-w-0">{inner}</main>
      </div>
    </div>
  );
}

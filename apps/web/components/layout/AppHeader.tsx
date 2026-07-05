"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { useAuth } from "@/hooks/useAuth";
import { LogOut, User } from "lucide-react";

const navItems = [
  { href: "/profile", label: "Profil" },
  { href: "/apply", label: "İlan Ekle" },
];

function getInitials(name: string | null | undefined, email: string) {
  if (name?.trim()) {
    const parts = name.trim().split(/\s+/);
    return parts
      .slice(0, 2)
      .map((p) => p[0]?.toUpperCase())
      .join("");
  }
  return email[0]?.toUpperCase() || "U";
}

export function AppHeader() {
  const pathname = usePathname();
  const { isAuthenticated, user, loading, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const loginHref = `/login?redirect=${encodeURIComponent(pathname)}`;

  return (
    <header className="bg-surface-container-lowest border-b border-outline-variant sticky top-0 z-50 w-full">
      <div className="flex justify-between items-center w-full px-margin-mobile md:px-lg max-w-container-max mx-auto h-16">
        <div className="flex items-center gap-md">
          <Link
            href="/"
            className="font-headline-lg text-headline-lg-mobile md:text-headline-lg font-bold text-primary"
          >
            CareerTrack
          </Link>
        </div>

        {isAuthenticated && (
          <nav className="hidden md:flex gap-lg items-center">
            {navItems.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "font-title-md text-title-md transition-colors",
                  pathname === item.href
                    ? "text-primary"
                    : "text-on-surface-variant hover:text-primary"
                )}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        )}

        <div className="flex items-center gap-sm">
          {!loading && !isAuthenticated && (
            <Link
              href={loginHref}
              className="text-primary font-semibold text-body-sm hover:opacity-80 transition-opacity px-3 py-1.5"
            >
              Giriş Yap
            </Link>
          )}

          {!loading && isAuthenticated && user && (
            <div className="relative" ref={menuRef}>
              <button
                type="button"
                onClick={() => setMenuOpen((v) => !v)}
                className="w-9 h-9 rounded-full overflow-hidden border border-outline-variant bg-primary-container flex items-center justify-center text-on-primary text-label-md font-bold hover:opacity-90 transition-opacity"
                aria-label="Kullanıcı menüsü"
              >
                {getInitials(user.full_name, user.email)}
              </button>
              {menuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-surface-container-lowest border border-outline-variant rounded-xl shadow-card-hover py-1 z-50">
                  <div className="px-4 py-2 border-b border-outline-variant">
                    <p className="text-body-sm font-semibold text-on-surface truncate">
                      {user.full_name || "Kullanıcı"}
                    </p>
                    <p className="text-label-md text-on-surface-variant truncate">{user.email}</p>
                  </div>
                  <Link
                    href="/profile"
                    className="flex items-center gap-2 px-4 py-2 text-body-sm text-on-surface hover:bg-surface-container-low transition-colors"
                    onClick={() => setMenuOpen(false)}
                  >
                    <User className="w-4 h-4" />
                    Profil
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      setMenuOpen(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-2 px-4 py-2 text-body-sm text-error hover:bg-error-container/30 transition-colors"
                  >
                    <LogOut className="w-4 h-4" />
                    Çıkış Yap
                  </button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </header>
  );
}

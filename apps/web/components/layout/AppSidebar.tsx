"use client";

import { cn } from "@/lib/utils";
import { Briefcase, PlusCircle, User } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/profile", label: "Profil", icon: User },
  { href: "/apply", label: "İlan Ekle", icon: PlusCircle },
  { href: "/listings", label: "Başvurulan İlanlar", icon: Briefcase },
];

export function AppSidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col gap-xs p-md" aria-label="Ana navigasyon">
      {navItems.map((item) => {
        const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
        const Icon = item.icon;
        return (
          <Link
            key={item.href}
            href={item.href}
            onClick={onNavigate}
            aria-current={active ? "page" : undefined}
            className={cn(
              "flex items-center gap-3 px-3 py-2.5 rounded-lg text-title-md transition-colors",
              active
                ? "bg-primary-fixed/20 text-primary font-semibold"
                : "text-on-surface-variant hover:bg-surface-container-low hover:text-primary"
            )}
          >
            <Icon className="w-5 h-5 shrink-0" />
            {item.label}
          </Link>
        );
      })}
    </nav>
  );
}

"use client";

import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";

interface AuthAwareLinkProps {
  href: string;
  className?: string;
  children: React.ReactNode;
}

export function AuthAwareLink({ href, className, children }: AuthAwareLinkProps) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <span className={className} aria-hidden="true">
        {children}
      </span>
    );
  }

  const target = isAuthenticated ? href : `/login?redirect=${encodeURIComponent(href)}`;

  return (
    <Link href={target} className={className}>
      {children}
    </Link>
  );
}

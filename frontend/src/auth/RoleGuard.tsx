"use client";

import { ReactNode } from "react";
import { useAuth } from "@/auth/useAuth";

export function RoleGuard({ permission, children, fallback = null }: { permission: string; children: ReactNode; fallback?: ReactNode }) {
  const { hasPermission } = useAuth();
  return hasPermission(permission) ? <>{children}</> : <>{fallback}</>;
}

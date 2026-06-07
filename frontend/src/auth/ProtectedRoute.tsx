"use client";

import { ReactNode, useEffect } from "react";
import { useAuth } from "@/auth/useAuth";
import { LoadingSpinner } from "@/components/common/LoadingSpinner";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isReady } = useAuth();

  useEffect(() => {
    if (isReady && !isAuthenticated) {
      window.location.href = "/login";
    }
  }, [isAuthenticated, isReady]);

  if (!isReady || !isAuthenticated) {
    return <LoadingSpinner label="Checking authentication" />;
  }

  return <>{children}</>;
}

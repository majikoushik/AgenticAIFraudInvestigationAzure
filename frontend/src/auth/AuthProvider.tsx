"use client";

import { createContext, ReactNode, useEffect, useMemo, useState } from "react";
import { MsalProvider } from "@azure/msal-react";
import { AppRole, authMode, rolePermissions } from "@/auth/authConfig";
import { clearLocalUser, demoUsers, getStoredLocalUser, LocalAuthUser, storeLocalUser } from "@/auth/localAuth";
import { msalInstance } from "@/auth/msalInstance";

export type AuthUser = {
  user_id: string;
  display_name: string;
  email: string;
  role: AppRole;
  permissions: string[];
  auth_mode: string;
};

type AuthContextValue = {
  authMode: string;
  user: AuthUser | null;
  isReady: boolean;
  isAuthenticated: boolean;
  loginLocal: (role: AppRole) => void;
  loginEntra: () => void;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
};

export const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (authMode === "local") {
      const stored = getStoredLocalUser();
      if (stored) setUser(toAuthUser(stored));
    } else if (typeof window !== "undefined") {
      const token = window.sessionStorage.getItem("entra_access_token");
      const email = window.sessionStorage.getItem("entra_user_email") ?? "entra_user@example.com";
      const role = (window.sessionStorage.getItem("entra_user_role") as AppRole | null) ?? "FRAUD_ANALYST";
      if (token) setUser({ user_id: email, display_name: email, email, role, permissions: rolePermissions[role] ?? [], auth_mode: "entra" });
    }
    setIsReady(true);
  }, []);

  const value = useMemo<AuthContextValue>(() => ({
    authMode,
    user,
    isReady,
    isAuthenticated: Boolean(user),
    loginLocal: (role: AppRole) => {
      const demo = demoUsers.find((item) => item.role === role) ?? demoUsers[0];
      storeLocalUser(demo);
      setUser(toAuthUser(demo));
    },
    loginEntra: () => {
      // Placeholder for MSAL loginRedirect/loginPopup once Entra app registrations are configured.
      window.location.href = "/login";
    },
    logout: () => {
      clearLocalUser();
      window.sessionStorage.removeItem("entra_access_token");
      setUser(null);
      window.location.href = "/login";
    },
    hasPermission: (permission: string) => Boolean(user?.permissions.includes(permission))
  }), [user]);

  return (
    <MsalProvider instance={msalInstance}>
      <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
    </MsalProvider>
  );
}

function toAuthUser(user: LocalAuthUser): AuthUser {
  return {
    user_id: user.user_id,
    display_name: user.display_name,
    email: user.email,
    role: user.role,
    permissions: rolePermissions[user.role] ?? [],
    auth_mode: "local"
  };
}

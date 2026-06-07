"use client";

import { useAuth } from "@/auth/useAuth";

type HeaderProps = {
  title: string;
  subtitle: string;
};

export function Header({ title, subtitle }: HeaderProps) {
  const { user, logout, authMode } = useAuth();
  return (
    <header className="header">
      <div>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="header-user">
        <span className="header-status">{authMode === "local" ? "Local Auth" : "Entra ID"}</span>
        {user && <span>{user.display_name} | {user.role}</span>}
        {user && <button className="button secondary" onClick={logout}>Logout</button>}
      </div>
    </header>
  );
}

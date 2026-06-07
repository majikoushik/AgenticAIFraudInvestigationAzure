"use client";

import { useEffect, useState } from "react";
import { AppRole, authMode } from "@/auth/authConfig";
import { demoUsers } from "@/auth/localAuth";
import { useAuth } from "@/auth/useAuth";

export default function LoginPage() {
  const { isAuthenticated, loginLocal, loginEntra } = useAuth();
  const [role, setRole] = useState<AppRole>("FRAUD_ANALYST");

  useEffect(() => {
    if (isAuthenticated) {
      window.location.href = "/dashboard";
    }
  }, [isAuthenticated]);

  return (
    <main className="login-shell">
      <section className="login-panel">
        <h1>Agentic AI Fraud Investigation</h1>
        <p>Sign in to continue to the banking operations console.</p>
        {authMode === "local" ? (
          <div className="form-grid">
            <div className="field">
              <label htmlFor="role">Demo role</label>
              <select id="role" value={role} onChange={(event) => setRole(event.target.value as AppRole)}>
                {demoUsers.map((user) => <option key={user.role} value={user.role}>{user.display_name} ({user.role})</option>)}
              </select>
            </div>
            <button className="button" onClick={() => loginLocal(role)}>Use Demo Role</button>
            <div className="message warning">Local auth is for development only. Do not use demo headers in production.</div>
          </div>
        ) : (
          <button className="button" onClick={loginEntra}>Sign in with Microsoft Entra ID</button>
        )}
      </section>
    </main>
  );
}

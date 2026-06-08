"use client";

import { useEffect, useState } from "react";
import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { LegalHoldCreateModal } from "@/components/compliance/LegalHoldCreateModal";
import { LegalHoldList } from "@/components/compliance/LegalHoldList";
import { LegalHoldReleaseModal } from "@/components/compliance/LegalHoldReleaseModal";
import { getLegalHolds } from "@/services/legalHoldService";
import type { LegalHold } from "@/types/legalHold.types";

export default function LegalHoldsPage() {
  const [holds, setHolds] = useState<LegalHold[]>([]);
  useEffect(() => { getLegalHolds().then(setHolds).catch(() => setHolds([])); }, []);
  return <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell"><Header title="Legal Holds" subtitle="Create, view, and release auditable holds that block purge." /><section className="content grid"><LegalHoldCreateModal onCreated={(hold) => setHolds((items) => [hold, ...items])} /><LegalHoldReleaseModal onReleased={(hold) => setHolds((items) => items.map((item) => item.legal_hold_id === hold.legal_hold_id ? hold : item))} /><section className="card"><div className="card-header"><h3>Active and Released Holds</h3><p>Auditors can view holds; modification is restricted.</p></div><div className="card-body"><LegalHoldList holds={holds} /></div></section></section></main></div></ProtectedRoute>;
}

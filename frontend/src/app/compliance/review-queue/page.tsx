import { ProtectedRoute } from "@/auth/ProtectedRoute";
import { Header } from "@/components/common/Header";
import { Sidebar } from "@/components/common/Sidebar";
import { RetentionReviewQueue } from "@/components/compliance/RetentionReviewQueue";

export default function RetentionReviewQueuePage() {
  return <ProtectedRoute><div className="app-layout"><Sidebar /><main className="main-shell"><Header title="Retention Review Queue" subtitle="Archive, purge, review, and legal hold conflicts." /><section className="content"><section className="card"><div className="card-header"><h3>Candidates</h3><p>Real purge requires explicit approval and dry_run=false.</p></div><div className="card-body"><RetentionReviewQueue /></div></section></section></main></div></ProtectedRoute>;
}

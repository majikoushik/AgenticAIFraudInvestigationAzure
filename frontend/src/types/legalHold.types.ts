import type { DataCategory } from "@/types/retention.types";

export type LegalHold = {
  legal_hold_id: string;
  case_id?: string;
  record_id?: string;
  data_category?: DataCategory;
  reason: string;
  created_by: string;
  created_at: string;
  status: "ACTIVE" | "RELEASED";
  released_by?: string;
  released_at?: string;
  release_reason?: string;
};

import { CardFrame } from "@/components/cases/CardFrame";
import { MetaList } from "@/components/cases/MetaList";
import type { Beneficiary } from "@/types/case.types";

type BeneficiaryDetailsCardProps = {
  beneficiary: Beneficiary | null;
};

export function BeneficiaryDetailsCard({ beneficiary }: BeneficiaryDetailsCardProps) {
  return (
    <CardFrame title="Beneficiary Details" subtitle="Payee context and known synthetic risk notes.">
      {beneficiary ? (
        <MetaList
          rows={[
            { label: "Beneficiary", value: beneficiary.display_name },
            { label: "Relationship", value: beneficiary.relationship_type },
            { label: "Bank Country", value: beneficiary.bank_country },
            { label: "First Seen", value: beneficiary.first_seen },
            { label: "Risk Note", value: beneficiary.risk_note }
          ]}
        />
      ) : (
        <div className="empty-state">No beneficiary profile is attached to this transaction.</div>
      )}
    </CardFrame>
  );
}

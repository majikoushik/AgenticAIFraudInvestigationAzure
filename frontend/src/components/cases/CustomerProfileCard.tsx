import { CardFrame } from "@/components/cases/CardFrame";
import { MetaList } from "@/components/cases/MetaList";
import type { CustomerProfile } from "@/types/case.types";
import { formatCurrency, maskCustomerId } from "@/utils/maskingUtils";

type CustomerProfileCardProps = {
  customer: CustomerProfile;
};

export function CustomerProfileCard({ customer }: CustomerProfileCardProps) {
  return (
    <CardFrame title="Customer Profile" subtitle="Masked customer and account context.">
      <MetaList
        rows={[
          { label: "Customer", value: customer.display_name || maskCustomerId(customer.customer_id) },
          { label: "Customer ID", value: maskCustomerId(customer.customer_id) },
          { label: "Account", value: customer.account_number_masked },
          { label: "Segment", value: customer.segment },
          { label: "Risk Tier", value: customer.risk_tier },
          { label: "Home Country", value: customer.home_country },
          { label: "Average Transaction", value: formatCurrency(customer.average_transaction_amount, "USD") }
        ]}
      />
    </CardFrame>
  );
}

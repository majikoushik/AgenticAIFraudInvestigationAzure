import { CardFrame } from "@/components/cases/CardFrame";
import { MetaList } from "@/components/cases/MetaList";
import type { Transaction } from "@/types/case.types";
import { formatCurrency, formatDateTime } from "@/utils/maskingUtils";

type TransactionDetailsCardProps = {
  transaction: Transaction;
};

export function TransactionDetailsCard({ transaction }: TransactionDetailsCardProps) {
  return (
    <CardFrame title="Suspicious Transaction" subtitle="Payment attributes used by the rule-based agents.">
      <MetaList
        rows={[
          { label: "Transaction ID", value: transaction.transaction_id },
          { label: "Amount", value: formatCurrency(transaction.amount, transaction.currency) },
          { label: "Merchant", value: transaction.merchant },
          { label: "Merchant Country", value: transaction.merchant_country },
          { label: "Channel", value: transaction.channel },
          { label: "Payment Method", value: transaction.payment_method },
          { label: "Timestamp", value: formatDateTime(transaction.timestamp) }
        ]}
      />
    </CardFrame>
  );
}

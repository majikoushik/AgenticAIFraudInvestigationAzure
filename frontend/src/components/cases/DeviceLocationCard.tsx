import { CardFrame } from "@/components/cases/CardFrame";
import { MetaList } from "@/components/cases/MetaList";
import type { Device } from "@/types/case.types";

type DeviceLocationCardProps = {
  device: Device | null;
};

export function DeviceLocationCard({ device }: DeviceLocationCardProps) {
  return (
    <CardFrame title="Device and Location" subtitle="Device trust and location signals.">
      {device ? (
        <MetaList
          rows={[
            { label: "Device ID", value: device.device_id },
            { label: "Type", value: device.device_type },
            { label: "Trusted", value: device.trusted },
            { label: "Last Seen IP", value: device.last_seen_ip },
            { label: "Last Seen Country", value: device.last_seen_country },
            { label: "First Seen", value: device.first_seen }
          ]}
        />
      ) : (
        <div className="empty-state">No device profile is attached to this transaction.</div>
      )}
    </CardFrame>
  );
}

from agents.agents.base_agent import BaseAgent
from agents.orchestration.state_manager import InvestigationState


class DeviceLocationAgent(BaseAgent):
    name = "DeviceLocationAgent"

    def run(self, state: InvestigationState) -> dict:
        customer = state.case["customer"]
        device = state.case.get("device")
        indicators = []

        if not device:
            return {"device_present": False, "risk_indicators": []}

        if not device["trusted"]:
            indicators.append(
                {
                    "code": "UNTRUSTED_DEVICE",
                    "description": "Device is not trusted for this synthetic customer.",
                    "severity": "high",
                }
            )

        if device["last_seen_country"] != customer["home_country"]:
            indicators.append(
                {
                    "code": "UNUSUAL_DEVICE_COUNTRY",
                    "description": "Device country differs from the customer's home country.",
                    "severity": "medium",
                }
            )

        return {
            "device_present": True,
            "device_id": device["device_id"],
            "is_new_or_untrusted": not device["trusted"],
            "location_unusual": device["last_seen_country"] != customer["home_country"],
            "risk_indicators": indicators,
        }

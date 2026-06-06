import type { BackendHealth } from "@/types/api";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function getBackendHealth(): Promise<BackendHealth> {
  try {
    const response = await fetch(`${apiBaseUrl}/health`, {
      cache: "no-store"
    });

    if (!response.ok) {
      throw new Error(`Backend health check failed with ${response.status}`);
    }

    return response.json();
  } catch {
    return {
      status: "unavailable",
      service: "fraud-investigation-backend"
    };
  }
}

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const authMode = process.env.NEXT_PUBLIC_AUTH_MODE ?? "local";

type RequestOptions = RequestInit & {
  body?: BodyInit | null;
};

export async function apiClient<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const authHeaders = getAuthHeaders();
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...options.headers
    }
  });

  if (!response.ok) {
    if (response.status === 401 && typeof window !== "undefined") {
      window.location.href = "/login";
    }
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  if (authMode === "entra") {
    const token = window.sessionStorage.getItem("entra_access_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  }
  const raw = window.localStorage.getItem("fraud_demo_user");
  if (!raw) return {};
  try {
    const user = JSON.parse(raw) as { user_id: string; role: string; email: string };
    return {
      "X-Demo-User": user.user_id,
      "X-Demo-Role": user.role,
      "X-Demo-Email": user.email
    };
  } catch {
    return {};
  }
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    const payload = (await response.json()) as { error?: { message?: string } };
    return payload.error?.message ?? `Backend request failed with status ${response.status}.`;
  } catch {
    return "Backend is unavailable or returned an unreadable response.";
  }
}

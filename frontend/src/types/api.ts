export type BackendHealth = {
  status: "ok" | "unavailable";
  service: string;
};

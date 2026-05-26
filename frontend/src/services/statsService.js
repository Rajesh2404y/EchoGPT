import { api, withRetry } from "./api";

export async function getStats() {
  const { data } = await withRetry(() => api.get("/stats"));
  return data;
}

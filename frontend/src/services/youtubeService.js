import { api, withRetry } from "./api";

export async function processYouTube(url, { title, language } = {}) {
  const { data } = await withRetry(() => api.post("/process-youtube", { url, title, language }), 0);
  console.debug("[youtube] process response", data);
  if (!data?.success && data?.success !== undefined) {
    throw new Error(data?.detail || "YouTube processing failed.");
  }
  if (!data?.collection_id || typeof data?.transcript !== "string") {
    throw new Error("Backend returned an invalid YouTube processing response.");
  }
  return data;
}

import { api, withRetry } from "./api";

export async function processYouTube(url, { title, language } = {}) {
  const { data } = await withRetry(() => api.post("/process-youtube", { url, title, language }), 0);
  return data;
}

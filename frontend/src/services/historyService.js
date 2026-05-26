import { api, withRetry } from "./api";

export async function getHistory() {
  const { data } = await withRetry(() => api.get("/history"));
  return Array.isArray(data) ? data : [];
}

export async function deleteHistoryItem(collectionId) {
  const { data } = await withRetry(() => api.delete(`/history/${collectionId}`));
  return data;
}

export async function getHistoryChat(chatId) {
  const { data } = await withRetry(() => api.get(`/history/${chatId}`));
  return data;
}

export async function clearHistory() {
  const { data } = await withRetry(() => api.delete("/history"));
  return data;
}

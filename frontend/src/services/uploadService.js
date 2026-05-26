import { api, withRetry } from "./api";

export async function uploadAudio(file, { title, language } = {}) {
  const form = new FormData();
  form.append("file", file);
  if (title) form.append("title", title);
  if (language) form.append("language", language);
  const { data } = await withRetry(() => api.post("/upload-audio", form), 0);
  return data;
}

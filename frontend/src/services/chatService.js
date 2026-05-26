import { api, withRetry } from "./api";

export async function askQuestion(collectionId, question) {
  const body = { question };
  if (collectionId) body.collection_id = collectionId;
  const { data } = await withRetry(() =>
    api.post("/ask", body)
  );
  return data;
}

export async function streamQuestion(collectionId, question, onToken) {
  const baseURL = api.defaults.baseURL;
  const body = { question, stream: true };
  if (collectionId) body.collection_id = collectionId;
  const response = await fetch(`${baseURL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";
    for (const event of events) {
      const line = event.split("\n").find((item) => item.startsWith("data: "));
      if (!line) continue;
      const payload = JSON.parse(line.replace("data: ", ""));
      if (payload.done) return;
      if (payload.token) onToken(payload.token);
    }
  }
}

export async function generateSummary(collectionId) {
  const { data } = await withRetry(() => api.post("/summary", { collection_id: collectionId }));
  return data;
}

export async function generateNotes(collectionId) {
  const { data } = await withRetry(() => api.post("/notes", { collection_id: collectionId }));
  return data;
}

export async function generateQuiz(collectionId) {
  const { data } = await withRetry(() => api.post("/quiz", { collection_id: collectionId }));
  return data;
}

export async function getHistory() {
  const { data } = await withRetry(() => api.get("/history"));
  return data;
}

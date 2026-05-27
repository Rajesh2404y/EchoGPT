import { api, withRetry } from "./api";

function normalizeChatResponse(data) {
  const payload = data?.data && typeof data.data === "object" ? data.data : data;
  const answer = payload?.answer || payload?.content || payload?.message || "";
  const normalized = {
    success: payload?.success !== false,
    answer: typeof answer === "string" ? answer : String(answer || ""),
    sources: Array.isArray(payload?.sources) ? payload.sources : [],
    status: payload?.status || "completed",
  };
  console.debug("[chat] normalized response", normalized);
  if (!normalized.answer.trim()) {
    throw new Error("Backend returned an empty answer.");
  }
  return normalized;
}

export async function askQuestion(collectionId, question) {
  const body = { question };
  if (collectionId) body.collection_id = collectionId;
  const { data } = await withRetry(() =>
    api.post("/ask", body)
  );
  return normalizeChatResponse(data);
}

export async function streamQuestion(collectionId, question, onToken) {
  const baseURL = api.defaults.baseURL;
  const body = { question, stream: true };
  if (collectionId) body.collection_id = collectionId;
  const controller = new AbortController();
  const timeout = window.setTimeout(
    () => controller.abort(),
    Number(import.meta.env.VITE_API_TIMEOUT_MS || 900000)
  );
  let response;
  try {
    response = await fetch(`${baseURL}/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
  } finally {
    window.clearTimeout(timeout);
  }

  if (!response.ok || !response.body) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let answer = "";

  function handleEvent(event) {
    const lines = event
      .split("\n")
      .map((item) => item.trim())
      .filter((item) => item.startsWith("data:"));
    for (const line of lines) {
      const raw = line.replace(/^data:\s*/, "");
      if (!raw) continue;
      let payload;
      try {
        payload = JSON.parse(raw);
      } catch (error) {
        console.error("[chat] invalid stream JSON", raw, error);
        throw new Error("Backend returned invalid streaming JSON.");
      }
      console.debug("[chat] stream event", payload);
      if (payload.done) return true;
      if (typeof payload.token === "string") {
        answer += payload.token;
        onToken(payload.token);
      }
    }
    return false;
  }

  while (true) {
    const { done, value } = await reader.read();
    buffer += done ? decoder.decode() : decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() || "";
    for (const event of events) {
      if (handleEvent(event)) return answer;
    }
    if (done) break;
  }
  if (buffer.trim()) handleEvent(buffer);
  if (!answer.trim()) throw new Error("Backend returned an empty streamed answer.");
  return answer;
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

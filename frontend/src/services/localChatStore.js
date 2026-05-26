const prefix = "echogpt-chat:";

export function getLocalChat(chatId) {
  if (!chatId) return null;
  try {
    return JSON.parse(localStorage.getItem(`${prefix}${chatId}`) || "null");
  } catch {
    return null;
  }
}

export function saveLocalChat(chatId, payload) {
  if (!chatId || !payload) return;
  localStorage.setItem(
    `${prefix}${chatId}`,
    JSON.stringify({
      ...payload,
      updatedAt: new Date().toISOString(),
    })
  );
}

export function normalizeStoredMessages(messages) {
  if (!Array.isArray(messages)) return [];
  return messages
    .filter((message) => message && message.content)
    .map((message) => ({
      id: message.id,
      role: message.role === "user" ? "user" : "assistant",
      content: message.content || "",
      createdAt: message.createdAt || message.created_at || message.timestamp || new Date().toISOString(),
    }));
}

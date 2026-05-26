import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: Number(import.meta.env.VITE_API_TIMEOUT_MS || 900000),
});

export default api;

export async function withRetry(action, retries = 1) {
  try {
    return await action();
  } catch (error) {
    if (retries > 0 && !error?.response) {
      await new Promise((resolve) => setTimeout(resolve, 700));
      return withRetry(action, retries - 1);
    }
    throw error;
  }
}

export function getErrorMessage(error) {
  if (error?.code === "ECONNABORTED") {
    return "Processing is taking longer than expected. Large videos can take several minutes while EchoGPT downloads, transcribes, and indexes the media.";
  }
  if (!error?.response) {
    return "Backend server offline. Start FastAPI with uvicorn app.main:app --reload.";
  }
  return error?.response?.data?.detail || error.message || "Something went wrong.";
}

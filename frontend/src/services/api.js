import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000",
  timeout: Number(import.meta.env.VITE_API_TIMEOUT_MS || 900000),
});

api.interceptors.response.use(
  (response) => {
    console.debug("[api] response", response.config?.url, response.status, response.data);
    return response;
  },
  (error) => {
    console.error("[api] error", error.config?.url, error);
    return Promise.reject(error);
  }
);

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
    return "Request timed out while processing the full video. Try again with a shorter video or a local audio upload.";
  }
  if (!error?.response) {
    return "Backend server offline. Start FastAPI with uvicorn app.main:app --reload.";
  }
  return error?.response?.data?.detail || error.message || "Something went wrong.";
}

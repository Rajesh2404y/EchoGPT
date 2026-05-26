import { useState } from "react";
import { getErrorMessage } from "../services/api";

export function useAsyncAction() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function run(action) {
    setLoading(true);
    setError("");
    try {
      return await action();
    } catch (err) {
      const message = getErrorMessage(err);
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  return { loading, error, run, setError };
}

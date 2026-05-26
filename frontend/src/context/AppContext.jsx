import { createContext, useContext, useEffect, useMemo, useState } from "react";

const AppContext = createContext(null);

export const themePresets = [
  {
    id: "neon-blue",
    name: "Neon Blue",
    from: "#06b6d4",
    to: "#3b82f6",
    accent: "#38bdf8",
    sidebar: "#08111f",
    bubble: "#0ea5e9",
  },
  {
    id: "purple-cyber",
    name: "Purple Cyber",
    from: "#a855f7",
    to: "#ec4899",
    accent: "#c084fc",
    sidebar: "#130a24",
    bubble: "#8b5cf6",
  },
  {
    id: "emerald-ai",
    name: "Emerald AI",
    from: "#10b981",
    to: "#14b8a6",
    accent: "#34d399",
    sidebar: "#071a14",
    bubble: "#059669",
  },
  {
    id: "sunset-orange",
    name: "Sunset Orange",
    from: "#f97316",
    to: "#ef4444",
    accent: "#fb923c",
    sidebar: "#20100a",
    bubble: "#ea580c",
  },
  {
    id: "ocean-cyan",
    name: "Ocean Cyan",
    from: "#22d3ee",
    to: "#2563eb",
    accent: "#67e8f9",
    sidebar: "#071827",
    bubble: "#0891b2",
  },
  {
    id: "dark-glass",
    name: "Dark Glass",
    from: "#64748b",
    to: "#18181b",
    accent: "#e5e7eb",
    sidebar: "#050507",
    bubble: "#3f3f46",
  },
];

const defaultSettings = {
  themeId: "neon-blue",
  mode: "dark",
  accentColor: "#38bdf8",
  sidebarColor: "#08111f",
  chatBubbleColor: "#0ea5e9",
  fontSize: "base",
  whisperModel: "small",
  llmModel: "qwen3:8b",
  embeddingModel: "BAAI/bge-small-en",
  streaming: true,
  autoScroll: true,
  showTimestamps: true,
  defaultLanguage: "auto",
  autoDetectLanguage: true,
  audioQuality: "balanced",
};

function loadSettings() {
  try {
    if (!localStorage.getItem("echogpt-settings")) {
      const randomTheme = themePresets[Math.floor(Math.random() * themePresets.length)];
      return {
        ...defaultSettings,
        themeId: randomTheme.id,
        accentColor: randomTheme.accent,
        sidebarColor: randomTheme.sidebar,
        chatBubbleColor: randomTheme.bubble,
      };
    }
    const stored = JSON.parse(localStorage.getItem("echogpt-settings") || "{}");
    return { ...defaultSettings, ...stored };
  } catch {
    return defaultSettings;
  }
}

export function AppProvider({ children }) {
  const [settings, setSettingsState] = useState(loadSettings);
  const [activeCollection, setActiveCollection] = useState(null);
  const [transcript, setTranscript] = useState("");
  const [timestamps, setTimestamps] = useState([]);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Upload audio or paste a YouTube URL, then ask me anything grounded in that media.",
    },
  ]);

  useEffect(() => {
    const preset = themePresets.find((item) => item.id === settings.themeId) || themePresets[0];
    const root = document.documentElement;
    root.dataset.mode = settings.mode;
    root.style.setProperty("--theme-from", preset.from);
    root.style.setProperty("--theme-to", preset.to);
    root.style.setProperty("--accent", settings.accentColor || preset.accent);
    root.style.setProperty("--sidebar", settings.sidebarColor || preset.sidebar);
    root.style.setProperty("--chat-user", settings.chatBubbleColor || preset.bubble);
    root.style.setProperty("--font-scale", settings.fontSize === "large" ? "1.06" : settings.fontSize === "small" ? "0.94" : "1");
    localStorage.setItem("echogpt-settings", JSON.stringify(settings));
  }, [settings]);

  useEffect(() => {
    if (!activeCollection?.collection_id || !Array.isArray(messages)) return;
    const meaningfulMessages = messages.filter((message) => message?.content);
    localStorage.setItem(
      `echogpt-chat:${activeCollection.collection_id}`,
      JSON.stringify({
        activeCollection,
        messages: meaningfulMessages,
        updatedAt: new Date().toISOString(),
      })
    );
  }, [activeCollection, messages]);

  function setSettings(update) {
    setSettingsState((current) => {
      const next = typeof update === "function" ? update(current) : { ...current, ...update };
      const preset = themePresets.find((item) => item.id === next.themeId);
      if (preset && next.themeId !== current.themeId) {
        return {
          ...next,
          accentColor: preset.accent,
          sidebarColor: preset.sidebar,
          chatBubbleColor: preset.bubble,
        };
      }
      return next;
    });
  }

  function resetSettings() {
    setSettingsState(defaultSettings);
  }

  const value = useMemo(
    () => ({
      settings,
      setSettings,
      resetSettings,
      themePresets,
      activeCollection,
      setActiveCollection,
      transcript,
      setTranscript,
      timestamps,
      setTimestamps,
      messages,
      setMessages,
    }),
    [settings, activeCollection, transcript, timestamps, messages]
  );

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

export function useAppState() {
  const context = useContext(AppContext);
  if (!context) throw new Error("useAppState must be used inside AppProvider");
  return context;
}

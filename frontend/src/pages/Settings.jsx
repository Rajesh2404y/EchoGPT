import { ChevronDown, Database, Info, MonitorCog, RotateCcw, SlidersHorizontal } from "lucide-react";
import { useState } from "react";
import { Button, Field, Panel } from "../components/ui/primitives";
import { useAppState } from "../context/AppContext";
import { clearHistory } from "../services/historyService";

const apiUrl = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

function Toggle({ checked, onChange }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!checked)}
      className={`flex h-7 w-12 items-center rounded-full border p-1 transition ${
        checked ? "border-transparent bg-[var(--accent)]" : "border-white/15 bg-white/10"
      }`}
      aria-pressed={checked}
    >
      <span className={`size-5 rounded-full bg-white transition ${checked ? "translate-x-5" : ""}`} />
    </button>
  );
}

function Section({ id, title, description, icon: Icon, open, onToggle, children }) {
  return (
    <section className="glass-card overflow-hidden">
      <button
        type="button"
        onClick={() => onToggle(id)}
        className="flex w-full items-center gap-4 p-4 text-left md:p-5"
      >
        <span className="grid size-10 shrink-0 place-items-center rounded-2xl bg-white/10 text-[var(--accent)]">
          <Icon size={19} />
        </span>
        <span className="min-w-0 flex-1">
          <span className="block font-semibold text-white">{title}</span>
          <span className="mt-1 block text-sm text-zinc-400">{description}</span>
        </span>
        <ChevronDown className={`shrink-0 text-zinc-500 transition ${open ? "rotate-180" : ""}`} size={18} />
      </button>
      {open && <div className="grid gap-4 border-t border-white/10 p-4 md:p-5">{children}</div>}
    </section>
  );
}

function SelectSetting({ label, value, onChange, options }) {
  return (
    <Field label={label}>
      <select className="input" value={value} onChange={(event) => onChange(event.target.value)}>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </Field>
  );
}

function ToggleRow({ label, description, checked, onChange }) {
  return (
    <div className="flex items-center justify-between gap-4 rounded-2xl border border-white/10 bg-white/[0.04] p-4">
      <span>
        <span className="block text-sm font-medium text-zinc-100">{label}</span>
        {description && <span className="mt-1 block text-xs text-zinc-500">{description}</span>}
      </span>
      <Toggle checked={checked} onChange={onChange} />
    </div>
  );
}

export default function Settings() {
  const { settings, setSettings, resetSettings } = useAppState();
  const [openSections, setOpenSections] = useState({
    ai: true,
    chat: true,
    media: false,
    system: false,
    about: false,
  });

  function toggleSection(id) {
    setOpenSections((current) => ({ ...current, [id]: !current[id] }));
  }

  return (
    <div className="mx-auto grid max-w-4xl gap-5">
      <div>
        <h1 className="text-2xl font-bold text-white md:text-3xl">Settings</h1>
        <p className="mt-2 max-w-2xl text-sm leading-6 text-zinc-400">
          Configure EchoGPT behavior. Appearance is handled from the top navigation theme controls.
        </p>
      </div>

      <div className="grid gap-3">
        <Section
          id="ai"
          title="AI Settings"
          description="Model choices used by transcription, retrieval, and generation."
          icon={MonitorCog}
          open={openSections.ai}
          onToggle={toggleSection}
        >
          <div className="grid gap-4 md:grid-cols-2">
            <SelectSetting label="Whisper model" value={settings.whisperModel} onChange={(whisperModel) => setSettings({ whisperModel })} options={[
              { value: "tiny", label: "tiny" },
              { value: "base", label: "base" },
              { value: "small", label: "small" },
              { value: "medium", label: "medium" },
            ]} />
            <SelectSetting label="LLM model" value={settings.llmModel} onChange={(llmModel) => setSettings({ llmModel })} options={[
              { value: "qwen3:8b", label: "qwen3:8b" },
              { value: "llama3.1", label: "llama3.1" },
              { value: "mistral", label: "mistral" },
            ]} />
          </div>
          <SelectSetting label="Embedding model" value={settings.embeddingModel} onChange={(embeddingModel) => setSettings({ embeddingModel })} options={[
            { value: "BAAI/bge-small-en", label: "BAAI/bge-small-en" },
            { value: "sentence-transformers/all-MiniLM-L6-v2", label: "all-MiniLM-L6-v2" },
          ]} />
        </Section>

        <Section
          id="chat"
          title="Chat Settings"
          description="Control response behavior and conversation ergonomics."
          icon={SlidersHorizontal}
          open={openSections.chat}
          onToggle={toggleSection}
        >
          <ToggleRow label="Streaming" description="Show answers as they are generated." checked={settings.streaming} onChange={(streaming) => setSettings({ streaming })} />
          <ToggleRow label="Auto-scroll" description="Keep the latest response in view." checked={settings.autoScroll} onChange={(autoScroll) => setSettings({ autoScroll })} />
          <ToggleRow label="Timestamp chips" description="Show message time metadata in chat." checked={settings.showTimestamps} onChange={(showTimestamps) => setSettings({ showTimestamps })} />
        </Section>

        <Section
          id="media"
          title="Media Settings"
          description="Defaults for uploads, YouTube processing, and transcription."
          icon={Database}
          open={openSections.media}
          onToggle={toggleSection}
        >
          <div className="grid gap-4 md:grid-cols-2">
            <SelectSetting label="Default language" value={settings.defaultLanguage} onChange={(defaultLanguage) => setSettings({ defaultLanguage })} options={[
              { value: "auto", label: "Auto detect" },
              { value: "en", label: "English" },
              { value: "ta", label: "Tamil" },
              { value: "hi", label: "Hindi" },
            ]} />
            <SelectSetting label="Audio quality" value={settings.audioQuality} onChange={(audioQuality) => setSettings({ audioQuality })} options={[
              { value: "fast", label: "Fast" },
              { value: "balanced", label: "Balanced" },
              { value: "high", label: "High quality" },
            ]} />
          </div>
          <ToggleRow label="Auto detect language" description="Let Whisper infer the source language when possible." checked={settings.autoDetectLanguage} onChange={(autoDetectLanguage) => setSettings({ autoDetectLanguage })} />
        </Section>

        <Section
          id="system"
          title="System Settings"
          description="Maintenance actions for local preferences and saved sessions."
          icon={Database}
          open={openSections.system}
          onToggle={toggleSection}
        >
          <div className="grid gap-3 sm:grid-cols-2">
            <Button variant="ghost" onClick={() => localStorage.removeItem("echogpt-settings")}>Clear cache</Button>
            <Button variant="ghost" onClick={clearHistory}>Clear history</Button>
          </div>
        </Section>

        <Section
          id="about"
          title="About"
          description="Version and runtime stack details."
          icon={Info}
          open={openSections.about}
          onToggle={toggleSection}
        >
          <div className="grid gap-3 text-sm text-zinc-400">
            <p><span className="font-medium text-zinc-200">Version:</span> 1.0.0</p>
            <p><span className="font-medium text-zinc-200">API:</span> {apiUrl}</p>
            <p><span className="font-medium text-zinc-200">Stack:</span> Whisper, BGE embeddings, ChromaDB, Ollama</p>
          </div>
        </Section>
      </div>

      <Panel className="flex flex-col gap-3 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="font-semibold text-white">Reset Preferences</h2>
          <p className="mt-1 text-sm text-zinc-400">Restore default EchoGPT settings for this browser.</p>
        </div>
        <Button variant="ghost" onClick={resetSettings}>
          <RotateCcw size={16} /> Reset settings
        </Button>
      </Panel>
    </div>
  );
}

import { FileAudio, Link2, UploadCloud } from "lucide-react";
import { useRef, useState } from "react";
import { Button, Field } from "../ui/primitives";
import Loader from "../Loader/Loader";
import { processYouTube } from "../../services/youtubeService";
import { uploadAudio } from "../../services/uploadService";
import { useAppState } from "../../context/AppContext";
import { useAsyncAction } from "../../hooks/useAsyncAction";

export default function UploadBox() {
  const fileRef = useRef(null);
  const [url, setUrl] = useState("");
  const { settings, setActiveCollection, setTranscript, setTimestamps, setMessages } = useAppState();
  const [language, setLanguage] = useState(settings.defaultLanguage || "auto");
  const { loading, error, run } = useAsyncAction();

  function applyResult(result) {
    setActiveCollection(result);
    setTranscript(result.transcript);
    setTimestamps(result.timestamps);
    setMessages([
      {
        role: "assistant",
        content: `Ready. I indexed ${result.chunks} transcript chunks from "${result.title}".`,
      },
    ]);
  }

  async function submitUrl(event) {
    event.preventDefault();
    if (!url.trim()) return;
    await run(async () => applyResult(await processYouTube(url, { language })));
  }

  async function onFileChange(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    await run(async () => applyResult(await uploadAudio(file, { language })));
  }

  return (
    <div className="grid gap-4">
      <form onSubmit={submitUrl} className="grid gap-3">
        <Field label="YouTube URL">
          <div className="flex gap-2">
            <span className="input-icon"><Link2 size={17} /></span>
            <input className="input" value={url} onChange={(event) => setUrl(event.target.value)} placeholder="https://youtube.com/watch?v=..." />
            <Button disabled={loading}>Process</Button>
          </div>
        </Field>
        <Field label="Language hint">
          <select className="input max-w-xs" value={language} onChange={(event) => setLanguage(event.target.value)}>
            <option value="auto">Auto Detect</option>
            <option value="en">English</option>
            <option value="ta">Tamil</option>
            <option value="hi">Hindi</option>
          </select>
        </Field>
      </form>
      <button className="dropzone" type="button" onClick={() => fileRef.current?.click()} disabled={loading}>
        <UploadCloud size={30} />
        <span className="font-medium text-white">Drop audio here or browse</span>
        <span className="text-sm text-zinc-400">mp3, wav, m4a up to your configured server limit</span>
        <input ref={fileRef} className="hidden" type="file" accept=".mp3,.wav,.m4a,audio/*" onChange={onFileChange} />
      </button>
      {loading && <Loader />}
      {error && <p className="rounded-2xl border border-red-400/30 bg-red-500/10 p-3 text-sm text-red-100">{error}</p>}
      <div className="grid grid-cols-3 gap-2 text-xs text-zinc-400">
        <span className="metric"><FileAudio size={14} /> Whisper auto</span>
        <span className="metric">BGE embeddings</span>
        <span className="metric">Qwen3:8b</span>
      </div>
    </div>
  );
}

import { Search } from "lucide-react";
import { useMemo, useState } from "react";

export default function TranscriptViewer({ transcript }) {
  const [query, setQuery] = useState("");
  const visible = useMemo(() => {
    if (!query) return transcript;
    return transcript
      .split(". ")
      .filter((sentence) => sentence.toLowerCase().includes(query.toLowerCase()))
      .join(". ");
  }, [query, transcript]);

  return (
    <div className="grid gap-3">
      <div className="flex items-center gap-2">
        <span className="input-icon"><Search size={16} /></span>
        <input className="input" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search transcript" />
      </div>
      <div className="max-h-[420px] overflow-y-auto rounded-2xl border border-white/10 bg-black/20 p-4 text-sm leading-7 text-zinc-300">
        {visible || "No transcript loaded yet."}
      </div>
    </div>
  );
}

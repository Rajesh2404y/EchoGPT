import { Clock3 } from "lucide-react";
import { formatSeconds } from "../../utils/time";

export default function TimestampCard({ item }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.05] p-3">
      <div className="mb-2 flex items-center gap-2 text-xs text-[var(--accent)]">
        <Clock3 size={14} />
        {formatSeconds(item.start)} - {formatSeconds(item.end)}
      </div>
      <p className="line-clamp-3 text-sm leading-6 text-zinc-300">{item.text}</p>
    </div>
  );
}

import { PlayCircle } from "lucide-react";

export default function VideoCard({ title = "No media selected", chunks = 0 }) {
  return (
    <div className="media-strip">
      <span className="animated-gradient grid size-12 place-items-center rounded-2xl text-white">
        <PlayCircle size={24} />
      </span>
      <div>
        <p className="font-semibold text-white">{title}</p>
        <p className="text-sm text-zinc-400">{chunks} indexed chunks</p>
      </div>
    </div>
  );
}

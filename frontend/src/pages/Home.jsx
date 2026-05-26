import { Brain, Captions, Layers3, RadioTower } from "lucide-react";
import ChatBox from "../components/ChatBox/ChatBox";
import TimestampCard from "../components/TimestampCard/TimestampCard";
import TranscriptViewer from "../components/TranscriptViewer/TranscriptViewer";
import UploadBox from "../components/UploadBox/UploadBox";
import VideoCard from "../components/VideoCard/VideoCard";
import { FadeIn, Panel } from "../components/ui/primitives";
import { useAppState } from "../context/AppContext";

export default function Home() {
  const { activeCollection, transcript, timestamps } = useAppState();
  const previewTimestamps = timestamps.slice(0, 4);

  return (
    <div className="grid gap-4 xl:grid-cols-[420px_1fr]">
      <FadeIn className="grid content-start gap-4">
        <Panel>
          <div className="mb-4">
            <p className="text-sm font-medium text-[var(--accent)]">EchoGPT</p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal text-white">
              Chat with YouTube videos and audio files.
            </h1>
            <p className="mt-3 text-sm leading-6 text-zinc-400">
              Transcribe, index, retrieve, summarize, and quiz from real media context.
            </p>
          </div>
          <UploadBox />
        </Panel>
        <VideoCard title={activeCollection?.title} chunks={activeCollection?.chunks || 0} />
        <div className="grid grid-cols-2 gap-3">
          {[
            ["Whisper", Captions],
            ["ChromaDB", Layers3],
            ["RAG", Brain],
            ["Ollama", RadioTower],
          ].map(([label, Icon]) => (
            <div key={label} className="stat-tile">
              <Icon size={18} />
              <span>{label}</span>
            </div>
          ))}
        </div>
      </FadeIn>
      <FadeIn delay={0.08} className="grid gap-4">
        <Panel className="overflow-hidden p-0">
          <ChatBox />
        </Panel>
        <div className="grid gap-4 lg:grid-cols-[1fr_280px]">
          <Panel>
            <h2 className="mb-3 text-lg font-semibold text-white">Transcript</h2>
            <TranscriptViewer transcript={transcript} />
          </Panel>
          <Panel>
            <h2 className="mb-3 text-lg font-semibold text-white">Timestamps</h2>
            <div className="grid max-h-[420px] gap-2 overflow-y-auto">
              {previewTimestamps.length
                ? previewTimestamps.map((item, index) => <TimestampCard key={index} item={item} />)
                : <p className="text-sm text-zinc-400">Timestamps appear after transcription.</p>}
            </div>
          </Panel>
        </div>
      </FadeIn>
    </div>
  );
}

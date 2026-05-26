import UploadBox from "../components/UploadBox/UploadBox";
import TranscriptViewer from "../components/TranscriptViewer/TranscriptViewer";
import TimestampCard from "../components/TimestampCard/TimestampCard";
import { Panel } from "../components/ui/primitives";
import { useAppState } from "../context/AppContext";

export default function Upload() {
  const { transcript, timestamps, activeCollection } = useAppState();

  return (
    <div className="grid gap-5 lg:grid-cols-[420px_1fr]">
      <Panel>
        <p className="text-sm font-semibold text-[var(--accent)]">Upload</p>
        <h1 className="mb-4 mt-2 text-2xl font-bold text-white">Process Media</h1>
        <UploadBox />
      </Panel>

      <div className="grid gap-4">
        <Panel className="animated-gradient text-white">
          <h2 className="text-lg font-semibold">{activeCollection?.title || "No active collection"}</h2>
          <p className="mt-1 text-sm text-white/75">
            {activeCollection?.collection_id || "Upload audio or process a YouTube URL to create a collection."}
          </p>
        </Panel>
        <Panel>
          <TranscriptViewer transcript={transcript} />
        </Panel>
        <div className="grid gap-2 md:grid-cols-2">
          {timestamps.slice(0, 8).map((item, index) => <TimestampCard key={index} item={item} />)}
        </div>
      </div>
    </div>
  );
}

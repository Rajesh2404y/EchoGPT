import { Clock3, FileAudio, Search, Trash2, Video } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, FadeIn } from "../components/ui/primitives";
import { deleteHistoryItem, getHistory } from "../services/historyService";

function HistorySkeleton() {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: 6 }).map((_, index) => (
        <div key={index} className="glass-card p-4">
          <div className="skeleton mb-4 h-12 w-12 rounded-2xl" />
          <div className="skeleton mb-3 h-5 w-3/4 rounded" />
          <div className="skeleton mb-2 h-4 w-full rounded" />
          <div className="skeleton h-4 w-2/3 rounded" />
        </div>
      ))}
    </div>
  );
}

export default function History() {
  const navigate = useNavigate();
  const [history, setHistory] = useState([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [openingId, setOpeningId] = useState("");

  async function fetchHistory() {
    setLoading(true);
    setError("");
    try {
      setHistory(await getHistory());
    } catch (err) {
      setError(err?.response?.data?.detail || "Backend server offline");
      setHistory([]);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    fetchHistory();
  }, []);

  const filtered = useMemo(() => {
    if (!Array.isArray(history)) return [];
    const term = query.trim().toLowerCase();
    if (!term) return history;
    return history.filter((item) =>
      [item.title, item.last_message, item.summary, item.type, item.chat_id, item.collection_id]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(term)
    );
  }, [history, query]);

  async function removeItem(item) {
    setHistory((current) => current.filter((entry) => entry.collection_id !== item.collection_id));
    try {
      await deleteHistoryItem(item.collection_id);
    } catch {
      fetchHistory();
    }
  }

  function openItem(item) {
    const chatId = item.chat_id || item.id || item.collection_id;
    if (!chatId) return;
    setOpeningId(chatId);
    navigate(`/chat/${chatId}`);
  }

  return (
    <div className="mx-auto grid max-w-6xl gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white md:text-3xl">History</h1>
          <p className="mt-1 text-sm text-zinc-400">Reopen processed media, continue chatting, or clean up old sessions.</p>
        </div>
        <Button variant="ghost" onClick={fetchHistory}>Refresh</Button>
      </div>

      <div className="glass-card flex items-center gap-3 p-3">
        <Search size={18} className="text-zinc-500" />
        <input
          className="w-full bg-transparent text-sm text-zinc-100 outline-none placeholder:text-zinc-500"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search by title, summary, type, or collection id"
        />
      </div>

      {loading && <HistorySkeleton />}

      {!loading && error && (
        <div className="glass-card border-red-400/30 bg-red-500/10 p-5 text-sm text-red-100">
          {error}
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="glass-card grid min-h-72 place-items-center p-8 text-center">
          <div>
            <span className="mx-auto mb-4 grid size-14 place-items-center rounded-2xl bg-white/10 text-[var(--accent)]">
              <Clock3 size={24} />
            </span>
            <h2 className="text-lg font-semibold text-white">Your media history will appear here.</h2>
            <p className="mt-2 text-sm text-zinc-400">Process a YouTube link or upload audio to create your first searchable session.</p>
          </div>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {Array.isArray(filtered) && filtered.map((item, index) => {
            const isYoutube = item.type === "youtube";
            const Icon = isYoutube ? Video : FileAudio;
            const chatId = item.chat_id || item.id || item.collection_id;
            return (
              <FadeIn key={chatId} delay={index * 0.03} className="glass-card flex h-full flex-col p-4">
                <div className="mb-4 flex items-start justify-between gap-3">
                  <span className="animated-gradient grid size-12 place-items-center rounded-2xl text-white">
                    <Icon size={20} />
                  </span>
                  <span className="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-semibold uppercase text-zinc-200">
                    {item.type || "media"}
                  </span>
                </div>
                <h2 className="line-clamp-2 font-semibold text-white">{item.title || "Untitled media"}</h2>
                <p className="mt-2 line-clamp-3 flex-1 text-sm leading-6 text-zinc-400">
                  {item.last_message || item.summary || "No messages yet."}
                </p>
                <div className="mt-4 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
                  <span>{item.updated_at || item.created_at ? new Date(item.updated_at || item.created_at).toLocaleString() : "No date"}</span>
                  <span>{item.chunks || 0} chunks</span>
                </div>
                <div className="mt-4 flex gap-2">
                  <Button className="flex-1" onClick={() => openItem(item)} disabled={openingId === chatId}>
                    {openingId === chatId ? "Opening..." : "Open Chat"}
                  </Button>
                  <Button variant="ghost" onClick={() => removeItem(item)} aria-label={`Delete ${item.title}`}>
                    <Trash2 size={16} />
                  </Button>
                </div>
              </FadeIn>
            );
          })}
        </div>
      )}
    </div>
  );
}

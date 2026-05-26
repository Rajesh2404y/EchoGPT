import { ArrowDown, FileQuestion, ListChecks, Send, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import ChatMessage from "../ChatMessage/ChatMessage";
import Loader from "../Loader/Loader";
import { Button } from "../ui/primitives";
import { useAppState } from "../../context/AppContext";
import { askQuestion, generateNotes, generateQuiz, generateSummary, streamQuestion } from "../../services/chatService";
import { useAsyncAction } from "../../hooks/useAsyncAction";

export default function ChatBox() {
  const { activeCollection, messages, setMessages, settings } = useAppState();
  const [question, setQuestion] = useState("");
  const [showJump, setShowJump] = useState(false);
  const scrollRef = useRef(null);
  const bottomRef = useRef(null);
  const { loading, error, run } = useAsyncAction();

  function scrollToBottom(behavior = "smooth") {
    bottomRef.current?.scrollIntoView({ behavior, block: "end" });
  }

  useEffect(() => {
    if (settings.autoScroll) scrollToBottom("smooth");
  }, [messages, loading, settings.autoScroll]);

  function onScroll() {
    const node = scrollRef.current;
    if (!node) return;
    setShowJump(node.scrollHeight - node.scrollTop - node.clientHeight > 180);
  }

  async function submit(event) {
    event.preventDefault();
    if (!question.trim()) return;
    const currentQuestion = question.trim();
    const userMessage = { role: "user", content: currentQuestion, createdAt: new Date().toISOString() };
    setMessages((current) => [...current, userMessage]);
    setQuestion("");
    await run(async () => {
      const assistantId = crypto.randomUUID();
      setMessages((current) => [...current, { id: assistantId, role: "assistant", content: "", createdAt: new Date().toISOString() }]);
      if (settings.streaming) {
        try {
          await streamQuestion(activeCollection?.collection_id, currentQuestion, (token) => {
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId ? { ...message, content: `${message.content}${token}` } : message
              )
            );
          });
          return;
        } catch {
          setMessages((current) => current.filter((message) => message.id !== assistantId));
        }
      }
      const response = await askQuestion(activeCollection?.collection_id, currentQuestion);
      setMessages((current) => [...current, { role: "assistant", content: response.answer, createdAt: new Date().toISOString() }]);
    });
  }

  async function generate(kind) {
    if (!activeCollection) return;
    const actions = { summary: generateSummary, notes: generateNotes, quiz: generateQuiz };
    await run(async () => {
      const response = await actions[kind](activeCollection.collection_id);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.content, createdAt: new Date().toISOString() },
      ]);
    });
  }

  return (
    <div className="relative flex h-[calc(100vh-7rem)] min-h-[620px] flex-col overflow-hidden">
      <div className="flex flex-wrap items-center gap-2 border-b border-white/10 p-3">
        <Button variant="ghost" onClick={() => generate("summary")} disabled={!activeCollection || loading}>
          <Sparkles size={16} /> Summary
        </Button>
        <Button variant="ghost" onClick={() => generate("notes")} disabled={!activeCollection || loading}>
          <ListChecks size={16} /> Notes
        </Button>
        <Button variant="ghost" onClick={() => generate("quiz")} disabled={!activeCollection || loading}>
          <FileQuestion size={16} /> Quiz
        </Button>
        {activeCollection && (
          <span className="ml-auto max-w-full truncate rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-zinc-300">
            {activeCollection.title}
          </span>
        )}
      </div>

      <div ref={scrollRef} onScroll={onScroll} className="relative flex-1 space-y-5 overflow-y-auto p-4 md:p-5">
        {Array.isArray(messages) && messages.length > 0 ? (
          messages.map((message, index) => (
            <ChatMessage key={message.id || `${message.role}-${index}`} message={message} showTimestamp={settings.showTimestamps} />
          ))
        ) : (
          <div className="grid min-h-80 place-items-center text-center">
            <div>
              <p className="text-lg font-semibold text-white">No saved messages in this chat</p>
              <p className="mt-2 max-w-md text-sm leading-6 text-zinc-400">
                Older history items may only contain the processed media. Ask a question here and future turns will reopen like ChatGPT history.
              </p>
            </div>
          </div>
        )}
        {loading && (
          <div className="chat-assistant chat-bubble flex items-center gap-3">
            <Loader label="EchoGPT is thinking" />
          </div>
        )}
        {error && <p className="rounded-2xl border border-red-400/30 bg-red-500/10 p-3 text-sm text-red-100">{error}</p>}
        <div ref={bottomRef} />
      </div>

      {showJump && (
        <button className="icon-btn absolute bottom-24 right-8 z-10" type="button" onClick={() => scrollToBottom()}>
          <ArrowDown size={18} />
        </button>
      )}

      <form onSubmit={submit} className="sticky bottom-0 border-t border-white/10 bg-black/35 p-3 backdrop-blur-xl">
        <div className="flex gap-2 rounded-2xl border border-white/10 bg-white/[0.06] p-2 shadow-xl">
          <textarea
            className="max-h-32 min-h-11 flex-1 resize-none bg-transparent px-2 py-2 text-sm text-white outline-none placeholder:text-zinc-500"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter" && !event.shiftKey) submit(event);
            }}
            placeholder={activeCollection ? "Ask about this media..." : "Ask a question or process media for grounded answers"}
            disabled={loading}
          />
          <Button className="self-end" disabled={loading || !question.trim()}>
            <Send size={17} />
          </Button>
        </div>
      </form>
    </div>
  );
}

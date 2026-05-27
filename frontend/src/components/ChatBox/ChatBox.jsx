import { ArrowDown, FileQuestion, ListChecks, Sparkles } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "../ui/primitives";
import { useAppState } from "../../context/AppContext";
import { askQuestion, generateNotes, generateQuiz, generateSummary, streamQuestion } from "../../services/chatService";
import { useAsyncAction } from "../../hooks/useAsyncAction";
import ChatInput from "./ChatInput";
import ChatLayout from "./ChatLayout";
import MessageList from "./MessageList";

export default function ChatBox() {
  const { activeCollection, messages, setMessages, settings } = useAppState();
  const [question, setQuestion] = useState("");
  const [showJump, setShowJump] = useState(false);
  const [streamingAssistantId, setStreamingAssistantId] = useState(null);
  const scrollRef = useRef(null);
  const bottomRef = useRef(null);
  const { loading, error, run } = useAsyncAction();
  const isWaitingForAssistant = loading && !streamingAssistantId;

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
      if (settings.streaming) {
        try {
          setStreamingAssistantId(assistantId);
          setMessages((current) => [...current, { id: assistantId, role: "assistant", content: "", createdAt: new Date().toISOString() }]);
          const streamedAnswer = await streamQuestion(activeCollection?.collection_id, currentQuestion, (token) => {
            setMessages((current) =>
              current.map((message) =>
                message.id === assistantId ? { ...message, content: `${message.content}${token}` } : message
              )
            );
          });
          if (streamedAnswer?.trim()) {
            setStreamingAssistantId(null);
            return;
          }
          setMessages((current) => current.filter((message) => message.id !== assistantId));
        } catch (streamError) {
          console.error("[chat] streaming failed, falling back to non-streaming", streamError);
          setMessages((current) => current.filter((message) => message.id !== assistantId));
        } finally {
          setStreamingAssistantId(null);
        }
      }
      const response = await askQuestion(activeCollection?.collection_id, currentQuestion);
      console.debug("[chat] rendering response", response);
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          content: response.answer || "I received an empty response from the backend.",
          sources: response.sources || [],
          createdAt: new Date().toISOString(),
        },
      ]);
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

  const header = (
    <>
      <div className="chat-header-actions">
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
          <span className="chat-active-title">
            {activeCollection.title}
          </span>
        )}
      </div>
    </>
  );

  const messageContent = (
    <div ref={scrollRef} onScroll={onScroll} className="chat-messages-scroll">
      <MessageList
        messages={messages}
        showTimestamp={settings.showTimestamps}
        isWaitingForAssistant={isWaitingForAssistant}
        error={error}
        bottomRef={bottomRef}
      />
    </div>
  );

  const jumpButton = showJump ? (
    <button className="chat-jump-btn" type="button" onClick={() => scrollToBottom()}>
      <ArrowDown size={18} />
    </button>
  ) : null;

  const input = (
    <ChatInput
      value={question}
      onChange={setQuestion}
      onSubmit={submit}
      disabled={loading}
      placeholder={activeCollection ? "Ask about this media..." : "Ask a question or process media for grounded answers"}
    />
  );

  return (
    <ChatLayout
      header={header}
      messages={messageContent}
      input={input}
      jumpButton={jumpButton}
    />
  );
}

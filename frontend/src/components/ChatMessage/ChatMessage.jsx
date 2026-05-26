import { Bot, User } from "lucide-react";

function renderMarkdown(text = "") {
  const blocks = text.split(/```/g);
  return blocks.map((block, index) => {
    if (index % 2 === 1) {
      const lines = block.replace(/^\w+\n/, "").trim();
      return (
        <pre key={index}>
          <code>{lines}</code>
        </pre>
      );
    }
    return block.split("\n").map((line, lineIndex) => {
      const trimmed = line.trim();
      if (!trimmed) return <br key={`${index}-${lineIndex}`} />;
      if (/^#{1,3}\s/.test(trimmed)) {
        return <h3 key={`${index}-${lineIndex}`} className="mt-2 font-semibold text-white">{trimmed.replace(/^#{1,3}\s/, "")}</h3>;
      }
      if (/^[-*]\s/.test(trimmed)) {
        return <p key={`${index}-${lineIndex}`} className="pl-3">- {trimmed.replace(/^[-*]\s/, "")}</p>;
      }
      return <p key={`${index}-${lineIndex}`}>{line}</p>;
    });
  });
}

export default function ChatMessage({ message, showTimestamp = true }) {
  const isUser = message.role === "user";
  return (
    <div className={`fade-in flex gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
      {!isUser && (
        <span className="animated-gradient grid size-9 shrink-0 place-items-center rounded-2xl text-white">
          <Bot size={17} />
        </span>
      )}
      <div className={`chat-bubble ${isUser ? "chat-user" : "chat-assistant"}`}>
        <div className="markdown-body whitespace-pre-wrap">{renderMarkdown(message.content)}</div>
        {showTimestamp && (
          <div className={`mt-2 text-[11px] ${isUser ? "text-white/70" : "text-zinc-500"}`}>
            {message.createdAt ? new Date(message.createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "Now"}
          </div>
        )}
      </div>
      {isUser && (
        <span className="grid size-9 shrink-0 place-items-center rounded-2xl border border-white/10 bg-white/10 text-white">
          <User size={17} />
        </span>
      )}
    </div>
  );
}

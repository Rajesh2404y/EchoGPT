import { memo } from "react";
import ChatMessage from "../ChatMessage/ChatMessage";
import Loader from "../Loader/Loader";

const MemoChatMessage = memo(ChatMessage);

function MessageList({
  messages,
  showTimestamp,
  isWaitingForAssistant,
  error,
  bottomRef,
}) {
  return (
    <div className="chat-message-list">
      {Array.isArray(messages) && messages.length > 0 ? (
        messages.map((message, index) => (
          <MemoChatMessage
            key={message.id || `${message.role}-${index}`}
            message={message}
            showTimestamp={showTimestamp}
          />
        ))
      ) : (
        <div className="chat-empty-state">
          <div>
            <p className="text-lg font-semibold text-white">No saved messages in this chat</p>
            <p className="mt-2 max-w-md text-sm leading-6 text-zinc-400">
              Ask a question here and future turns will reopen like ChatGPT history.
            </p>
          </div>
        </div>
      )}
      {isWaitingForAssistant && (
        <div className="chat-row chat-row-assistant">
          <div className="chat-bubble chat-assistant flex items-center gap-3">
            <Loader label="EchoGPT is thinking" />
          </div>
        </div>
      )}
      {error && <p className="chat-error">{error}</p>}
      <div ref={bottomRef} />
    </div>
  );
}

export default memo(MessageList);

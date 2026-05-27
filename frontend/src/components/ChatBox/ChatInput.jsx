import { Send } from "lucide-react";
import { Button } from "../ui/primitives";

export default function ChatInput({
  disabled = false,
  placeholder = "Ask a question",
  value,
  onChange,
  onSubmit,
}) {
  return (
    <form onSubmit={onSubmit} className="chat-input-shell">
      <div className="chat-input-wrap">
        <textarea
          className="chat-input"
          value={value}
          onChange={(event) => onChange(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) onSubmit(event);
          }}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
        />
        <Button className="chat-send-btn" disabled={disabled || !value.trim()} aria-label="Send message">
          <Send size={17} />
        </Button>
      </div>
    </form>
  );
}

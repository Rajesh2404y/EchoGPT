export default function ChatLayout({ header, messages, input, jumpButton }) {
  return (
    <section className="chat-layout">
      <header className="chat-header">{header}</header>
      <div className="chat-scroll-region">
        {messages}
        {jumpButton}
      </div>
      {input}
    </section>
  );
}

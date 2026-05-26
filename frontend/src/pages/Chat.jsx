import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import ChatBox from "../components/ChatBox/ChatBox";
import Loader from "../components/Loader/Loader";
import { Panel } from "../components/ui/primitives";
import { useAppState } from "../context/AppContext";
import { getHistoryChat } from "../services/historyService";
import { getLocalChat, normalizeStoredMessages, saveLocalChat } from "../services/localChatStore";

export default function Chat() {
  const { chatId } = useParams();
  const { setActiveCollection, setMessages } = useAppState();
  const [loading, setLoading] = useState(Boolean(chatId));
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function fetchChat() {
      if (!chatId) {
        setLoading(false);
        return;
      }
      setLoading(true);
      setError("");
      try {
        const localSession = getLocalChat(chatId);
        if (localSession && active) {
          setActiveCollection(localSession.activeCollection);
          setMessages(normalizeStoredMessages(localSession.messages));
        }
        const session = await getHistoryChat(chatId);
        if (!active) return;
        const activeCollection = {
          collection_id: session.collection_id || session.id,
          title: session.title || "Untitled media",
          chunks: session.chunks || 0,
        };
        const restoredMessages = normalizeStoredMessages(session.messages);
        setActiveCollection(activeCollection);
        setMessages(restoredMessages);
        saveLocalChat(session.chat_id || session.id || chatId, {
          activeCollection,
          messages: restoredMessages,
        });
      } catch (err) {
        if (!active) return;
        const localSession = getLocalChat(chatId);
        if (localSession) {
          setActiveCollection(localSession.activeCollection);
          setMessages(normalizeStoredMessages(localSession.messages));
          setError("Loaded local chat copy because the backend session could not be reached.");
        } else {
          setError(err?.response?.data?.detail || "Could not load previous chat.");
          setMessages([]);
        }
      } finally {
        if (active) setLoading(false);
      }
    }

    fetchChat();
    return () => {
      active = false;
    };
  }, [chatId, setActiveCollection, setMessages]);

  return (
    <Panel className="mx-auto max-w-5xl overflow-hidden p-0 shadow-2xl">
      {loading ? (
        <div className="grid min-h-[520px] place-items-center p-6">
          <Loader label="Loading previous chat" />
        </div>
      ) : (
        <>
          {error && <div className="border-b border-red-400/30 bg-red-500/10 p-3 text-sm text-red-100">{error}</div>}
          <ChatBox />
        </>
      )}
    </Panel>
  );
}

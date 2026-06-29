import { useState, useRef, useEffect, useCallback } from "react";
import { MessageCircle, X, Send, Loader2 } from "lucide-react";

const API_BASE = "http://localhost:8000";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export function HelpButton() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
  }, [messages]);

  const send = useCallback(async () => {
    if (!input.trim() || loading) return;
    const userMsg: ChatMessage = { role: "user", content: input.trim() };
    setInput("");
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/help/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMsg.content,
          history: messages.slice(-10),
        }),
      });
      if (!res.ok) {
        const e = await res.json();
        throw new Error(e.detail ?? "Failed to get response");
      }
      const data = await res.json();
      setMessages((prev) => [...prev, userMsg, { role: "assistant", content: data.reply }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        userMsg,
        { role: "assistant", content: `Error: ${err instanceof Error ? err.message : "Unknown error"}` },
      ]);
    } finally {
      setLoading(false);
    }
  }, [input, loading, messages]);

  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-4 right-4 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-accent text-white shadow-lg transition-transform hover:scale-110"
        title="Help"
      >
        <MessageCircle className="h-6 w-6" />
      </button>
    );
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex h-[500px] w-96 flex-col rounded-lg border border-border bg-bg-base shadow-2xl">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border px-4 py-3">
        <div className="flex items-center gap-2">
          <MessageCircle className="h-5 w-5 text-accent" />
          <span className="font-semibold">Help Assistant</span>
        </div>
        <button
          onClick={() => setOpen(false)}
          className="rounded p-1 text-text-muted hover:bg-bg-surface hover:text-text-base"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 && (
          <div className="text-center text-sm text-text-muted py-8">
            <MessageCircle className="mx-auto mb-3 h-8 w-8 opacity-40" />
            <p>Ask me anything about Open-Write Studio!</p>
            <p className="mt-1 text-xs">Features, pipeline, profiles, export...</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bg-accent text-white"
                  : "bg-bg-surface text-text-base border border-border"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-lg bg-bg-surface border border-border px-3 py-2">
              <Loader2 className="h-4 w-4 animate-spin text-accent" />
              <span className="text-sm text-text-muted">Thinking...</span>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-border p-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && send()}
            placeholder="Ask about features, pipeline, profiles..."
            className="flex-1 rounded-md border border-border bg-bg-surface px-3 py-2 text-sm text-text-base placeholder:text-text-muted focus:border-accent focus:outline-none"
            disabled={loading}
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="flex items-center justify-center rounded-md bg-accent px-3 py-2 text-white transition-colors hover:bg-accent/80 disabled:opacity-40"
          >
            <Send className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

import { useState } from "react";
import { sendAgentMessage, applyProposal, type AgentMessage, type AgentProposal } from "../../api/agent";

interface AgentChatProps {
  onApplied: () => void;
}

export function AgentChat({ onApplied }: AgentChatProps) {
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState("");
  const [proposal, setProposal] = useState<AgentProposal | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    const nextMessages: AgentMessage[] = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setProposal(null);
    setError(null);
    setLoading(true);
    try {
      const result = await sendAgentMessage(nextMessages);
      setMessages([...nextMessages, { role: "assistant", content: result.message }]);
      setProposal(result.proposal);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  async function handleApply() {
    if (!proposal) return;
    try {
      await applyProposal(proposal);
      setProposal(null);
      onApplied();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-2.5 max-h-[360px] overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-text-muted text-[12.5px]">
            Ask me to reassign a responsibility — e.g. "put Rob on Interrupt instead of Sam".
          </p>
        )}
        {messages.map((m, i) => (
          <div
            key={i}
            className={`max-w-[85%] rounded-md px-3 py-2 text-[13px] ${
              m.role === "user"
                ? "self-end bg-accent text-accent-ink"
                : "self-start bg-surface border border-border text-text"
            }`}
          >
            {m.content}
          </div>
        ))}
        {loading && <p className="text-text-muted text-[12px]">Thinking...</p>}
      </div>

      {error && <p className="text-danger text-[12px]">{error}</p>}

      {proposal && (
        <div className="bg-surface border border-border rounded-md p-3.5 flex flex-col gap-2.5">
          <div className="text-[12.5px] font-semibold">{proposal.responsibility_name}</div>
          <div className="flex items-center gap-1.5 text-[12.5px]">
            <span className="text-text-muted line-through">
              {proposal.from_raider_name ?? "Unassigned"}
            </span>
            <span className="text-text-muted">→</span>
            <span className="text-accent font-semibold">{proposal.to_raider_name}</span>
            {proposal.confidence === "unknown" && (
              <span className="text-[10.5px] font-mono text-warning ml-1">unconfirmed</span>
            )}
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleApply}
              className="flex-1 bg-accent border-none rounded px-3 py-2 text-accent-ink font-bold text-[12.5px]"
            >
              Apply
            </button>
            <button
              onClick={() => setProposal(null)}
              className="flex-1 border border-border-strong rounded px-3 py-2 text-text-muted text-[12.5px]"
            >
              Discard
            </button>
          </div>
        </div>
      )}

      <div className="flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          disabled={loading}
          placeholder="Ask about a reassignment..."
          className="flex-1 bg-background border border-border-strong rounded px-2.5 py-2 text-text text-[13px]"
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-accent border-none rounded px-4 py-2 text-accent-ink font-bold text-[13px]"
        >
          Send
        </button>
      </div>
    </div>
  );
}

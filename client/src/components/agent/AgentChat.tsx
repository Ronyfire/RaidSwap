import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { sendAgentMessage, applyProposal, type AgentMessage, type AgentProposal } from "../../api/agent";
import { ApiError } from "../../api/client";

interface AgentChatProps {
  onApplied: () => void;
  bossId?: number;
}

export function AgentChat({ onApplied, bossId }: AgentChatProps) {
  const { t } = useTranslation();
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [input, setInput] = useState("");
  const [proposal, setProposal] = useState<AgentProposal | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [cooldownSeconds, setCooldownSeconds] = useState(0);
  const [acknowledgedRisk, setAcknowledgedRisk] = useState(false);

  useEffect(() => {
    if (cooldownSeconds <= 0) return;
    const id = setInterval(() => setCooldownSeconds((s) => Math.max(0, s - 1)), 1000);
    return () => clearInterval(id);
  }, [cooldownSeconds]);

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    const nextMessages: AgentMessage[] = [...messages, { role: "user", content: text }];
    setMessages(nextMessages);
    setInput("");
    setProposal(null);
    setAcknowledgedRisk(false);
    setError(null);
    setLoading(true);
    try {
      const result = await sendAgentMessage(nextMessages, bossId);
      setMessages([...nextMessages, { role: "assistant", content: result.message }]);
      setProposal(result.proposal);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("common.unknownError"));
    } finally {
      setLoading(false);
    }
  }

  async function handleApply() {
    if (!proposal) return;
    try {
      await applyProposal(proposal, acknowledgedRisk);
      setProposal(null);
      setAcknowledgedRisk(false);
      onApplied();
    } catch (err) {
      if (err instanceof ApiError && err.status === 429) {
        setCooldownSeconds(Number(err.body.retry_after_seconds) || 60);
      } else {
        setError(err instanceof Error ? err.message : t("common.unknownError"));
      }
    }
  }

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-col gap-2.5 max-h-[360px] overflow-y-auto">
        {messages.length === 0 && (
          <p className="text-text-muted text-[12.5px]">{t("agentChat.examplePrompt")}</p>
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
        {loading && <p className="text-text-muted text-[12px]">{t("agentChat.thinking")}</p>}
      </div>

      {error && <p className="text-danger text-[12px]">{error}</p>}

      {proposal && (
        <div className="bg-surface border border-border rounded-md p-3.5 flex flex-col gap-2.5">
          <div className="text-[12.5px] font-semibold">{proposal.responsibility_name}</div>
          <div className="flex items-center gap-1.5 text-[12.5px]">
            <span className="text-text-muted line-through">
              {proposal.from_raider_name ?? t("common.unassigned")}
            </span>
            <span className="text-text-muted">→</span>
            <span className="text-accent font-semibold">{proposal.to_raider_name}</span>
            {proposal.confidence === "unknown" && (
              <span className="text-[10.5px] font-mono text-warning ml-1">
                {t("common.unconfirmed")}
              </span>
            )}
          </div>

          {proposal.confidence === "unknown" && (
            <div className="bg-warning/10 border border-warning/30 rounded px-2.5 py-2 flex flex-col gap-1.5">
              <p className="text-[11.5px] text-warning">
                {t(
                  proposal.confidence_reason === "never_done"
                    ? "agentChat.reasonNeverDone"
                    : "agentChat.reasonNoProfile",
                  { name: proposal.to_raider_name },
                )}
              </p>
              <label className="flex items-center gap-1.5 text-[11.5px] text-text cursor-pointer">
                <input
                  type="checkbox"
                  checked={acknowledgedRisk}
                  onChange={(e) => setAcknowledgedRisk(e.target.checked)}
                />
                {t("agentChat.confirmRisk")}
              </label>
            </div>
          )}

          <div className="flex gap-2">
            <button
              onClick={handleApply}
              disabled={cooldownSeconds > 0 || (proposal.confidence === "unknown" && !acknowledgedRisk)}
              className="flex-1 bg-accent border-none rounded px-3 py-2 text-accent-ink font-bold text-[12.5px] disabled:opacity-50"
            >
              {cooldownSeconds > 0
                ? t("agentChat.waitSeconds", { seconds: cooldownSeconds })
                : t("agentChat.apply")}
            </button>
            <button
              onClick={() => {
                setProposal(null);
                setAcknowledgedRisk(false);
              }}
              className="flex-1 border border-border-strong rounded px-3 py-2 text-text-muted text-[12.5px]"
            >
              {t("agentChat.discard")}
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
          placeholder={t("agentChat.inputPlaceholder")}
          className="flex-1 bg-background border border-border-strong rounded px-2.5 py-2 text-text text-[13px]"
        />
        <button
          onClick={handleSend}
          disabled={loading}
          className="bg-accent border-none rounded px-4 py-2 text-accent-ink font-bold text-[13px]"
        >
          {t("agentChat.send")}
        </button>
      </div>
    </div>
  );
}

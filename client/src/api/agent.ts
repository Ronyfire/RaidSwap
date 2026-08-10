import { apiFetch } from "./client";

export interface AgentMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AgentProposal {
  boss_name: string;
  responsibility_name: string;
  from_raider_name: string | null;
  to_raider_name: string;
  confidence: "confirmed" | "unknown";
  confidence_reason: "no_profile" | "never_done" | null;
}

export interface AgentChatResponse {
  message: string;
  proposal: AgentProposal | null;
}

export function sendAgentMessage(
  messages: AgentMessage[],
  bossId?: number,
): Promise<AgentChatResponse> {
  return apiFetch<AgentChatResponse>("/api/agent/chat", {
    method: "POST",
    body: JSON.stringify({ messages, boss_id: bossId }),
  });
}

export function applyProposal(proposal: AgentProposal, acknowledgedRisk = false): Promise<unknown> {
  return apiFetch("/api/agent/apply", {
    method: "POST",
    body: JSON.stringify({ proposal, acknowledged_risk: acknowledgedRisk }),
  });
}

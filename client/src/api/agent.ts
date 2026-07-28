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
}

export interface AgentChatResponse {
  message: string;
  proposal: AgentProposal | null;
}

export function sendAgentMessage(messages: AgentMessage[]): Promise<AgentChatResponse> {
  return apiFetch<AgentChatResponse>("/api/agent/chat", {
    method: "POST",
    body: JSON.stringify({ messages }),
  });
}

export function applyProposal(proposal: AgentProposal): Promise<unknown> {
  return apiFetch("/api/agent/apply", {
    method: "POST",
    body: JSON.stringify({ proposal }),
  });
}

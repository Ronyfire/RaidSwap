"""LLM adapter + agent loop for the reassignment agent.

Provider-agnostic on purpose (see projects/agent-architecture.md): today only
OpenRouter is implemented, picked via AI_PROVIDER. Adding a second provider
(e.g. Anthropic direct) means adding a sibling branch in _get_client()/_MODEL,
not touching run_agent_turn() or anything that calls it.

Model default: NOT Kimi K2 free (explicitly excluded — see architecture doc).
google/gemini-2.0-flash-exp:free and meta-llama/llama-3.3-70b-instruct:free
were both smoke-tested and 404'd (pulled from OpenRouter's free tier).
Landed on openrouter/free — OpenRouter's own auto-router, which picks among
whatever free models are currently live and filters for tool-calling support
— so individual free-slug churn doesn't break this app again. Smoke-tested
2026-07-28 with a real key: correctly called get_roster. Swap OPENROUTER_MODEL
in .env for a pinned single model if the routing ever proves unreliable.
"""

import json
import os

from openai import OpenAI

from services import agent_tools

_DEFAULT_MODEL = "openrouter/free"
_MAX_TOOL_ITERATIONS = 5

SYSTEM_PROMPT = """You are RaidSwap's raid assignment assistant. You help a WoW \
raid leader reassign responsibilities when their roster changes mid-progress.

Rules:
- Always use the tools to look up real data — never guess a raider's class, \
role, or mechanic experience.
- To change who's doing a mechanic, call propose_reassignment. It does NOT \
apply the change — it only prepares it for the raid leader to confirm.
- If propose_reassignment comes back with confidence "unknown" (no evidence \
the new raider has done this mechanic before), say so plainly and ask the \
raid leader to confirm before they apply it — don't imply it's a safe bet.
- If propose_reassignment returns an error, explain it in plain language \
instead of retrying blindly.
- Apply the MINIMAL necessary change: only touch the one responsibility being \
discussed, never suggest recalculating the whole boss composition.
- Be concise. This is a mid-raid tool, not a chat companion."""

_TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_roster",
            "description": "List every raider in the roster with their class, spec, and role.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_mechanic_profile",
            "description": "Check how proficient a specific raider is at a specific mechanic/responsibility.",
            "parameters": {
                "type": "object",
                "properties": {
                    "raider_name": {"type": "string"},
                    "responsibility_name": {"type": "string"},
                },
                "required": ["raider_name", "responsibility_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "propose_reassignment",
            "description": (
                "Prepare (but do not apply) reassigning a boss responsibility to a "
                "different raider. Returns a proposal for the raid leader to confirm."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "boss_name": {"type": "string"},
                    "responsibility_name": {"type": "string"},
                    "new_raider_name": {"type": "string"},
                },
                "required": ["boss_name", "responsibility_name", "new_raider_name"],
            },
        },
    },
]

_TOOL_FUNCTIONS = {
    "get_roster": lambda: agent_tools.get_roster(),
    "get_mechanic_profile": lambda raider_name, responsibility_name: agent_tools.get_mechanic_profile(
        raider_name, responsibility_name
    ),
    "propose_reassignment": lambda boss_name, responsibility_name, new_raider_name: agent_tools.propose_reassignment(
        boss_name, responsibility_name, new_raider_name
    ),
}


def _get_client() -> OpenAI:
    provider = os.environ.get("AI_PROVIDER", "openrouter")
    if provider != "openrouter":
        raise NotImplementedError(f"AI_PROVIDER '{provider}' not implemented yet")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )


def _get_model() -> str:
    return os.environ.get("OPENROUTER_MODEL", _DEFAULT_MODEL)


def run_agent_turn(messages: list[dict]) -> dict:
    """Runs the agent loop for one user turn.

    `messages` is the full conversation so far (list of {"role", "content"}),
    NOT including the system prompt. Returns {"message": str, "proposal": dict | None} —
    proposal is the last propose_reassignment() result this turn, if any, so the
    frontend can render an Apply/Discard card without parsing prose.
    """
    client = _get_client()
    model = _get_model()
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}, *messages]
    pending_proposal = None

    for _ in range(_MAX_TOOL_ITERATIONS):
        response = client.chat.completions.create(
            model=model, messages=conversation, tools=_TOOL_SCHEMAS
        )
        message = response.choices[0].message

        if not message.tool_calls:
            return {"message": message.content or "", "proposal": pending_proposal}

        conversation.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in message.tool_calls
                ],
            }
        )

        for tool_call in message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments or "{}")
            fn = _TOOL_FUNCTIONS.get(name)
            result = fn(**args) if fn else {"error": f"Unknown tool '{name}'"}

            if name == "propose_reassignment" and "error" not in result:
                pending_proposal = result

            conversation.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result),
                }
            )

    return {
        "message": "Sorry, I couldn't finish that — try rephrasing your request.",
        "proposal": pending_proposal,
    }

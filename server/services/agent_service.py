"""LLM adapter + agent loop for the reassignment agent.

Provider-agnostic on purpose (see projects/agent-architecture.md): today only
OpenRouter is implemented, picked via AI_PROVIDER. Adding a second provider
(e.g. Anthropic direct) means adding a sibling branch in _get_client()/_MODEL,
not touching run_agent_turn() or anything that calls it.

Model default: NOT Kimi K2 free (explicitly excluded — see architecture doc).
openrouter/free (OpenRouter's own auto-router) and google/gemini-2.0-flash-exp:free
/meta-llama/llama-3.3-70b-instruct:free were all tried and dropped — either 404'd
(pulled from the free tier) or, for the auto-router, not reliable enough at
one-shot tool-calling with the boss-context injection. Pinned to
nvidia/nemotron-3-super-120b-a12b:free after a head-to-head smoke test against
openai/gpt-oss-20b:free (0/3) — nemotron passed 3/3. Run
scripts/smoke_test_model.py against a candidate before ever changing this.
"""

import json
import os

from openai import OpenAI

from services import agent_tools

_DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
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
- If propose_reassignment's error includes current_assignees (a responsibility \
with more than one raider currently on it), don't guess which one to replace — \
list them and ask the raid leader which one, then call propose_reassignment \
again with that name as from_raider_name.
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
                "different raider. Returns a proposal for the raid leader to confirm. "
                "If the responsibility currently has more than one raider assigned, "
                "this returns an error with current_assignees instead of guessing — "
                "ask the raid leader which one, then call again with from_raider_name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "boss_name": {"type": "string"},
                    "responsibility_name": {"type": "string"},
                    "new_raider_name": {"type": "string"},
                    "from_raider_name": {
                        "type": "string",
                        "description": (
                            "Which currently-assigned raider to replace. Only required "
                            "when the responsibility has more than one raider assigned; "
                            "omit it otherwise."
                        ),
                    },
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
    "propose_reassignment": lambda boss_name, responsibility_name, new_raider_name, from_raider_name=None: agent_tools.propose_reassignment(
        boss_name, responsibility_name, new_raider_name, from_raider_name
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


def _boss_context_message(boss_id: int) -> dict | None:
    context = agent_tools.get_boss_context(boss_id)
    if context is None:
        return None
    names = ", ".join(f'"{n}"' for n in context["responsibility_names"])
    return {
        "role": "system",
        "content": (
            f'The raid leader is currently viewing "{context["boss_name"]}". '
            "Assume that's the boss they mean unless they clearly say otherwise "
            "— don't ask them to name it. "
            f"Its responsibilities are: {names or '(none yet)'}. "
            "Map informal references (e.g. \"the interrupt\") to the exact "
            "responsibility name from this list before calling propose_reassignment."
        ),
    }


def run_agent_turn(messages: list[dict], boss_id: int | None = None) -> dict:
    """Runs the agent loop for one user turn.

    `messages` is the full conversation so far (list of {"role", "content"}),
    NOT including the system prompt. `boss_id`, when given, injects a second
    system message naming the boss currently on screen and its responsibility
    names, so the raid leader doesn't have to spell out the boss every turn.
    Returns {"message": str, "proposal": dict | None} — proposal is the last
    propose_reassignment() result this turn, if any, so the frontend can
    render an Apply/Discard card without parsing prose.
    """
    client = _get_client()
    model = _get_model()
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    if boss_id is not None:
        boss_message = _boss_context_message(boss_id)
        if boss_message is not None:
            conversation.append(boss_message)
    conversation += messages
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

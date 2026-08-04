"""One-off script: verify a candidate OpenRouter model can actually do tool-calling.

Not part of the app or the test suite — run manually once OPENROUTER_API_KEY is
set, whenever picking/changing OPENROUTER_MODEL:

    pipenv run python scripts/smoke_test_model.py [model-slug]

Prints whether the model called the tool as expected. If it just replies in
prose instead of calling get_roster, that model's tool-calling isn't reliable
enough for this app — try another candidate (see suggestions below) and update
OPENROUTER_MODEL in .env once one works.

2026-07-28: google/gemini-2.0-flash-exp:free and meta-llama/llama-3.3-70b-instruct:free
both 404'd (pulled from OpenRouter's free tier). openrouter/free (OpenRouter's own
auto-router) worked at the time but wasn't reliable enough later against the real
boss-context injection. openai/gpt-oss-20b:free failed 0/3 one-shot tool-calling
attempts; nvidia/nemotron-3-super-120b-a12b:free passed 3/3 and is now the pinned
default (Kimi K2 free is explicitly excluded — see projects/agent-architecture.md).
"""

import json
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_roster",
            "description": "List every raider in the roster.",
            "parameters": {"type": "object", "properties": {}},
        },
    }
]


def main():
    model = sys.argv[1] if len(sys.argv) > 1 else os.environ.get(
        "OPENROUTER_MODEL", "nvidia/nemotron-3-super-120b-a12b:free"
    )
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ.get("OPENROUTER_API_KEY"),
    )

    print(f"Testing model: {model}")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You help manage a WoW raid roster. Use tools to look up real data."},
            {"role": "user", "content": "Who's in the roster right now?"},
        ],
        tools=TOOLS,
    )
    message = response.choices[0].message

    if message.tool_calls:
        print("PASS — model called a tool:")
        for tc in message.tool_calls:
            print(f"  {tc.function.name}({tc.function.arguments})")
    else:
        print("FAIL — model replied without calling a tool:")
        print(f"  {message.content}")
        print(json.dumps(response.model_dump(), indent=2)[:1000])


if __name__ == "__main__":
    main()

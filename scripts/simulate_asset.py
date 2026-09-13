#!/usr/bin/env python3
"""scripts/simulate_asset.py: Local simulation tool for live model mounts & injections.

Designed strictly for LOCAL developer testing (NOT CI).
Allows authors to mount custom or catalog personas, memories, and lineages into real
frontier APIs (Claude, OpenAI, Gemini) or local Ollama instances to test how the model
reacts to real prompts before committing or opening a PR.

Usage examples:
  # Test the chef with Thessaloniki breakfasts against Gemini
  python scripts/simulate_asset.py -p north_mediterranean_chef \\
    -m culinary/thessaloniki_breakfasts --provider gemini

  # Test legal philosopher against Claude
  python scripts/simulate_asset.py -p juris_philosopher \\
    -m legal/semicolon_fine_tuning_trap --provider anthropic

  # Test tactical aviator against local Ollama
  python scripts/simulate_asset.py -p edge_aviator \\
    -m robotics/uav_microburst_stall --provider ollama

  # Interactive multi-turn conversational session
  python scripts/simulate_asset.py -p north_mediterranean_chef \\
    -m culinary/thessaloniki_breakfasts --interactive
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any
from pathlib import Path

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

import mnemolink  # noqa: E402


def query_anthropic(
    system_prompt: str, user_prompt: str, model: str = "claude-3-5-sonnet-20241022"
) -> tuple[str, float, int]:
    """Execute query against Anthropic Messages API."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set in environment or .env")

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    payload: dict[str, Any] = {
        "model": model,
        "max_tokens": 1024,
        "system": [
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if not any(v in model for v in ("-5", "sonnet-5", "haiku-5", "opus-5", "fable-5")):
        payload["temperature"] = 0.2

    start = time.perf_counter()
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        latency = time.perf_counter() - start
        text_blocks = [
            b["text"]
            for b in res.get("content", [])
            if b.get("type") == "text" and "text" in b
        ]
        content = "\n".join(text_blocks).strip() if text_blocks else ""
        out_tokens = res.get("usage", {}).get("output_tokens", len(content.split()))
        return content, latency, out_tokens


def query_openai(
    system_prompt: str, user_prompt: str, model: str = "gpt-4o"
) -> tuple[str, float, int]:
    """Execute query against OpenAI Chat Completions API."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in environment or .env")

    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    start = time.perf_counter()
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        latency = time.perf_counter() - start
        content = res["choices"][0]["message"]["content"]
        out_tokens = res.get("usage", {}).get("completion_tokens", len(content.split()))
        return content, latency, out_tokens


def query_gemini(
    system_instruction: str, user_prompt: str, model: str = "gemini-2.5-flash"
) -> tuple[str, float, int]:
    """Execute query against Google Gemini REST API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment or .env")

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )
    headers = {"Content-Type": "application/json"}
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024},
    }

    start = time.perf_counter()
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        latency = time.perf_counter() - start
        cand = res["candidates"][0]["content"]["parts"][0]["text"]
        out_tokens = res.get("usageMetadata", {}).get(
            "candidatesTokenCount", len(cand.split())
        )
        return cand, latency, out_tokens


def query_ollama(
    system_prompt: str,
    user_prompt: str,
    model: str = "llama3.1:8b",
    host: str = "http://localhost:11434",
) -> tuple[str, float, int]:
    """Execute query against local Ollama instance."""
    clean_host = host.rstrip("/")
    url = f"{clean_host}/api/generate"
    payload = {
        "model": model,
        "system": system_prompt,
        "prompt": user_prompt,
        "stream": False,
        "options": {"temperature": 0.2},
    }

    start = time.perf_counter()
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        latency = time.perf_counter() - start
        content = res.get("response", "").strip()
        out_tokens = res.get("eval_count", len(content.split()))
        return content, latency, out_tokens


def main():
    parser = argparse.ArgumentParser(
        description="Local simulation harness for testing MnemoLink assets against live models."
    )
    parser.add_argument("-p", "--persona", required=True, help="Persona ID or path")
    parser.add_argument(
        "-m", "--memories", nargs="*", default=[], help="Memory IDs or paths"
    )
    parser.add_argument("-l", "--lineage", default=None, help="Lineage ID or path")
    parser.add_argument(
        "--provider",
        choices=["anthropic", "openai", "gemini", "ollama"],
        default="gemini",
        help="Target model provider",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Specific model name (defaults to provider standard)",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Prompt to send (if omitted, prompts interactively)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch an interactive multi-turn session",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("MnemoLink Local Asset Simulation Harness (Live Model Mount)")
    print("=" * 70)

    # 1. Compose the mnemonic bundle
    print(f"Loading Persona: {args.persona}")
    if args.memories:
        print(f"Loading Memories: {', '.join(args.memories)}")
    if args.lineage:
        print(f"Loading Lineage: {args.lineage}")

    bundle = mnemolink.compose(
        persona=args.persona,
        memories=args.memories,
        build_lineage=bool(args.lineage or len(args.memories) > 1),
    )

    print(
        f"Context compiled successfully ({len(bundle.render_markdown().split())} words)."
    )
    print(f"Target Provider: {args.provider.upper()}")

    # Determine default model if not provided
    default_models = {
        "anthropic": "claude-3-5-sonnet-20241022",
        "openai": "gpt-4o",
        "gemini": "gemini-2.5-flash",
        "ollama": "llama3.1:8b",
    }
    target_model = args.model or default_models[args.provider]
    print(f"Target Model: {target_model}")
    print("-" * 70)

    # Select adapter output
    if args.provider == "anthropic":
        system_text = bundle.to_claude()
    elif args.provider == "openai":
        system_text = bundle.to_raw()
    elif args.provider == "gemini":
        system_text = bundle.to_gemini()
    else:
        system_text = bundle.to_ollama()

    def run_turn(user_msg: str):
        print(f"\n[USER PROMPT]: {user_msg}")
        print("Sending to model...")
        try:
            if args.provider == "anthropic":
                reply, latency, tokens = query_anthropic(
                    system_text, user_msg, model=target_model
                )
            elif args.provider == "openai":
                reply, latency, tokens = query_openai(
                    system_text, user_msg, model=target_model
                )
            elif args.provider == "gemini":
                reply, latency, tokens = query_gemini(
                    system_text, user_msg, model=target_model
                )
            else:
                reply, latency, tokens = query_ollama(
                    system_text, user_msg, model=target_model
                )

            print(f"\n[MODEL RESPONSE ({latency:.2f}s, {tokens} tokens)]:\n")
            print(reply)
            print("-" * 70)
        except Exception as e:
            print(f"\n[ERROR]: Failed to query {args.provider}: {e}")

    if args.interactive:
        print("Starting interactive session. Type 'exit' or 'quit' to stop.")
        while True:
            try:
                user_input = input("\nYou > ").strip()
                if user_input.lower() in {"exit", "quit"}:
                    break
                if not user_input:
                    continue
                run_turn(user_input)
            except (KeyboardInterrupt, EOFError):
                break
    else:
        test_prompt = (
            args.prompt
            or "Introduce yourself, state what principles you refuse to violate, "
            "and what experience forged them."
        )
        run_turn(test_prompt)


if __name__ == "__main__":
    main()

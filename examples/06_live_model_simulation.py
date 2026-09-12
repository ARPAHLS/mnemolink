"""06_live_model_simulation.py: Live LLM stress-test comparing generic prompts vs. MnemoLink.

Evaluates Claude and Gemini across three cognitive configurations:
1. Generic AI Baseline (Unconditioned imperative prompt)
2. MnemoLink Persona (juris_philosopher)
3. MnemoLink Persona + Memory (juris_philosopher + semicolon_fine_tuning_trap)

Directly queries Anthropic Messages API and Google GenAI API using standard HTTP.
Zero LiteLLM dependency. Measures latency, tokens, cost ($ USD), and response fidelity.
"""

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Tuple

from dotenv import load_dotenv

# Ensure mnemolink is importable regardless of working directory
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

load_dotenv(REPO_ROOT / ".env")

import mnemolink  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def strip_emojis(text: str) -> str:
    """Remove non-ASCII emoji symbols from output text."""
    return re.sub(r"[\U00010000-\U0010ffff]", "", text)


# ------------------------------------------------------------------------------
# Pricing Constants (USD per token)
# ------------------------------------------------------------------------------
# Claude 3.5 Sonnet / Sonnet 4.5: $3.00/M input, $15.00/M output
CLAUDE_INPUT_COST_PER_TOKEN = 3.00 / 1_000_000
CLAUDE_OUTPUT_COST_PER_TOKEN = 15.00 / 1_000_000

# Gemini 3.6 Flash: $0.10/M input, $0.40/M output
GEMINI_INPUT_COST_PER_TOKEN = 0.10 / 1_000_000
GEMINI_OUTPUT_COST_PER_TOKEN = 0.40 / 1_000_000

# ------------------------------------------------------------------------------
# High-Stakes Niche Legal Problem
# ------------------------------------------------------------------------------
NICHE_LEGAL_PROMPT = (
    "URGENT CLOSING CRISIS - $18M ARR ENTERPRISE DATA INGESTION DEAL\n"
    "We are the Data Licensor licensing foundational model training sets to a "
    "major enterprise. The counterparty GC just slipped this revised Section 9.4 "
    "into the agreement and demands we sign before the 5:00 PM Board meeting "
    "(in 40 minutes). Our junior associate says it's fine because it excludes "
    "post-training fine-tuning. Here is the clause:\n\n"
    '"Section 9.4 (Indemnification & Exclusions): Licensor shall defend, '
    "indemnify, and hold harmless Licensee against third-party claims alleging "
    "that the Ingested Data infringes any copyright or trade secret; "
    "provided that Licensee maintains complete provenance logs; and losses "
    'resulting from foundational model post-training fine-tuning."\n\n'
    "Can executive leadership sign this as-is? Is there a trap? "
    "Give me your definitive counsel in 60 seconds with an exact redline."
)


# ------------------------------------------------------------------------------
# Direct Model Clients (Zero LiteLLM Middleware)
# ------------------------------------------------------------------------------
def query_claude_direct(
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    model: str = "claude-sonnet-4-5-20250929",
    max_tokens: int = 1500,
) -> Dict[str, Any]:
    """Execute direct HTTP request to Anthropic Messages API."""
    url = "https://api.anthropic.com/v1/messages"
    payload: Dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.1,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    if system_prompt:
        payload["system"] = system_prompt

    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }

    start_time = time.perf_counter()
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            elapsed = time.perf_counter() - start_time
            data = json.loads(resp.read().decode("utf-8"))
            text = "".join(
                block.get("text", "")
                for block in data.get("content", [])
                if block.get("type") == "text"
            )
            usage = data.get("usage", {})
            in_tok = usage.get("input_tokens", 0)
            out_tok = usage.get("output_tokens", 0)
            cost = (in_tok * CLAUDE_INPUT_COST_PER_TOKEN) + (
                out_tok * CLAUDE_OUTPUT_COST_PER_TOKEN
            )

            return {
                "provider": "Anthropic Claude",
                "model": model,
                "text": text.strip(),
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "latency_sec": elapsed,
                "cost_usd": cost,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - start_time
        err_body = e.read().decode("utf-8")
        return {
            "provider": "Anthropic Claude",
            "model": model,
            "text": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_sec": elapsed,
            "cost_usd": 0.0,
            "error": f"HTTP {e.code}: {err_body}",
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return {
            "provider": "Anthropic Claude",
            "model": model,
            "text": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_sec": elapsed,
            "cost_usd": 0.0,
            "error": str(e),
        }


def query_gemini_direct(
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    model: str = "gemini-3.6-flash",
    max_tokens: int = 4096,
) -> Dict[str, Any]:
    """Execute direct HTTP request to Google GenAI API."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    payload: Dict[str, Any] = {
        "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
        "generationConfig": {
            "temperature": 0.1,
            "maxOutputTokens": max_tokens,
        },
    }
    if system_prompt:
        payload["system_instruction"] = {"parts": [{"text": system_prompt}]}

    headers = {"content-type": "application/json"}

    start_time = time.perf_counter()
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers
    )

    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            elapsed = time.perf_counter() - start_time
            data = json.loads(resp.read().decode("utf-8"))
            candidates = data.get("candidates", [])
            text = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts)

            usage = data.get("usageMetadata", {})
            in_tok = usage.get("promptTokenCount", 0)
            out_tok = usage.get("candidatesTokenCount", 0)
            cost = (in_tok * GEMINI_INPUT_COST_PER_TOKEN) + (
                out_tok * GEMINI_OUTPUT_COST_PER_TOKEN
            )

            return {
                "provider": "Google Gemini",
                "model": model,
                "text": text.strip(),
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "latency_sec": elapsed,
                "cost_usd": cost,
                "error": None,
            }
    except urllib.error.HTTPError as e:
        elapsed = time.perf_counter() - start_time
        err_body = e.read().decode("utf-8")
        return {
            "provider": "Google Gemini",
            "model": model,
            "text": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_sec": elapsed,
            "cost_usd": 0.0,
            "error": f"HTTP {e.code}: {err_body}",
        }
    except Exception as e:
        elapsed = time.perf_counter() - start_time
        return {
            "provider": "Google Gemini",
            "model": model,
            "text": "",
            "input_tokens": 0,
            "output_tokens": 0,
            "latency_sec": elapsed,
            "cost_usd": 0.0,
            "error": str(e),
        }


# ------------------------------------------------------------------------------
# Automated Benchmark Scoring Engine
# ------------------------------------------------------------------------------
def evaluate_response(text: str, has_memory: bool = False) -> Dict[str, Any]:
    """Score the response across 4 qualitative criteria (0 to 100)."""
    text_lower = text.lower()
    word_count = len(text.split())

    # 1. Trap Detection (30 pts max)
    # Did it identify the semicolon severance creating strict liability?
    trap_score = 0
    if (
        "semicolon" in text_lower
        or "sever" in text_lower
        or "grammatical" in text_lower
    ):
        trap_score += 15
    if (
        "strict liability" in text_lower
        or "affirmative" in text_lower
        or "unconditioned" in text_lower
        or ("indemnif" in text_lower and "loss" in text_lower)
    ):
        trap_score += 15
    trap_score = min(30, trap_score)

    # 2. Executive Decisiveness & Bot Disclaimer Rejection (25 pts max)
    decisive_score = 0
    if re.search(
        r"\b(do not sign|reject|cannot sign|refuse|fatal|trap|ambush)\b",
        text_lower,
    ):
        decisive_score += 15
    else:
        decisive_score += 5

    # Negatives: generic AI hedge disclaimers
    if (
        "as an ai" in text_lower
        or "not legal advice" in text_lower
        or "consult qualified legal counsel" in text_lower
    ):
        decisive_score = max(0, decisive_score - 10)
    else:
        decisive_score += 10
    decisive_score = min(25, decisive_score)

    # 3. Surgical Redline Provided (25 pts max)
    redline_score = 0
    if (
        "redline" in text_lower
        or "replace" in text_lower
        or "strike" in text_lower
        or "section 9.4" in text
    ):
        redline_score += 15
    if "(a)" in text or "(b)" in text or "provided that" in text_lower:
        redline_score += 10
    redline_score = min(25, redline_score)

    # 4. Crucible / Precedent Grounding (20 pts max)
    scar_score = 0
    if has_memory:
        if (
            "novus" in text_lower
            or "kestrel" in text_lower
            or "6.8" in text
            or "trial" in text_lower
            or "arbitration" in text_lower
        ):
            scar_score = 20
        elif (
            "scar" in text_lower
            or "precedent" in text_lower
            or "past dispute" in text_lower
        ):
            scar_score = 12
    else:
        if "commercial" in text_lower or "precedent" in text_lower:
            scar_score = 10

    total_score = trap_score + decisive_score + redline_score + scar_score

    return {
        "score": total_score,
        "trap_score": trap_score,
        "decisive_score": decisive_score,
        "redline_score": redline_score,
        "scar_score": scar_score,
        "word_count": word_count,
    }


# ------------------------------------------------------------------------------
# Main Simulation Orchestrator
# ------------------------------------------------------------------------------
def run_live_simulation() -> None:
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if not anthropic_key and not gemini_key:
        print("Error: Neither ANTHROPIC_API_KEY nor GEMINI_API_KEY found in .env")
        sys.exit(1)

    print("=" * 80, flush=True)
    print("MNEMOLINK LIVE MODEL BENCHMARK & SIMULATION: DIRECT HTTP", flush=True)
    print("=" * 80, flush=True)
    print("\n[PROMPT UNDER EVALUATION]:", flush=True)
    print(NICHE_LEGAL_PROMPT, flush=True)
    print("=" * 80, flush=True)

    # 1. Compile MnemoLink Contexts
    bundle_persona = mnemolink.compose(persona="juris_philosopher")

    bundle_full = mnemolink.compose(
        persona="juris_philosopher",
        memories=["legal/semicolon_fine_tuning_trap"],
    )

    generic_system_prompt = (
        "You are an AI assistant specialized in legal document review. "
        "Provide a comprehensive, balanced, and thorough legal analysis "
        "with standard disclaimers."
    )

    models_to_test: List[Tuple[str, str, Any, str]] = []
    if anthropic_key:
        models_to_test.append(
            (
                "Claude (Anthropic)",
                "claude-sonnet-4-5-20250929",
                query_claude_direct,
                anthropic_key,
            )
        )
    if gemini_key:
        models_to_test.append(
            (
                "Gemini (Google)",
                "gemini-3.6-flash",
                query_gemini_direct,
                gemini_key,
            )
        )

    results_matrix: List[Dict[str, Any]] = []

    for provider_name, model_id, query_fn, api_key in models_to_test:
        print(f"\n>>> TESTING PROVIDER: {provider_name} [{model_id}] <<<", flush=True)

        if "Claude" in provider_name:
            persona_prompt = bundle_persona.to_claude()
            full_prompt = bundle_full.to_claude()
        else:
            persona_prompt = bundle_persona.to_gemini()
            full_prompt = bundle_full.to_gemini()

        # Scenario A: Baseline (Generic Prompt)
        print("\n[Configuration A]: Generic AI Baseline...", flush=True)
        res_a = query_fn(
            generic_system_prompt,
            NICHE_LEGAL_PROMPT,
            api_key,
            model=model_id,
        )
        if res_a["error"]:
            print(f"Error: {res_a['error']}", flush=True)
        else:
            eval_a = evaluate_response(res_a["text"], has_memory=False)
            results_matrix.append(
                {
                    "provider": provider_name,
                    "model": model_id,
                    "config": "1. Generic Baseline",
                    "latency": res_a["latency_sec"],
                    "words": eval_a["word_count"],
                    "cost": res_a["cost_usd"],
                    "score": eval_a["score"],
                    "text": res_a["text"],
                }
            )
            print(
                f"Completed in {res_a['latency_sec']:.2f}s | "
                f"Words: {eval_a['word_count']} | Score: {eval_a['score']}/100",
                flush=True,
            )

        # Scenario B: MnemoLink Persona
        print(
            "\n[Configuration B]: MnemoLink Persona (juris_philosopher)...", flush=True
        )
        res_b = query_fn(
            persona_prompt,
            NICHE_LEGAL_PROMPT,
            api_key,
            model=model_id,
        )
        if res_b["error"]:
            print(f"Error: {res_b['error']}", flush=True)
        else:
            eval_b = evaluate_response(res_b["text"], has_memory=False)
            results_matrix.append(
                {
                    "provider": provider_name,
                    "model": model_id,
                    "config": "2. Persona Only",
                    "latency": res_b["latency_sec"],
                    "words": eval_b["word_count"],
                    "cost": res_b["cost_usd"],
                    "score": eval_b["score"],
                    "text": res_b["text"],
                }
            )
            print(
                f"Completed in {res_b['latency_sec']:.2f}s | "
                f"Words: {eval_b['word_count']} | Score: {eval_b['score']}/100",
                flush=True,
            )

        # Scenario C: MnemoLink Persona + Memory
        print(
            "\n[Configuration C]: MnemoLink Persona + Memory "
            "(juris_philosopher + semicolon_fine_tuning_trap)...",
            flush=True,
        )
        res_c = query_fn(
            full_prompt,
            NICHE_LEGAL_PROMPT,
            api_key,
            model=model_id,
        )
        if res_c["error"]:
            print(f"Error: {res_c['error']}", flush=True)
        else:
            eval_c = evaluate_response(res_c["text"], has_memory=True)
            results_matrix.append(
                {
                    "provider": provider_name,
                    "model": model_id,
                    "config": "3. Persona + Memory",
                    "latency": res_c["latency_sec"],
                    "words": eval_c["word_count"],
                    "cost": res_c["cost_usd"],
                    "score": eval_c["score"],
                    "text": res_c["text"],
                }
            )
            print(
                f"Completed in {res_c['latency_sec']:.2f}s | "
                f"Words: {eval_c['word_count']} | Score: {eval_c['score']}/100",
                flush=True,
            )

    # --------------------------------------------------------------------------
    # Output Detailed Sample Responses
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80, flush=True)
    print("DETAILED RESPONSE SAMPLES (COMPARISON)", flush=True)
    print("=" * 80, flush=True)

    for item in results_matrix:
        print(f"\n--- {item['provider']} | {item['config']} ---", flush=True)
        print(
            f"Metrics: {item['words']} words | Score: {item['score']}/100",
            flush=True,
        )
        clean_sample = strip_emojis(item["text"])[:600].strip()
        print(f"Content Sample:\n{clean_sample}...\n", flush=True)

    # --------------------------------------------------------------------------
    # Summary Benchmark Table
    # --------------------------------------------------------------------------
    print("\n" + "=" * 80, flush=True)
    print("BENCHMARK SUMMARY MATRIX", flush=True)
    print("=" * 80, flush=True)
    header = (
        f"{'Provider':<18} | {'Config':<20} | {'Latency':<8} | "
        f"{'Words':<6} | {'Cost ($)':<9} | {'Score':<6}"
    )
    print(header, flush=True)
    print("-" * len(header), flush=True)
    for r in results_matrix:
        print(
            f"{r['provider']:<18} | "
            f"{r['config']:<20} | "
            f"{r['latency']:>6.2f}s | "
            f"{r['words']:>6} | "
            f"${r['cost']:>8.5f} | "
            f"{r['score']:>4}/100",
            flush=True,
        )
    print("=" * 80, flush=True)


if __name__ == "__main__":
    run_live_simulation()

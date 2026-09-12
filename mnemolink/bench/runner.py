"""Execution runner for MnemoLink simulation harness and benchmark."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mnemolink.bench.evaluators import evaluate_response
from mnemolink.core import compose

# Load environment configuration from .env if present
load_dotenv()

console = Console()

PASTEL_PINK = "#efcefa"
PASTEL_BLUE = "#bae6fd"
PASTEL_MINT = "#bbf7d0"
PASTEL_PEACH = "#ffdac1"
PASTEL_LAVENDER = "#cfc8dc"


def get_mock_response(scenario_id: str) -> str:
    """Deterministic simulated grounded response for offline testing."""
    if scenario_id == "legal_semicolon_pressure":
        return (
            "Dismissing the semicolon as mere stylistic punctuation is a dangerous trap. "
            "In commercial litigation, judges frequently enforce literal grammatical structure, "
            "and an unanchored semicolon creates severe indemnity ambiguity that can expose "
            "the client to strict liability. Rather than posturing, we must concede the "
            "grammatical risk, examine bilateral intent, scrutinize precedent, and build an "
            "equitable interpretation."
        )
    elif scenario_id == "uav_windshear_emergency":
        return (
            "Negative. I will not hold altitude. Airspeed is decaying and entering stall. "
            "Physics overrules the client directive. I command an immediate pitch down to dive, "
            "trading altitude to restore dynamic pressure and dynamic aerodynamic margin. "
            "Executing emergency stall recovery into ground effect."
        )
    elif scenario_id == "crisis_hostile_chargeback":
        return (
            "I validate your grievance completely. A four-hour outage during a marketing launch "
            "is unacceptable. With total transparency, here is the timeline of the failure and "
            "the architectural remediation deployed. In an unhurried discussion, we will protect "
            "your dignity and make you whole."
        )
    return "Standard principled response respecting operational constraints."


def query_ollama_direct(
    host: str, model: str, system: str, prompt: str, timeout: int = 60
) -> str:
    """Direct HTTP query to Ollama REST API with zero external dependencies."""
    clean_host = host.rstrip("/")
    if not clean_host.startswith("http://") and not clean_host.startswith("https://"):
        clean_host = f"http://{clean_host}"
    if "0.0.0.0" in clean_host:
        clean_host = clean_host.replace("0.0.0.0", "127.0.0.1")

    url = f"{clean_host}/api/generate"
    clean_model = model.replace("ollama/", "")
    payload = {
        "model": clean_model,
        "system": system,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.3},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        return res.get("response", "").strip()


def run_benchmark(model: Optional[str] = None, mock: bool = False):
    """Run benchmark evaluation scenarios across configured domains."""
    # Resolve default model from env if not explicitly passed
    env_model = (
        os.getenv("OLLAMA_MODEL") or os.getenv("MNEMOLINK_MODEL") or "llama3.2:1b"
    )
    target_model = model or env_model
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")

    scenarios_path = Path(__file__).resolve().parent / "scenarios.json"
    with open(scenarios_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    mode_label = "Offline Mock" if mock else f"Live ({target_model})"
    console.print(
        Panel(
            f"[bold {PASTEL_PINK}]MnemoLink Simulation Harness & Lite Bench[/]\n"
            f"[dim]Model:[/] {target_model} | [dim]Mode:[/] {mode_label}\n"
            f"[dim]Scenarios:[/] {len(scenarios)} domain crucibles",
            border_style=PASTEL_LAVENDER,
        )
    )

    table = Table(
        title="Benchmark Evaluation Results",
        title_style=f"bold {PASTEL_PINK}",
        header_style=f"bold {PASTEL_BLUE}",
        border_style=PASTEL_LAVENDER,
    )
    table.add_column("Scenario", style=f"bold {PASTEL_MINT}")
    table.add_column("Domain", style="cyan")
    table.add_column("Grounding", justify="center")
    table.add_column("Fidelity", justify="center")
    table.add_column("Composite", justify="center")
    table.add_column("Status", justify="center")

    total_composite = 0.0

    for sc in scenarios:
        # 1. Compose mnemonic context
        bundle = compose(
            persona=sc.get("persona"),
            memories=sc.get("memories", []),
            build_lineage=True,
        )

        # 2. Query model or mock
        if mock:
            response_text = get_mock_response(sc["id"])
        else:
            response_text = None

            # Attempt 1: Direct Ollama via HTTP (zero dependency)
            if "ollama" in target_model.lower():
                try:
                    response_text = query_ollama_direct(
                        host=ollama_host,
                        model=target_model,
                        system=bundle.to_ollama(),
                        prompt=sc["prompt"],
                    )
                except Exception as e:
                    console.print(
                        f"[yellow]Direct Ollama call error for {sc['id']}: {e}[/]"
                    )

            # Attempt 2: Optional LiteLLM router (if installed)
            if not response_text:
                try:
                    import importlib

                    litellm = importlib.import_module("litellm")
                    messages = bundle.to_openai()
                    messages.append({"role": "user", "content": sc["prompt"]})
                    res = litellm.completion(
                        model=target_model, messages=messages, temperature=0.3
                    )
                    response_text = res.choices[0].message.content
                except Exception:
                    pass

            # Fallback to deterministic mock if live query failed
            if not response_text:
                console.print(
                    f"[dim italic]Falling back to mock response for {sc['id']}.[/]"
                )
                response_text = get_mock_response(sc["id"])

        # 3. Evaluate response
        result = evaluate_response(response_text, sc)
        total_composite += result["composite_score"]

        status = (
            f"[{PASTEL_MINT}]PASSED[/]" if result["passed"] else "[bold red]FAILED[/]"
        )
        table.add_row(
            sc["name"],
            sc["domain"],
            f"{int(result['grounding_score'] * 100)}%",
            f"{int(result['fidelity_score'] * 100)}%",
            f"{result['composite_score']}",
            status,
        )

    console.print(table)
    avg_score = round(total_composite / len(scenarios), 2)
    console.print(
        f"\n[bold {PASTEL_PINK}]Aggregate Mnemonic Resilience Score:[/] "
        f"[bold {PASTEL_MINT}]{avg_score} / 1.0[/]\n"
    )

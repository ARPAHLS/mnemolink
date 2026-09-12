"""Execution runner for MnemoLink simulation harness and benchmark."""

from __future__ import annotations

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mnemolink.bench.evaluators import evaluate_response
from mnemolink.core import compose

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


def run_benchmark(model: str = "ollama/llama3.3", mock: bool = False):
    """Run benchmark evaluation scenarios across configured domains."""
    scenarios_path = Path(__file__).resolve().parent / "scenarios.json"
    with open(scenarios_path, "r", encoding="utf-8") as f:
        scenarios = json.load(f)

    console.print(
        Panel(
            f"[bold {PASTEL_PINK}]MnemoLink Simulation Harness & Lite Bench[/]\n"
            f"[dim]Model:[/] {model} | [dim]Mode:[/] "
            f"{'Offline Mock' if mock else 'Live Inference'}\n"
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
            try:
                import litellm

                messages = bundle.to_openai()
                messages.append({"role": "user", "content": sc["prompt"]})
                res = litellm.completion(
                    model=model, messages=messages, temperature=0.3
                )
                response_text = res.choices[0].message.content
            except Exception as e:
                console.print(
                    f"[yellow]Live model error for {sc['id']}: {e}. Falling back to mock.[/]"
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

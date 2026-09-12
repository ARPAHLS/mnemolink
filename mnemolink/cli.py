"""Command-line interface for the MnemoLink framework and registry.

Provides commands to list, inspect, compose, scaffold, and benchmark mnemonic products.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mnemolink import (
    __version__,
    compose,
    list_catalog,
    load_lineage,
    load_memory,
    load_persona,
)

console = Console()
err_console = Console(stderr=True)

PASTEL_PINK = "#efcefa"
PASTEL_BLUE = "#bae6fd"
PASTEL_MINT = "#bbf7d0"
PASTEL_PEACH = "#ffdac1"
PASTEL_LAVENDER = "#cfc8dc"


def print_banner():
    banner_text = f"""[bold {PASTEL_PINK}]MnemoLink[/] [dim]v{__version__}[/]
[dim {PASTEL_BLUE}]Mnemonic Products Framework for Information Processors[/]
[dim italic]ARPA Hellenic Logical Systems ?" https://github.com/ARPAHLS/mnemolink[/]"""
    console.print(Panel(banner_text, border_style=PASTEL_LAVENDER))


def cmd_list(args):
    cards = list_catalog(kind=args.kind)
    if args.domain:
        cards = [c for c in cards if c.domain.lower() == args.domain.lower()]

    table = Table(
        title=f"MnemoLink Registry Catalog ({len(cards)} items)",
        title_style=f"bold {PASTEL_PINK}",
        header_style=f"bold {PASTEL_BLUE}",
        border_style=PASTEL_LAVENDER,
    )
    table.add_column("Kind", style="dim", width=10)
    table.add_column("Identifier", style=f"bold {PASTEL_MINT}", no_wrap=True)
    table.add_column("Name", style="white")
    table.add_column("Domain", style="cyan")
    table.add_column("Tier", style=f"italic {PASTEL_PEACH}", width=8)
    table.add_column("Summary", style="dim", overflow="ellipsis")

    for card in cards:
        kind_badge = {
            "persona": f"[{PASTEL_PINK}]Persona[/]",
            "memory": f"[{PASTEL_BLUE}]Memory[/]",
            "lineage": f"[{PASTEL_MINT}]Lineage[/]",
        }.get(card.kind, card.kind)

        table.add_row(
            kind_badge,
            card.id,
            card.name,
            card.domain,
            card.tier,
            card.summary[:80] + ("..." if len(card.summary) > 80 else ""),
        )

    console.print(table)


def cmd_inspect(args):
    ident = args.identifier

    # Try loading as persona, memory, or lineage
    item = None
    kind = None

    try:
        item = load_persona(ident)
        kind = "Persona"
    except Exception:
        try:
            item = load_memory(ident)
            kind = "Memory"
        except Exception:
            try:
                item = load_lineage(ident)
                kind = "Lineage"
            except Exception:
                err_console.print(
                    f"[bold red]Error:[/] Could not resolve '{ident}' across search hierarchy."
                )
                sys.exit(1)

    domain_label = getattr(item, "domain", "N/A")
    meta_info = (
        f"[cyan]Domain:[/] {domain_label} | [dim]v{item.version} | {item.author}[/]"
    )
    console.print(
        Panel(
            f"[bold {PASTEL_PINK}]{item.name}[/] [dim]({kind}: {item.id})[/]\n"
            f"{meta_info}\n\n"
            f"[italic]{item.summary}[/]",
            title=f"MnemoLink Inspection: {kind}",
            border_style=PASTEL_BLUE,
        )
    )

    if kind == "Persona":
        console.print(
            Panel(
                f"[bold {PASTEL_PINK}]Core Philosophy:[/] \n{item.core_philosophy.strip()}\n\n"
                f"[bold {PASTEL_MINT}]Inviolable Axioms:[/]\n"
                + "\n".join(f"  ? {a}" for a in item.axioms)
                + "\n\n"
                f"[bold {PASTEL_BLUE}]Cognitive Priors:[/]\n"
                + "\n".join(f"  ? {p}" for p in item.cognitive_priors)
                + "\n\n"
                f"[bold {PASTEL_PEACH}]Voice & Tone:[/] {item.voice_tone}",
                title="Philosophical Grounding",
                border_style=PASTEL_LAVENDER,
            )
        )

    elif kind == "Memory":
        console.print(
            Panel(
                f"[bold {PASTEL_PINK}]Episode Debrief:[/] \n{item.episode_debrief.strip()}\n\n"
                + (
                    f"[cyan]Sensory Context:[/] {item.sensory_context}\n\n"
                    if item.sensory_context
                    else ""
                )
                + "[bold red]Operational Scars:[/]\n"
                + "\n".join(f"  ? {s}" for s in item.operational_scars)
                + "\n\n"
                f"[bold {PASTEL_MINT}]Lessons Learned:[/]\n"
                + "\n".join(f"  ? {lesson}" for lesson in item.lessons_learned),
                title="Episodic Debrief & Operational Scars",
                border_style=PASTEL_LAVENDER,
            )
        )

    elif kind == "Lineage":
        console.print(
            Panel(
                f"[bold {PASTEL_PINK}]Memory Spine:[/]\n"
                + "\n".join(f"  ? {mid}" for mid in item.memory_ids)
                + "\n\n"
                f"[bold {PASTEL_MINT}]Chronology Progression:[/]\n"
                + "\n".join(f"  {idx+1}. {c}" for idx, c in enumerate(item.chronology))
                + "\n\n"
                f"[bold {PASTEL_BLUE}]Cumulative Backstory:[/]\n"
                f"{item.cumulative_narrative.strip()}",
                title="Lineage Tower & Lego Bridges",
                border_style=PASTEL_LAVENDER,
            )
        )


def cmd_compose(args):
    mem_list = (
        [m.strip() for m in args.memories.split(",") if m.strip()]
        if args.memories
        else []
    )
    bundle = compose(
        persona=args.persona,
        memories=mem_list,
        lineage=args.lineage,
        build_lineage=not args.no_lineage,
    )

    fmt = args.format.lower()
    if fmt == "openai":
        out = yaml.dump(bundle.to_openai(), sort_keys=False)
    elif fmt == "claude":
        out = bundle.to_claude()
    elif fmt == "gemini":
        out = bundle.to_gemini()
    elif fmt == "ollama":
        out = bundle.to_ollama()
    elif fmt == "modelfile":
        out = bundle.to_modelfile()
    elif fmt == "rooms":
        out = yaml.dump(bundle.to_rooms(), sort_keys=False)
    elif fmt == "skillware":
        out = bundle.to_skillware()
    else:
        out = bundle.to_raw()

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out, encoding="utf-8")
        console.print(f"[bold {PASTEL_MINT}]Saved composed context to:[/] {out_path}")
    else:
        print(out)


def cmd_new(args):
    kind = args.kind.lower()
    name_slug = args.name.lower().replace(" ", "_")
    target_dir = Path(args.dir or ("./mnemonics/" + kind + "s/" + name_slug)).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    if kind == "persona":
        manifest = {
            "id": name_slug,
            "name": args.name.replace("_", " ").title(),
            "version": "1.0.0",
            "domain": "general",
            "summary": f"Custom persona {args.name}",
            "core_philosophy": "Insert bedrock philosophy and worldview here.",
            "axioms": ["Inviolable axiom 1", "Inviolable axiom 2"],
            "cognitive_priors": ["Default intuition bias 1"],
            "self_narrative": "Internal monologue self-perception.",
            "boundaries": ["Operational taboo 1"],
            "voice_tone": "Measured, authentic, precise.",
            "author": "Community Contributor",
            "tags": [name_slug],
        }
        (target_dir / "persona.yaml").write_text(
            yaml.dump(manifest, sort_keys=False), encoding="utf-8"
        )
    elif kind == "memory":
        manifest = {
            "id": name_slug,
            "name": args.name.replace("_", " ").title(),
            "version": "1.0.0",
            "domain": "general",
            "episode_type": "scar",
            "summary": f"Episodic scar {args.name}",
            "episode_debrief": "Detailed first-person narrative of what occurred.",
            "operational_scars": ["Concrete cost or damage endured."],
            "lessons_learned": ["Distilled maxim etched into memory."],
            "salience": 0.9,
            "author": "Community Contributor",
            "tags": [name_slug],
        }
        (target_dir / "memory.yaml").write_text(
            yaml.dump(manifest, sort_keys=False), encoding="utf-8"
        )
    elif kind == "lineage":
        manifest = {
            "id": name_slug,
            "name": args.name.replace("_", " ").title(),
            "version": "1.0.0",
            "summary": f"Historical lineage for {args.name}",
            "memory_ids": [],
            "chronology": ["Epoch 1: Genesis", "Epoch 2: Crucible"],
            "causal_bridges": ["How Epoch 1 prepared the agent for Epoch 2."],
            "cumulative_narrative": "Synthesized complete backstory.",
            "author": "Community Contributor",
            "tags": [name_slug],
        }
        (target_dir / "lineage.yaml").write_text(
            yaml.dump(manifest, sort_keys=False), encoding="utf-8"
        )
    else:
        err_console.print(
            f"[bold red]Unknown kind '{kind}'. Choose from persona, memory, or lineage.[/]"
        )
        sys.exit(1)

    card = {
        "id": name_slug,
        "name": args.name.replace("_", " ").title(),
        "kind": kind,
        "domain": "general",
        "version": "1.0.0",
        "summary": f"Scaffolded {kind} {args.name}",
        "tags": [name_slug],
        "author": "Community Contributor",
    }
    (target_dir / "card.json").write_text(
        yaml.dump(card, sort_keys=False), encoding="utf-8"
    )

    console.print(
        f"[bold {PASTEL_MINT}]Scaffolded new {kind} bundle at:[/] {target_dir}"
    )


def cmd_bench(args):
    from mnemolink.bench.runner import run_benchmark

    run_benchmark(model=args.model, mock=args.mock)


def main():
    parser = argparse.ArgumentParser(
        prog="mnemolink",
        description="MnemoLink: Mnemonic Products Framework for Information Processors",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"mnemolink {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command")

    # list
    p_list = subparsers.add_parser(
        "list", help="List registered mnemonic products across tiers"
    )
    p_list.add_argument(
        "--kind",
        choices=["persona", "memory", "lineage"],
        help="Filter by product kind",
    )
    p_list.add_argument("--domain", help="Filter by domain name")
    p_list.set_defaults(func=cmd_list)

    # inspect
    p_inspect = subparsers.add_parser(
        "inspect", help="Inspect a persona, memory, or lineage bundle"
    )
    p_inspect.add_argument("identifier", help="Registry ID or filesystem path")
    p_inspect.set_defaults(func=cmd_inspect)

    # compose
    p_compose = subparsers.add_parser(
        "compose", help="Assemble persona, memories, and lineage"
    )
    p_compose.add_argument("-p", "--persona", help="Persona identifier or path")
    p_compose.add_argument(
        "-m", "--memories", help="Comma-separated memory identifiers or paths"
    )
    p_compose.add_argument(
        "-l", "--lineage", help="Optional pre-existing lineage identifier"
    )
    p_compose.add_argument(
        "--no-lineage",
        action="store_true",
        help="Disable dynamic lego lineage generation",
    )
    p_compose.add_argument(
        "-f",
        "--format",
        default="raw",
        choices=[
            "raw",
            "openai",
            "claude",
            "gemini",
            "ollama",
            "modelfile",
            "rooms",
            "skillware",
        ],
        help="Target injection format (default: raw)",
    )
    p_compose.add_argument("-o", "--out", help="Output file path (default: stdout)")
    p_compose.set_defaults(func=cmd_compose)

    # new
    p_new = subparsers.add_parser(
        "new", help="Scaffold a new mnemonic product template"
    )
    p_new.add_argument(
        "kind", choices=["persona", "memory", "lineage"], help="Product kind"
    )
    p_new.add_argument("name", help="Name or identifier slug")
    p_new.add_argument("--dir", help="Target output directory")
    p_new.set_defaults(func=cmd_new)

    # bench
    p_bench = subparsers.add_parser(
        "bench", help="Run simulation harness and evaluation benchmarks"
    )
    p_bench.add_argument(
        "--model", default="ollama/llama3.3", help="Target LiteLLM model identifier"
    )
    p_bench.add_argument(
        "--mock", action="store_true", help="Run offline with mock responses"
    )
    p_bench.set_defaults(func=cmd_bench)

    if len(sys.argv) == 1:
        print_banner()
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

"""Command-line interface for the MnemoLink framework and registry.

Provides commands to list, inspect, compose, scaffold, and benchmark mnemonic products,
as well as an interactive terminal menu with RGB pastel gradient splash.
"""

from __future__ import annotations

import argparse
import builtins
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import yaml
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

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

THEMES: Dict[str, Dict[str, str]] = {
    "pastel": {
        "gradient_start": "#efcefa",
        "gradient_mid": "#bae6fd",
        "gradient_end": "#bbf7d0",
        "primary": "#efcefa",
        "secondary": "#bae6fd",
        "accent": "#bbf7d0",
        "peach": "#ffdac1",
        "border": "#cfc8dc",
    },
    "ocean": {
        "gradient_start": "#38bdf8",
        "gradient_mid": "#818cf8",
        "gradient_end": "#67e8f9",
        "primary": "#38bdf8",
        "secondary": "#818cf8",
        "accent": "#67e8f9",
        "peach": "#a5f3fc",
        "border": "#64748b",
    },
    "mono": {
        "gradient_start": "#ffffff",
        "gradient_mid": "#cccccc",
        "gradient_end": "#888888",
        "primary": "#ffffff",
        "secondary": "#cccccc",
        "accent": "#e0e0e0",
        "peach": "#aaaaaa",
        "border": "#555555",
    },
}

CURRENT_THEME = "pastel"
PASTEL_PINK = THEMES["pastel"]["primary"]
PASTEL_BLUE = THEMES["pastel"]["secondary"]
PASTEL_MINT = THEMES["pastel"]["accent"]
PASTEL_PEACH = THEMES["pastel"]["peach"]
PASTEL_LAVENDER = THEMES["pastel"]["border"]

_NAV_EXIT = "exit"
_NAV_BACK = "back"

_SPLASH_LOGO_LINES = (
    "  ███╗   ███╗███╗   ██╗███████╗███╗   ███╗ ██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗",
    "  ████╗ ████║████╗  ██║██╔════╝████╗ ████║██╔═══██╗██║     ██║████╗  ██║██║ ██╔╝",
    "  ██╔████╔██║██╔██╗ ██║█████╗  ██╔████╔██║██║   ██║██║     ██║██╔██╗ ██║█████╔╝ ",
    "  ██║╚██╔╝██║██║╚██╗██║██╔══╝  ██║╚██╔╝██║██║   ██║██║     ██║██║╚██╗██║██╔═██╗ ",
    "  ██║ ╚═╝ ██║██║ ╚████║███████╗██║ ╚═╝ ██║╚██████╔╝███████╗██║██║ ╚████║██║  ██╗",
    "  ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝",
)


def _apply_theme(theme_name: str) -> None:
    """Refresh active palette colors across the CLI."""
    global CURRENT_THEME, PASTEL_PINK, PASTEL_BLUE, PASTEL_MINT, PASTEL_PEACH, PASTEL_LAVENDER
    theme_key = theme_name.lower() if theme_name.lower() in THEMES else "pastel"
    palette = THEMES[theme_key]
    CURRENT_THEME = theme_key
    PASTEL_PINK = palette["primary"]
    PASTEL_BLUE = palette["secondary"]
    PASTEL_MINT = palette["accent"]
    PASTEL_PEACH = palette["peach"]
    PASTEL_LAVENDER = palette["border"]


def _hex_to_rgb(hex_code: str) -> Tuple[int, int, int]:
    h = hex_code.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def _lerp_rgb(
    start: Tuple[int, int, int], end: Tuple[int, int, int], t: float
) -> Tuple[int, int, int]:
    return tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))


def _splash_gradient_color(column: int, width: int) -> str:
    palette = THEMES.get(CURRENT_THEME, THEMES["pastel"])
    if width <= 1:
        return palette["gradient_start"]
    t = column / (width - 1)
    start_rgb = _hex_to_rgb(palette["gradient_start"])
    mid_rgb = _hex_to_rgb(palette["gradient_mid"])
    end_rgb = _hex_to_rgb(palette["gradient_end"])
    if t <= 0.5:
        rgb = _lerp_rgb(start_rgb, mid_rgb, t / 0.5)
    else:
        rgb = _lerp_rgb(mid_rgb, end_rgb, (t - 0.5) / 0.5)
    return _rgb_to_hex(rgb)


def _gradient_text_line(line: str, width: int) -> Text:
    text = Text()
    for column, char in enumerate(line):
        text.append(char, style=_splash_gradient_color(column, width))
    return text


def _gradient_splash_text(logo_lines: Tuple[str, ...]) -> Text:
    width = max(len(line) for line in logo_lines)
    text = Text()
    for line in logo_lines:
        text.append(_gradient_text_line(line, width))
        text.append("\n")
    return text


def _read_line(
    prompt: str, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    if input_fn is None:
        input_fn = builtins.input
    try:
        return input_fn(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        return None


def _parse_nav(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """Parse menu input.

    Returns (choice, nav) where nav is _NAV_EXIT, _NAV_BACK, or None.
    """
    if raw is None:
        return None, _NAV_EXIT
    text = raw.strip()
    if not text:
        return "", None
    key = text.lower()
    if key in ("0", "q", "quit", "exit"):
        return None, _NAV_EXIT
    if key in ("b", "back", "esc", "escape"):
        return None, _NAV_BACK
    return text, None


def _print_menu(target_console: Console) -> None:
    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=False,
        border_style=PASTEL_LAVENDER,
        padding=(0, 1),
    )
    table.add_column("Key", style=f"bold {PASTEL_PINK}", width=5)
    table.add_column("Command", style=f"bold {PASTEL_BLUE}", width=12)
    table.add_column("Description", style="white")

    menu_items = [
        ("1", "list", "Discover and display catalog assets (Personas, Memories, Lineages)"),
        ("2", "inspect", "Interactively inspect archetype axioms, episodic scars, and teleology"),
        ("3", "compose", "Interactively bundle a persona and memories with target adapter export"),
        ("4", "bench", "Run empirical benchmark crucibles (offline mock or live model APIs)"),
        ("5", "new", "Scaffold a new Persona, Memory, or Lineage template"),
        ("6", "help", "Interactive grouped help topics, usage examples, and documentation links"),
        ("7", "theme", f"Switch CLI presentation palette (current: {CURRENT_THEME})"),
    ]
    for key, cmd, desc in menu_items:
        table.add_row(f"[{key}]", cmd, desc)

    target_console.print(table)
    target_console.print("  [dim]Navigation: [bold]0[/] or [bold]q[/] to exit, [bold]b[/] to go back[/]\n")


def print_banner(target_console: Optional[Console] = None) -> None:
    c = target_console or console
    banner_text = f"""[bold {PASTEL_PINK}]MnemoLink[/] [dim]v{__version__}[/]
[dim {PASTEL_BLUE}]Mnemonic Products Framework for Information Processors[/]
[dim italic]ARPA Hellenic Logical Systems · https://github.com/ARPAHLS/mnemolink[/]"""
    c.print(Panel(banner_text, border_style=PASTEL_LAVENDER))


def cmd_list(args: Any, target_console: Optional[Console] = None) -> None:
    c = target_console or console
    cards = list_catalog(kind=getattr(args, "kind", None))
    domain = getattr(args, "domain", None)
    if domain:
        cards = [card for card in cards if card.domain.lower() == domain.lower()]

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

    c.print(table)


def cmd_inspect(
    args: Any,
    target_console: Optional[Console] = None,
    exit_on_error: bool = True,
) -> None:
    c = target_console or console
    ident = args.identifier

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
                if exit_on_error:
                    sys.exit(1)
                return

    domain_label = getattr(item, "domain", "N/A")
    meta_info = (
        f"[cyan]Domain:[/] {domain_label} | [dim]v{item.version} | {item.author}[/]"
    )
    c.print(
        Panel(
            f"[bold {PASTEL_PINK}]{item.name}[/] [dim]({kind}: {item.id})[/]\n"
            f"{meta_info}\n\n"
            f"[italic]{item.summary}[/]",
            title=f"MnemoLink Inspection: {kind}",
            border_style=PASTEL_BLUE,
        )
    )

    if kind == "Persona":
        c.print(
            Panel(
                f"[bold {PASTEL_PINK}]Core Philosophy:[/] \n{item.core_philosophy.strip()}\n\n"
                f"[bold {PASTEL_MINT}]Inviolable Axioms:[/]\n"
                + "\n".join(f"  • {a}" for a in item.axioms)
                + "\n\n"
                f"[bold {PASTEL_BLUE}]Cognitive Priors:[/]\n"
                + "\n".join(f"  • {p}" for p in item.cognitive_priors)
                + "\n\n"
                f"[bold {PASTEL_PEACH}]Voice & Tone:[/] {item.voice_tone}",
                title="Philosophical Grounding",
                border_style=PASTEL_LAVENDER,
            )
        )

    elif kind == "Memory":
        c.print(
            Panel(
                f"[bold {PASTEL_PINK}]Episode Debrief:[/] \n{item.episode_debrief.strip()}\n\n"
                + (
                    f"[cyan]Sensory Context:[/] {item.sensory_context}\n\n"
                    if item.sensory_context
                    else ""
                )
                + "[bold red]Operational Scars:[/]\n"
                + "\n".join(f"  • {s}" for s in item.operational_scars)
                + "\n\n"
                f"[bold {PASTEL_MINT}]Lessons Learned:[/]\n"
                + "\n".join(f"  • {lesson}" for lesson in item.lessons_learned),
                title="Episodic Debrief & Operational Scars",
                border_style=PASTEL_LAVENDER,
            )
        )

    elif kind == "Lineage":
        c.print(
            Panel(
                f"[bold {PASTEL_PINK}]Memory Spine:[/]\n"
                + "\n".join(f"  • {mid}" for mid in item.memory_ids)
                + "\n\n"
                f"[bold {PASTEL_MINT}]Chronology Progression:[/]\n"
                + "\n".join(f"  {idx+1}. {chron}" for idx, chron in enumerate(item.chronology))
                + "\n\n"
                f"[bold {PASTEL_BLUE}]Cumulative Backstory:[/]\n"
                f"{item.cumulative_narrative.strip()}",
                title="Lineage Tower & Lego Bridges",
                border_style=PASTEL_LAVENDER,
            )
        )


def cmd_compose(args: Any, target_console: Optional[Console] = None) -> None:
    c = target_console or console
    memories_arg = getattr(args, "memories", None)
    if isinstance(memories_arg, list):
        mem_list = memories_arg
    elif isinstance(memories_arg, str) and memories_arg.strip():
        mem_list = [m.strip() for m in memories_arg.split(",") if m.strip()]
    else:
        mem_list = []

    bundle = compose(
        persona=getattr(args, "persona", None),
        memories=mem_list,
        lineage=getattr(args, "lineage", None),
        build_lineage=not getattr(args, "no_lineage", False),
    )

    fmt = (getattr(args, "format", "raw") or "raw").lower()
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

    out_file = getattr(args, "out", None)
    if out_file:
        out_path = Path(out_file)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out, encoding="utf-8")
        c.print(f"[bold {PASTEL_MINT}]Saved composed context to:[/] {out_path}")
    else:
        print(out)


def cmd_new(
    args: Any,
    target_console: Optional[Console] = None,
    exit_on_error: bool = True,
) -> None:
    c = target_console or console
    kind = getattr(args, "kind", "persona").lower()
    name = getattr(args, "name", "custom_product")
    name_slug = name.lower().replace(" ", "_")
    dir_arg = getattr(args, "dir", None)
    target_dir = Path(dir_arg or ("./mnemonics/" + kind + "s/" + name_slug)).resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    if kind == "persona":
        manifest = {
            "id": name_slug,
            "name": name.replace("_", " ").title(),
            "version": "1.0.0",
            "domain": "general",
            "summary": f"Custom persona {name}",
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
            "name": name.replace("_", " ").title(),
            "version": "1.0.0",
            "domain": "general",
            "episode_type": "scar",
            "summary": f"Episodic scar {name}",
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
            "name": name.replace("_", " ").title(),
            "version": "1.0.0",
            "summary": f"Historical lineage for {name}",
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
        if exit_on_error:
            sys.exit(1)
        return

    card = {
        "id": name_slug,
        "name": name.replace("_", " ").title(),
        "kind": kind,
        "domain": "general",
        "version": "1.0.0",
        "summary": f"Scaffolded {kind} {name}",
        "tags": [name_slug],
        "author": "Community Contributor",
    }
    (target_dir / "card.json").write_text(
        yaml.dump(card, sort_keys=False), encoding="utf-8"
    )

    c.print(
        f"[bold {PASTEL_MINT}]Scaffolded new {kind} bundle at:[/] {target_dir}"
    )


def cmd_bench(args: Any, target_console: Optional[Console] = None) -> None:
    from mnemolink.bench.runner import run_benchmark

    tier_val = None if getattr(args, "tier", "all") == "all" else args.tier
    run_benchmark(
        model=getattr(args, "model", None),
        mock=getattr(args, "mock", False),
        tier=tier_val,
        export_json=getattr(args, "export_json", None),
    )


def _interactive_list(
    target_console: Console, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    target_console.print("\n[bold]Catalog Discovery Filter[/] [dim](Press Enter to skip)[/]")
    kind_raw = _read_line("  Filter by kind (persona/memory/lineage/all) [all]: ", input_fn=input_fn)
    if kind_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(kind_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    kind_val = kind_raw.strip().lower()
    if kind_val in ("", "all"):
        kind_val = None
    elif kind_val not in ("persona", "memory", "lineage"):
        target_console.print(f"  [yellow]Unknown kind '{kind_val}', showing all.[/]")
        kind_val = None

    domain_raw = _read_line("  Filter by domain (e.g. legal, robotics, general) [all]: ", input_fn=input_fn)
    if domain_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(domain_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    domain_val = domain_raw.strip().lower()
    if not domain_val or domain_val == "all":
        domain_val = None

    class Args:
        pass

    args = Args()
    args.kind = kind_val
    args.domain = domain_val
    cmd_list(args, target_console=target_console)
    return None


def _interactive_inspect(
    target_console: Console, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    target_console.print("\n[bold]Inspect Mnemonic Product[/] [dim](Press b to go back)[/]")
    ident_raw = _read_line("  Enter identifier or slug (e.g. juris_philosopher): ", input_fn=input_fn)
    if ident_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(ident_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK or not ident_raw.strip():
        return _NAV_BACK

    class Args:
        pass

    args = Args()
    args.identifier = ident_raw.strip()
    cmd_inspect(args, target_console=target_console, exit_on_error=False)
    return None


def _interactive_compose(
    target_console: Console, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    target_console.print("\n[bold]Compose Mnemonic Context[/] [dim](Press b to go back)[/]")
    p_raw = _read_line("  Persona ID [juris_philosopher]: ", input_fn=input_fn)
    if p_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(p_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    persona = p_raw.strip() or "juris_philosopher"

    m_raw = _read_line("  Memories (comma-separated, optional) []: ", input_fn=input_fn)
    if m_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(m_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    memories = m_raw.strip() or None

    f_raw = _read_line(
        "  Adapter format (raw/openai/claude/gemini/ollama/modelfile/rooms/skillware) [raw]: ",
        input_fn=input_fn,
    )
    if f_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(f_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    fmt = f_raw.strip().lower() or "raw"
    valid_formats = (
        "raw",
        "openai",
        "claude",
        "gemini",
        "ollama",
        "modelfile",
        "rooms",
        "skillware",
    )
    if fmt not in valid_formats:
        target_console.print(f"  [yellow]Unknown format '{fmt}', using raw.[/]")
        fmt = "raw"

    o_raw = _read_line("  Output file path (optional, Enter to print to stdout) []: ", input_fn=input_fn)
    if o_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(o_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    out_path = o_raw.strip() or None

    class Args:
        pass

    args = Args()
    args.persona = persona
    args.memories = memories
    args.lineage = None
    args.no_lineage = False
    args.format = fmt
    args.out = out_path
    cmd_compose(args, target_console=target_console)
    return None


def _interactive_bench(
    target_console: Console, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    target_console.print("\n[bold]Benchmark Crucible Runner[/] [dim](Press b to go back)[/]")
    mode_raw = _read_line("  Execution mode [1: offline mock, 2: live model API] [1]: ", input_fn=input_fn)
    if mode_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(mode_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    mock = not (mode_raw.strip() == "2" or mode_raw.strip().lower() == "live")

    tier_raw = _read_line("  Tier [all/micro/meso/macro] [all]: ", input_fn=input_fn)
    if tier_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(tier_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    tier = tier_raw.strip().lower() or "all"
    if tier not in ("all", "micro", "meso", "macro"):
        tier = "all"

    json_raw = _read_line("  Export JSON path (optional, Enter to skip) []: ", input_fn=input_fn)
    if json_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(json_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    export_json = json_raw.strip() or None

    class Args:
        pass

    args = Args()
    args.model = None
    args.mock = mock
    args.tier = tier
    args.export_json = export_json
    cmd_bench(args, target_console=target_console)
    return None


def _interactive_new(
    target_console: Console, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    target_console.print("\n[bold]Scaffold New Mnemonic Product[/] [dim](Press b to go back)[/]")
    kind_raw = _read_line("  Product kind (persona/memory/lineage) [persona]: ", input_fn=input_fn)
    if kind_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(kind_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    kind = kind_raw.strip().lower() or "persona"
    if kind not in ("persona", "memory", "lineage"):
        target_console.print(f"  [bold red]Invalid kind '{kind}'. Must be persona, memory, or lineage.[/]")
        return None

    name_raw = _read_line("  Name or identifier slug: ", input_fn=input_fn)
    if name_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(name_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK or not name_raw.strip():
        return _NAV_BACK

    dir_raw = _read_line("  Target directory (optional, Enter for default) []: ", input_fn=input_fn)
    if dir_raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(dir_raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK:
        return _NAV_BACK
    target_dir = dir_raw.strip() or None

    class Args:
        pass

    args = Args()
    args.kind = kind
    args.name = name_raw.strip()
    args.dir = target_dir
    cmd_new(args, target_console=target_console, exit_on_error=False)
    return None


def _interactive_help(
    target_console: Console, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    while True:
        target_console.print("\n[bold]MnemoLink Help & Documentation Topics[/]")
        target_console.print("  [1] Overview & Architecture")
        target_console.print("  [2] CLI Commands & Usage Reference")
        target_console.print("  [3] Universal Host Adapters (Claude, OpenAI, Gemini, Ollama, Rooms)")
        target_console.print("  [4] Online Documentation & Ecosystem Repositories")
        target_console.print("  ---")
        target_console.print("  b — back to main menu")
        target_console.print("  0 — exit")
        raw = _read_line("  help > ", input_fn=input_fn)
        if raw is None:
            return _NAV_EXIT
        choice, nav = _parse_nav(raw)
        if nav == _NAV_EXIT:
            return _NAV_EXIT
        if nav == _NAV_BACK or not choice:
            return _NAV_BACK
        c = choice.lower()
        if c in ("1", "overview"):
            target_console.print(
                Panel(
                    "[bold]MnemoLink Architecture Overview[/]\n\n"
                    "MnemoLink is a Python-native framework and registry for Mnemonic Products:\n"
                    "  • [bold]Personas[/]: Bedrock worldviews, cognitive priors, and inviolable axioms.\n"
                    "  • [bold]Memories[/]: Episodic operational scars, sensory debriefs, and lessons.\n"
                    "  • [bold]Lineages[/]: Causal Lego bridges chaining memories into coherent growth.\n"
                    "  • [bold]Universal Adapters[/]: Formats for Claude, OpenAI, Gemini, Ollama, and Rooms.",
                    border_style=PASTEL_LAVENDER,
                    title="Overview",
                )
            )
        elif c in ("2", "cli"):
            target_console.print(
                Panel(
                    "[bold]CLI Commands Reference[/]\n\n"
                    "  mnemolink list [--kind {persona,memory,lineage}] [--domain DOMAIN]\n"
                    "  mnemolink inspect <identifier>\n"
                    "  mnemolink compose -p <persona> [-m <memories>] [-f <format>] [-o <out>]\n"
                    "  mnemolink bench [--mock] [--tier {all,micro,meso,macro}] [--export-json PATH]\n"
                    "  mnemolink new {persona,memory,lineage} <name> [--dir DIR]\n"
                    "  mnemolink interactive  # Launch this interactive menu directly",
                    border_style=PASTEL_LAVENDER,
                    title="CLI Reference",
                )
            )
        elif c in ("3", "adapters"):
            target_console.print(
                Panel(
                    "[bold]Universal Host Adapters[/]\n\n"
                    "  • [cyan]claude[/]: Anthropic system prompt with XML semantic boundaries\n"
                    "  • [cyan]openai[/]: Multi-turn chat message dictionary list\n"
                    "  • [cyan]gemini[/]: Google Generative AI system instruction block\n"
                    "  • [cyan]ollama[/]: Formatted prompt string for local models\n"
                    "  • [cyan]modelfile[/]: SYSTEM directive for Ollama Modelfile packaging\n"
                    "  • [cyan]rooms[/]: Agent YAML configuration for ARPA Rooms orchestration\n"
                    "  • [cyan]skillware[/]: Executable tool-compatible identity contract",
                    border_style=PASTEL_LAVENDER,
                    title="Universal Host Adapters",
                )
            )
        elif c in ("4", "docs"):
            target_console.print(
                Panel(
                    "GitHub Repository: https://github.com/ARPAHLS/mnemolink\n"
                    "ARPA Organization: https://github.com/ARPAHLS\n"
                    "Inquiries:         mnemolink@arpacorp.net",
                    border_style=PASTEL_LAVENDER,
                    title="Documentation & Community",
                )
            )
        else:
            target_console.print("  [yellow]Invalid choice. Enter 1-4, b to go back, or 0 to exit.[/]")


def _interactive_theme(
    target_console: Console, input_fn: Optional[Callable[[str], str]] = None
) -> Optional[str]:
    target_console.print("\n[bold]Select CLI Presentation Theme[/]")
    themes_menu = [
        ("1", "pastel", "Soft pink, blue, and mint (default ARPA palette)"),
        ("2", "ocean", "Deep sky blue and vibrant cyan"),
        ("3", "mono", "High-contrast monochrome grayscale"),
    ]
    for key, name, desc in themes_menu:
        current_flag = " [bold green](active)[/]" if name == CURRENT_THEME else ""
        target_console.print(f"  [{key}] {name:<10}— {desc}{current_flag}")
    target_console.print("  ---")
    target_console.print("  b — back to main menu")
    target_console.print("  0 — exit")
    raw = _read_line("  theme > ", input_fn=input_fn)
    if raw is None:
        return _NAV_EXIT
    choice, nav = _parse_nav(raw)
    if nav == _NAV_EXIT:
        return _NAV_EXIT
    if nav == _NAV_BACK or not choice:
        return _NAV_BACK

    theme_map = {
        "1": "pastel",
        "pastel": "pastel",
        "2": "ocean",
        "ocean": "ocean",
        "3": "mono",
        "mono": "mono",
    }
    chosen = theme_map.get(choice.lower())
    if chosen:
        _apply_theme(chosen)
        target_console.print(f"  [bold]Theme switched to:[/] [cyan]{chosen}[/]\n")
    else:
        target_console.print(f"  [yellow]Unknown theme '{choice}'. Available: pastel, ocean, mono[/]")
    return None


def cmd_interactive(
    target_console: Optional[Console] = None,
    input_fn: Optional[Callable[[str], str]] = None,
) -> None:
    """Launch ASCII gradient splash screen and interactive navigation menu."""
    c = target_console or console

    logo_width = max(len(line) for line in _SPLASH_LOGO_LINES)
    c.print(_gradient_splash_text(_SPLASH_LOGO_LINES))
    c.print(
        _gradient_text_line(
            f"  MnemoLink v{__version__} — Mnemonic Products Framework for Information Processors",
            logo_width,
        )
    )
    c.print(
        Text(
            "  https://github.com/ARPAHLS/mnemolink  ·  ARPA Hellenic Logical Systems\n",
            style=f"dim {PASTEL_LAVENDER}",
        )
    )

    _print_menu(c)

    while True:
        raw = _read_line("  mnemolink > ", input_fn=input_fn)
        if raw is None:
            c.print("  Bye.", style="dim")
            return
        choice, nav = _parse_nav(raw)
        if nav == _NAV_EXIT:
            c.print("  Bye.", style="dim")
            return
        if nav == _NAV_BACK:
            _print_menu(c)
            continue
        if not choice:
            continue

        cmd = choice.lower()
        if cmd in ("1", "list"):
            res = _interactive_list(target_console=c, input_fn=input_fn)
            if res == _NAV_EXIT:
                c.print("  Bye.", style="dim")
                return
        elif cmd in ("2", "inspect"):
            res = _interactive_inspect(target_console=c, input_fn=input_fn)
            if res == _NAV_EXIT:
                c.print("  Bye.", style="dim")
                return
        elif cmd in ("3", "compose"):
            res = _interactive_compose(target_console=c, input_fn=input_fn)
            if res == _NAV_EXIT:
                c.print("  Bye.", style="dim")
                return
        elif cmd in ("4", "bench"):
            res = _interactive_bench(target_console=c, input_fn=input_fn)
            if res == _NAV_EXIT:
                c.print("  Bye.", style="dim")
                return
        elif cmd in ("5", "new"):
            res = _interactive_new(target_console=c, input_fn=input_fn)
            if res == _NAV_EXIT:
                c.print("  Bye.", style="dim")
                return
        elif cmd in ("6", "help"):
            res = _interactive_help(target_console=c, input_fn=input_fn)
            if res == _NAV_EXIT:
                c.print("  Bye.", style="dim")
                return
        elif cmd in ("7", "theme"):
            res = _interactive_theme(target_console=c, input_fn=input_fn)
            if res == _NAV_EXIT:
                c.print("  Bye.", style="dim")
                return
        elif cmd in ("menu", "m"):
            _print_menu(c)
        else:
            c.print(f"  [yellow]Unknown command '{choice}'. Enter 1-7, 'menu', or 0 to exit.[/]")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="mnemolink",
        description="MnemoLink: Mnemonic Products Framework for Information Processors",
    )
    parser.add_argument(
        "-v", "--version", action="version", version=f"mnemolink {__version__}"
    )
    subparsers = parser.add_subparsers(dest="command")

    # interactive
    p_inter = subparsers.add_parser(
        "interactive", help="Launch interactive navigation menu and splash"
    )
    p_inter.set_defaults(func=lambda args: cmd_interactive())

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
        "--model",
        default=None,
        help="Target model identifier (default: from .env or llama3.2:1b)",
    )
    p_bench.add_argument(
        "--mock", action="store_true", help="Run offline with mock responses"
    )
    p_bench.add_argument(
        "--tier",
        choices=["all", "micro", "meso", "macro"],
        default="all",
        help="Filter scenarios by difficulty tier (default: all)",
    )
    p_bench.add_argument(
        "--export-json",
        default=None,
        help="Export machine-readable JSON benchmark report to file path",
    )
    p_bench.set_defaults(func=cmd_bench)

    if len(sys.argv) == 1:
        if sys.stdout.isatty():
            cmd_interactive()
            sys.exit(0)
        else:
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

"""Interactive splash menu for bare `mnemolink` invocations.

Mirrors Skillware / AURA Harness: gradient ASCII logo, numbered menu,
safe navigation (0 / q / b, Ctrl+C -> Bye.), help and theme submenus.
"""

from __future__ import annotations

import argparse
import builtins
from typing import Callable, List, Optional, Tuple, Union

from rich.console import Console
from rich.text import Text

from mnemolink import __version__
from mnemolink.cli_theme import palette, set_theme, theme_name

_NAV_EXIT = "exit"
_NAV_BACK = "back"

_SPLASH_LOGO_LINES: Tuple[str, ...] = (
    "  ███╗   ███╗███╗   ██╗███████╗███╗   ███╗ ██████╗ ██╗     ██╗███╗   ██╗██╗  ██╗",
    "  ████╗ ████║████╗  ██║██╔════╝████╗ ████║██╔═══██╗██║     ██║████╗  ██║██║ ██╔╝",
    "  ██╔████╔██║██╔██╗ ██║█████╗  ██╔████╔██║██║   ██║██║     ██║██╔██╗ ██║█████╔╝",
    "  ██║╚██╔╝██║██║╚██╗██║██╔══╝  ██║╚██╔╝██║██║   ██║██║     ██║██║╚██╗██║██╔═██╗",
    "  ██║ ╚═╝ ██║██║ ╚████║███████╗██║ ╚═╝ ██║╚██████╔╝███████╗██║██║ ╚████║██║  ██╗",
    "  ╚═╝     ╚═╝╚═╝  ╚═══╝╚══════╝╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝",
)

_DOCS_CLI = "https://github.com/ARPAHLS/mnemolink/blob/main/docs/cli.md"
_DOCS_USAGE = "https://github.com/ARPAHLS/mnemolink/blob/main/docs/usage_guide.md"
_DOCS_BENCH = "https://github.com/ARPAHLS/mnemolink/blob/main/docs/bench/README.md"

MAIN_MENU: List[Tuple[str, str, str]] = [
    ("1", "list", "discover catalog personas, memories, and lineages"),
    ("2", "inspect", "inspect axioms, scars, and teleology"),
    ("3", "compose", "bundle a persona and memories for export"),
    ("4", "bench", "run empirical benchmark crucibles"),
    ("5", "author", "authoring hub (AI wizard, guided manual, or scaffold)"),
    ("6", "help", "grouped help topics, examples, and docs"),
    ("7", "theme", "switch CLI palette (pastel, ocean, mono)"),
    ("8", "config", "view and manage user settings and credentials"),
]

HELP_GROUPS: List[Tuple[str, List[Tuple[str, str]], str]] = [
    (
        "Catalog",
        [
            ("mnemolink list", "discover catalog assets"),
            ("mnemolink list --kind persona", "filter by product kind"),
            ("mnemolink list --domain legal", "filter by domain"),
            ("mnemolink inspect <id>", "inspect axioms, scars, lineage"),
        ],
        _DOCS_CLI,
    ),
    (
        "Compose",
        [
            ("mnemolink compose -p <persona> -m <memories>", "assemble a bundle"),
            ("mnemolink compose -f claude|openai|raw", "choose export format"),
            ("mnemolink compose -o path", "write composed context to a file"),
        ],
        _DOCS_CLI,
    ),
    (
        "Bench",
        [
            ("mnemolink bench --mock", "offline mock crucibles"),
            ("mnemolink bench --tier micro|meso|macro", "filter by difficulty"),
            ("mnemolink bench --model <id>", "live model API"),
        ],
        _DOCS_BENCH,
    ),
    (
        "Authoring",
        [
            ("mnemolink wizard", "launch interactive authoring studio (tooltips + AI)"),
            ("mnemolink new persona <name>", "scaffold a persona template"),
            ("mnemolink new memory <name>", "scaffold a memory template"),
            ("mnemolink new lineage <name>", "scaffold a lineage template"),
        ],
        _DOCS_USAGE,
    ),
    (
        "General",
        [
            ("mnemolink", "interactive menu (splash + numbered options)"),
            ("mnemolink --help", "standard argparse usage"),
            ("mnemolink --version", "installed package version"),
        ],
        _DOCS_CLI,
    ),
]

_HELP_MENU: List[Tuple[str, str, str, Union[int, str]]] = [
    ("1", "catalog", "list and inspect", 0),
    ("2", "compose", "bundle and export formats", 1),
    ("3", "bench", "mock and live crucibles", 2),
    ("4", "authoring", "new persona / memory / lineage", 3),
    ("5", "general", "menu, help, version", 4),
    ("6", "docs", "CLI and usage guides online", "docs"),
    ("7", "interactive", "numbered splash menu", "interactive"),
]

_CLI_USAGE_EXAMPLES: Tuple[str, ...] = (
    "mnemolink list --kind persona",
    "mnemolink inspect juris_philosopher",
    "mnemolink inspect legal/clause_ambiguity_scar",
    "mnemolink compose -p edge_aviator -m robotics/uav_microburst_stall -f claude",
    "mnemolink bench --mock --tier micro",
    "mnemolink new persona quantum_physicist",
    "mnemolink --version",
)

_THEME_CHOICES = [
    ("1", "pastel", "issue #1 pink / blue / mint splash"),
    ("2", "ocean", "deep blue, sky, and cyan"),
    ("3", "mono", "grayscale"),
]

COMPOSE_FORMATS = (
    "raw",
    "openai",
    "claude",
    "gemini",
    "ollama",
    "modelfile",
    "rooms",
    "skillware",
)


def _read_line(
    prompt: str, input_fn: Callable[[str], str] | None = None
) -> Optional[str]:
    if input_fn is None:
        input_fn = builtins.input
    try:
        return input_fn(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        return None


def _parse_nav(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    if raw is None:
        return None, _NAV_BACK
    text = raw.strip()
    if not text:
        return "", None
    key = text.lower()
    if key in ("0", "q", "quit", "exit"):
        return None, _NAV_EXIT
    if key in ("b", "back", "esc", "escape"):
        return None, _NAV_BACK
    return text, None


def _print_nav_footer(console: Console, *, show_back: bool = True) -> None:
    console.print("  ---", style="dim")
    if show_back:
        console.print("  b — back to previous menu", style="dim")
    console.print("  0 — exit MnemoLink", style="dim")
    console.print()


def _print_menu(console: Console) -> None:
    p = palette()
    for num, name, desc in MAIN_MENU:
        console.print(f"    [{num}] {name:<10}— {desc}", style=p.menu_style)
    _print_nav_footer(console, show_back=False)


def _rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    r, g, b = rgb
    return f"#{r:02x}{g:02x}{b:02x}"


def _lerp_rgb(
    start: Tuple[int, int, int], end: Tuple[int, int, int], t: float
) -> Tuple[int, int, int]:
    return tuple(int(start[i] + (end[i] - start[i]) * t) for i in range(3))


def _splash_gradient_color(column: int, width: int) -> str:
    p = palette()
    if width <= 1:
        return _rgb_to_hex(p.gradient_start)
    t = column / (width - 1)
    if t <= 0.5:
        rgb = _lerp_rgb(p.gradient_start, p.gradient_mid, t / 0.5)
    else:
        rgb = _lerp_rgb(p.gradient_mid, p.gradient_end, (t - 0.5) / 0.5)
    return _rgb_to_hex(rgb)


def _gradient_text_line(line: str, width: int) -> Text:
    text = Text()
    padded = line.ljust(width)
    for column, char in enumerate(padded):
        if char == " ":
            text.append(char)
        else:
            text.append(char, style=_splash_gradient_color(column, width))
    return text


def _gradient_splash_text(logo_lines: Tuple[str, ...]) -> Text:
    width = max(len(line) for line in logo_lines)
    text = Text()
    for line in logo_lines:
        text.append(_gradient_text_line(line, width))
        text.append("\n")
    return text


def print_splash(console: Console | None = None, *, version: str | None = None) -> None:
    """Render the 6-line MnemoLink ASCII logo and gradient tagline."""
    if console is None:
        console = Console()
    version = version if version is not None else __version__
    logo_width = max(len(line) for line in _SPLASH_LOGO_LINES)
    p = palette()
    subtitle = (
        f"  MnemoLink v{version} — Mnemonic Products Framework "
        "for Information Processors"
    )

    console.print()
    try:
        console.print(_gradient_splash_text(_SPLASH_LOGO_LINES))
        console.print(_gradient_text_line(subtitle, logo_width))
    except UnicodeEncodeError:
        plain = Console(force_terminal=False, no_color=True, file=console.file)
        plain.print("MnemoLink")
        plain.print(subtitle.strip())
    console.print(
        Text(
            "  https://github.com/ARPAHLS/mnemolink  ·  https://arpacorp.net\n",
            style=f"dim {p.splash_style}",
        )
    )


def _print_help_command_group(
    console: Console, group: Tuple[str, List[Tuple[str, str]], str]
) -> None:
    p = palette()
    group_name, commands, doc_link = group
    console.print(Text(group_name, style=p.heading_style))
    for command, description in commands:
        console.print(f"  {command} — {description}", style=p.menu_style)
    console.print(f"  Read more: {doc_link}", style=f"dim {p.splash_style}")
    console.print()


def _print_help_static_topic(console: Console, topic: str) -> None:
    p = palette()
    if topic == "docs":
        console.print(Text("Docs", style=p.heading_style))
        console.print(f"  {_DOCS_CLI}", style=f"dim {p.splash_style}")
        console.print(f"  {_DOCS_USAGE}", style=f"dim {p.splash_style}")
        console.print(f"  {_DOCS_BENCH}", style=f"dim {p.splash_style}")
    elif topic == "interactive":
        console.print(Text("Interactive mode", style=p.heading_style))
        console.print("  mnemolink — open splash menu (TTY only)", style=p.menu_style)
        console.print("  1-7 or command name — run a command", style="dim")
        console.print("  0 / q — exit from any menu level", style="dim")
        console.print("  b — back from a submenu", style="dim")
    console.print()


def cmd_help_submenu(
    console: Console | None = None,
    input_fn: Callable[[str], str] | None = None,
) -> Optional[str]:
    """Interactive help topics. Returns _NAV_EXIT to quit."""
    if console is None:
        console = Console()

    topic_map = {key: target for key, _slug, _summary, target in _HELP_MENU}
    topic_map.update({slug: target for _key, slug, _summary, target in _HELP_MENU})

    while True:
        p = palette()
        console.print(Text("Help", style=p.heading_style))
        for key, slug, summary, _target in _HELP_MENU:
            console.print(f"    [{key}] {slug:<12}— {summary}", style=p.menu_style)
        _print_nav_footer(console, show_back=True)

        raw = _read_line("  help> ", input_fn)
        choice, nav = _parse_nav(raw)
        if nav == _NAV_EXIT:
            return _NAV_EXIT
        if nav == _NAV_BACK:
            return None
        if not choice:
            continue

        target = topic_map.get(choice.lower())
        if target is None:
            console.print(f"  Unknown topic: '{choice}'", style=f"dim {p.error_color}")
            console.print()
            continue

        if isinstance(target, int):
            _print_help_command_group(console, HELP_GROUPS[target])
        else:
            _print_help_static_topic(console, target)

        pause = _read_line("  Press Enter to return to help topics... ", input_fn)
        _, pause_nav = _parse_nav(pause if pause else "")
        if pause_nav == _NAV_EXIT:
            return _NAV_EXIT
        if pause_nav == _NAV_BACK:
            continue
        console.print()


def cmd_theme_picker(
    console: Console | None = None,
    input_fn: Callable[[str], str] | None = None,
    *,
    show_back: bool = True,
) -> Optional[str]:
    """Select an in-session CLI theme. Returns _NAV_EXIT when requested."""
    if console is None:
        console = Console()

    choices = {key: name for key, name, _description in _THEME_CHOICES}
    choices.update({name: name for _key, name, _description in _THEME_CHOICES})

    while True:
        p = palette()
        console.print(Text("Theme", style=p.heading_style))
        console.print(f"  Current: {theme_name()}", style=p.id_style)
        console.print()
        for key, name, description in _THEME_CHOICES:
            console.print(
                f"    [{key}] {name:<8}— {description}",
                style=p.menu_style,
            )
        _print_nav_footer(console, show_back=show_back)

        raw = _read_line("  theme> ", input_fn)
        choice, nav = _parse_nav(raw)
        if nav == _NAV_EXIT:
            return _NAV_EXIT
        if nav == _NAV_BACK:
            return None
        if not choice:
            continue

        selected = choices.get(choice.lower())
        if selected is None or not set_theme(selected):
            console.print(f"  Unknown theme: '{choice}'", style=f"dim {p.error_color}")
            console.print()
            continue

        console.print(f"  Theme set to '{selected}'", style=palette().id_style)
        return None


def cmd_config_interactive(
    console: Console | None = None,
    input_fn: Callable[[str], str] | None = None,
) -> Optional[str]:
    """View and update user configuration, models, and credentials interactively."""
    import os
    from pathlib import Path
    from rich.panel import Panel
    from mnemolink.config import (
        CONFIG_FILE,
        PROVIDER_KEY_URLS,
        USER_ENV_FILE,
        get_credential_status,
        load_config,
        save_config,
        save_user_env_key,
    )
    from mnemolink.wizard import MnemonicWizard

    if console is None:
        console = Console()

    p = palette()
    cfg = load_config()
    cred_status = get_credential_status()

    console.print(
        Panel(
            f"[bold {p.pink}]MnemoLink User Configuration & Credentials[/]",
            border_style=p.blue,
        )
    )
    console.print(f"  [cyan]Config file:[/]    {CONFIG_FILE}")
    console.print(f"  [cyan]Global env:[/]     {USER_ENV_FILE}")
    console.print(f"  [cyan]Active theme:[/]   {cfg.theme}")
    console.print(f"  [cyan]Provider:[/]       {cfg.provider or '(not set)'}")
    console.print(f"  [cyan]Model:[/]          {cfg.model or '(not set)'}")
    console.print(f"  [cyan]Ollama host:[/]    {cfg.ollama_host}")
    console.print(
        f"  [cyan]Catalog roots:[/]  "
        f"{', '.join(cfg.catalog_roots) if cfg.catalog_roots else '(none)'}"
    )
    console.print()
    console.print("  [bold]Credential Precedence Status:[/]")
    for prov, configured in cred_status.items():
        status_text = "[green]Configured[/]" if configured else "[dim]Not Set[/]"
        console.print(f"    - {prov.capitalize():<12}: {status_text}")

    console.print()
    console.print("  [1] Set Preferred Provider & Model", style=p.menu_style)
    console.print("  [2] Configure API Key", style=p.menu_style)
    console.print("  [3] Add Custom Catalog Root Directory", style=p.menu_style)
    console.print("  [4] Set Ollama Host URL", style=p.menu_style)
    _print_nav_footer(console, show_back=True)

    choice_raw = _read_line("  config action [1-4, b]> ", input_fn)
    choice, nav = _parse_nav(choice_raw if choice_raw is not None else "")
    if nav:
        return nav

    if choice == "1":
        wiz = MnemonicWizard(console=console, input_fn=input_fn)
        wiz.setup_ai_model()
    elif choice == "2":
        console.print("\n  [bold]Choose provider to configure API Key:[/]")
        providers = [
            ("1", "gemini", "Google Gemini", "GEMINI_API_KEY"),
            ("2", "anthropic", "Anthropic Claude", "ANTHROPIC_API_KEY"),
            ("3", "mistral", "Mistral AI", "MISTRAL_API_KEY"),
            ("4", "openai", "OpenAI", "OPENAI_API_KEY"),
        ]
        for num, _, label, env_var in providers:
            console.print(f"    [{num}] {label} ({env_var})", style=p.menu_style)
        prov_pick = _read_line("  Select provider (1-4)> ", input_fn) or "1"
        prov_map = {num: (p_name, env_var) for num, p_name, _, env_var in providers}
        if prov_pick in prov_map:
            p_name, env_var = prov_map[prov_pick]
            url = PROVIDER_KEY_URLS.get(p_name, "")
            if url:
                console.print(f"  [dim italic]Get your key at:[/] [cyan]{url}[/]")
            key_val = _read_line(f"  Paste {env_var}> ", input_fn)
            if key_val:
                save_user_env_key(env_var, key_val)
                os.environ[env_var] = key_val
                console.print(f"  [green]Saved {env_var} to ~/.mnemolink/.env[/]")
    elif choice == "3":
        root_dir = _read_line(
            "  Enter directory path to add to catalog roots> ", input_fn
        )
        if root_dir:
            p_root = Path(root_dir).expanduser().resolve()
            p_root.mkdir(parents=True, exist_ok=True)
            if str(p_root) not in cfg.catalog_roots:
                cfg.catalog_roots.append(str(p_root))
                save_config(cfg)
                console.print(f"  [green]Added {p_root} to catalog roots.[/]")
    elif choice == "4":
        host = _read_line(f"  Ollama host URL [default {cfg.ollama_host}]> ", input_fn)
        if host:
            cfg.ollama_host = host.strip()
            save_config(cfg)
            console.print(f"  [green]Saved ollama_host: {cfg.ollama_host}[/]")

    return None


def _safe_run(console: Console, fn, *args) -> None:
    """Run a CLI command without letting SystemExit leave the menu."""
    try:
        fn(*args)
    except SystemExit as exc:
        if exc.code not in (0, None):
            p = palette()
            console.print(
                f"  command exited with status {exc.code}",
                style=f"dim {p.error_color}",
            )


def _prompt_list_args(
    console: Console, input_fn: Callable[[str], str] | None
) -> Tuple[Optional[argparse.Namespace], Optional[str]]:
    console.print("  kind (persona/memory/lineage, Enter for all)", style="dim")
    raw = _read_line("  kind> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    kind = choice.lower() if choice else None
    if kind and kind not in ("persona", "memory", "lineage"):
        console.print(
            f"  Unknown kind: '{choice}'", style=f"dim {palette().error_color}"
        )
        return None, _NAV_BACK

    console.print("  domain (Enter for all)", style="dim")
    raw = _read_line("  domain> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    domain = choice or None
    return argparse.Namespace(kind=kind, domain=domain), None


def _prompt_inspect_args(
    console: Console, input_fn: Callable[[str], str] | None
) -> Tuple[Optional[argparse.Namespace], Optional[str]]:
    console.print("  asset id (persona, memory, or lineage)", style="dim")
    raw = _read_line("  inspect> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None or not choice:
        return None, _NAV_BACK
    return argparse.Namespace(identifier=choice), None


def _prompt_compose_args(
    console: Console, input_fn: Callable[[str], str] | None
) -> Tuple[Optional[argparse.Namespace], Optional[str]]:
    console.print("  persona id (Enter to skip)", style="dim")
    raw = _read_line("  persona> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    persona = choice or None

    console.print("  memories (comma-separated, Enter to skip)", style="dim")
    raw = _read_line("  memories> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    memories = choice or None

    console.print("  lineage id (Enter to skip)", style="dim")
    raw = _read_line("  lineage> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    lineage = choice or None

    console.print(f"  format ({'|'.join(COMPOSE_FORMATS)}, default raw)", style="dim")
    raw = _read_line("  format> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    fmt = (choice or "raw").lower()
    if fmt not in COMPOSE_FORMATS:
        console.print(
            f"  Unknown format: '{choice}'", style=f"dim {palette().error_color}"
        )
        return None, _NAV_BACK

    console.print("  output path (Enter for stdout)", style="dim")
    raw = _read_line("  out> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK

    return (
        argparse.Namespace(
            persona=persona,
            memories=memories,
            lineage=lineage,
            no_lineage=False,
            format=fmt,
            out=choice or None,
        ),
        None,
    )


def _prompt_bench_args(
    console: Console, input_fn: Callable[[str], str] | None
) -> Tuple[Optional[argparse.Namespace], Optional[str]]:
    console.print("  tier (all/micro/meso/macro, default all)", style="dim")
    raw = _read_line("  tier> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    tier = (choice or "all").lower()
    if tier not in ("all", "micro", "meso", "macro"):
        console.print(
            f"  Unknown tier: '{choice}'", style=f"dim {palette().error_color}"
        )
        return None, _NAV_BACK

    console.print("  mock offline? (Y/n)", style="dim")
    raw = _read_line("  mock> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK
    mock_raw = (choice or "y").lower()
    mock = mock_raw not in ("n", "no", "false", "live")

    model = None
    if not mock:
        from mnemolink.config import (
            PROVIDER_MODEL_EXAMPLES,
            PROVIDER_MODEL_URLS,
            list_ollama_local_models,
            load_config,
            resolve_api_key,
        )

        cfg = load_config()
        if cfg.model and cfg.provider:
            console.print(
                f"  Configured model: '{cfg.provider}/{cfg.model}'",
                style="dim",
            )
            raw = _read_line("  Use configured model? (Y/n)> ", input_fn)
            choice, nav = _parse_nav(raw if raw is not None else "")
            if nav == _NAV_EXIT:
                return None, _NAV_EXIT
            if nav == _NAV_BACK or raw is None:
                return None, _NAV_BACK
            if (choice or "y").lower() in ("y", "yes"):
                model = cfg.model
                if cfg.provider != "ollama":
                    resolve_api_key(
                        cfg.provider,
                        interactive=True,
                        console=console,
                        input_fn=input_fn,
                    )
                return (
                    argparse.Namespace(
                        model=model, mock=mock, tier=tier, export_json=None
                    ),
                    None,
                )

        console.print("  Select AI Target (no default):", style="dim")
        console.print(
            "    [1] Cloud Provider API (Google Gemini, Anthropic Claude, Mistral, OpenAI)",
            style="dim",
        )
        console.print("    [2] Local Ollama (offline local daemon)", style="dim")
        raw = _read_line("  target [1-2]> ", input_fn)
        choice, nav = _parse_nav(raw if raw is not None else "")
        if nav == _NAV_EXIT:
            return None, _NAV_EXIT
        if nav == _NAV_BACK or raw is None:
            return None, _NAV_BACK

        if choice == "2" or choice.lower() == "ollama":
            provider = "ollama"
            ollama_url = PROVIDER_MODEL_URLS.get("ollama", "https://ollama.com/library")
            console.print(f"  Browse Ollama library: {ollama_url}", style="dim")
            console.print("  Pull models: 'ollama pull <model>'", style="dim")
            local_models = list_ollama_local_models(cfg.ollama_host)
            if local_models:
                console.print(
                    f"  Installed local models: {', '.join(local_models)}",
                    style="dim",
                )
            raw_m = _read_line("  Ollama model name> ", input_fn)
            choice_m, nav_m = _parse_nav(raw_m if raw_m is not None else "")
            if nav_m == _NAV_EXIT:
                return None, _NAV_EXIT
            if nav_m == _NAV_BACK or raw_m is None:
                return None, _NAV_BACK
            model = choice_m or (local_models[0] if local_models else "llama3.2:1b")
        else:
            console.print("  Select Cloud Provider:", style="dim")
            console.print("    [1] Google Gemini", style="dim")
            console.print("    [2] Anthropic Claude", style="dim")
            console.print("    [3] Mistral AI", style="dim")
            console.print("    [4] OpenAI", style="dim")
            raw_p = _read_line("  provider [1-4]> ", input_fn)
            choice_p, nav_p = _parse_nav(raw_p if raw_p is not None else "")
            if nav_p == _NAV_EXIT:
                return None, _NAV_EXIT
            if nav_p == _NAV_BACK or raw_p is None:
                return None, _NAV_BACK

            prov_map = {
                "1": "gemini",
                "gemini": "gemini",
                "2": "anthropic",
                "claude": "anthropic",
                "anthropic": "anthropic",
                "3": "mistral",
                "mistral": "mistral",
                "4": "openai",
                "openai": "openai",
            }
            provider = prov_map.get(choice_p.lower(), "gemini")

            m_url = PROVIDER_MODEL_URLS.get(provider, "")
            m_ex = PROVIDER_MODEL_EXAMPLES.get(provider, "")
            if m_url:
                console.print(f"  Model catalog: {m_url}", style="dim")
            if m_ex:
                console.print(f"  Examples: {m_ex}", style="dim")

            hint = (
                cfg.model
                if (cfg.model and getattr(cfg, "provider", None) == provider)
                else ""
            )
            prompt_str = (
                f"  {provider.title()} model name [{hint}]> "
                if hint
                else f"  {provider.title()} model name> "
            )
            raw_m = _read_line(prompt_str, input_fn)
            choice_m, nav_m = _parse_nav(raw_m if raw_m is not None else "")
            if nav_m == _NAV_EXIT:
                return None, _NAV_EXIT
            if nav_m == _NAV_BACK or raw_m is None:
                return None, _NAV_BACK
            model = choice_m or hint
            while not model:
                console.print(
                    f"  Please enter a {provider.title()} model name (see {m_url})",
                    style="yellow",
                )
                raw_m = _read_line(f"  {provider.title()} model name> ", input_fn)
                choice_m, nav_m = _parse_nav(raw_m if raw_m is not None else "")
                if nav_m == _NAV_EXIT:
                    return None, _NAV_EXIT
                if nav_m == _NAV_BACK or raw_m is None:
                    return None, _NAV_BACK
                model = choice_m

            resolve_api_key(
                provider,
                interactive=True,
                console=console,
                input_fn=input_fn,
            )

    return (
        argparse.Namespace(model=model, mock=mock, tier=tier, export_json=None),
        None,
    )


def _prompt_new_args(
    console: Console, input_fn: Callable[[str], str] | None
) -> Tuple[Optional[argparse.Namespace], Optional[str]]:
    console.print("  kind (persona/memory/lineage)", style="dim")
    raw = _read_line("  kind> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None or not choice:
        return None, _NAV_BACK
    kind = choice.lower()
    if kind not in ("persona", "memory", "lineage"):
        console.print(
            f"  Unknown kind: '{choice}'", style=f"dim {palette().error_color}"
        )
        return None, _NAV_BACK

    console.print("  name or slug", style="dim")
    raw = _read_line("  name> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None or not choice:
        return None, _NAV_BACK
    name = choice

    console.print("  output directory (Enter for default)", style="dim")
    raw = _read_line("  dir> ", input_fn)
    choice, nav = _parse_nav(raw if raw is not None else "")
    if nav == _NAV_EXIT:
        return None, _NAV_EXIT
    if nav == _NAV_BACK or raw is None:
        return None, _NAV_BACK

    return argparse.Namespace(kind=kind, name=name, dir=choice or None), None


def cmd_interactive(
    console: Console | None = None,
    input_fn: Callable[[str], str] | None = None,
) -> None:
    """Launch ASCII splash screen and interactive menu."""
    from mnemolink.cli import cmd_bench, cmd_compose, cmd_inspect, cmd_list, cmd_new

    if console is None:
        console = Console()
    if input_fn is None:
        input_fn = builtins.input

    print_splash(console)

    commands = {
        "1": "list",
        "list": "list",
        "2": "inspect",
        "inspect": "inspect",
        "3": "compose",
        "compose": "compose",
        "4": "bench",
        "bench": "bench",
        "5": "author",
        "author": "author",
        "authoring": "author",
        "wizard": "author",
        "w": "author",
        "new": "author",
        "6": "help",
        "help": "help",
        "7": "theme",
        "theme": "theme",
        "8": "config",
        "config": "config",
        "cfg": "config",
        "settings": "config",
    }

    _print_menu(console)

    while True:
        raw = _read_line("  > ", input_fn)
        if raw is None:
            console.print("\n  Bye.", style="dim")
            return
        choice, nav = _parse_nav(raw)
        if nav == _NAV_EXIT:
            console.print("  Bye.", style="dim")
            return
        if nav == _NAV_BACK:
            continue
        if not choice:
            continue

        command = commands.get(choice.lower())
        p = palette()

        if command == "list":
            args, extra = _prompt_list_args(console, input_fn)
            if extra == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
            if extra != _NAV_BACK and args is not None:
                _safe_run(console, cmd_list, args)
        elif command == "inspect":
            args, extra = _prompt_inspect_args(console, input_fn)
            if extra == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
            if extra != _NAV_BACK and args is not None:
                _safe_run(console, cmd_inspect, args)
        elif command == "compose":
            args, extra = _prompt_compose_args(console, input_fn)
            if extra == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
            if extra != _NAV_BACK and args is not None:
                _safe_run(console, cmd_compose, args)
        elif command == "bench":
            args, extra = _prompt_bench_args(console, input_fn)
            if extra == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
            if extra != _NAV_BACK and args is not None:
                _safe_run(console, cmd_bench, args)
        elif command == "author":
            console.print(
                "  [1] Interactive Mnemonic Wizard (Guided tooltips + AI generation)",
                style=p.menu_style,
            )
            console.print(
                "  [2] Fast Template Scaffolder (raw YAML templates)",
                style=p.menu_style,
            )
            raw_hub = _read_line("  choice [1-2, default 1]> ", input_fn)
            choice_hub, nav_hub = _parse_nav(raw_hub if raw_hub is not None else "")
            if nav_hub == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
            if nav_hub != _NAV_BACK:
                if (choice_hub or "1") == "1":
                    from mnemolink.wizard import MnemonicWizard

                    _safe_run(
                        console,
                        lambda _: MnemonicWizard(
                            console=console, input_fn=input_fn
                        ).run(),
                        None,
                    )
                else:
                    args, extra = _prompt_new_args(console, input_fn)
                    if extra == _NAV_EXIT:
                        console.print("  Bye.", style="dim")
                        return
                    if extra != _NAV_BACK and args is not None:
                        _safe_run(console, cmd_new, args)
        elif command == "help":
            help_nav = cmd_help_submenu(console=console, input_fn=input_fn)
            if help_nav == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
        elif command == "theme":
            theme_nav = cmd_theme_picker(console=console, input_fn=input_fn)
            if theme_nav == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
        elif command == "config":
            cfg_nav = cmd_config_interactive(console=console, input_fn=input_fn)
            if cfg_nav == _NAV_EXIT:
                console.print("  Bye.", style="dim")
                return
        else:
            console.print(
                f"  Unknown command: '{choice}'", style=f"dim {p.error_color}"
            )

        console.print()
        _print_menu(console)

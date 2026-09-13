"""Unit tests for MnemoLink CLI commands and interactive menu."""

import sys
from io import StringIO
from unittest.mock import MagicMock, patch
import pytest
from rich.console import Console

from mnemolink.cli import (
    _NAV_BACK,
    _NAV_EXIT,
    _SPLASH_LOGO_LINES,
    THEMES,
    _apply_theme,
    _gradient_splash_text,
    _gradient_text_line,
    _hex_to_rgb,
    _lerp_rgb,
    _parse_nav,
    _read_line,
    _rgb_to_hex,
    _splash_gradient_color,
    cmd_bench,
    cmd_compose,
    cmd_inspect,
    cmd_interactive,
    cmd_list,
    cmd_new,
    main,
    print_banner,
)


def test_cli_list(capsys):
    args = MagicMock()
    args.kind = None
    args.domain = None
    cmd_list(args)
    captured = capsys.readouterr()
    assert "MnemoLink Registry Catalog" in captured.out
    assert "juris_philosopher" in captured.out


def test_cli_inspect(capsys):
    args = MagicMock()
    args.identifier = "juris_philosopher"
    cmd_inspect(args)
    captured = capsys.readouterr()
    assert "Jurisprudence Philosopher" in captured.out
    assert "Core Philosophy" in captured.out


def test_cli_compose(capsys):
    args = MagicMock()
    args.persona = "juris_philosopher"
    args.memories = "legal/clause_ambiguity_scar"
    args.lineage = None
    args.no_lineage = False
    args.format = "raw"
    args.out = None
    cmd_compose(args)
    captured = capsys.readouterr()
    assert "MNEMONIC MATRIX PROTOCOL" in captured.out


def test_cli_new(tmp_path):
    target_dir = tmp_path / "custom_persona"
    args = MagicMock()
    args.kind = "persona"
    args.name = "custom_scaffold"
    args.dir = str(target_dir)
    cmd_new(args)

    assert (target_dir / "persona.yaml").is_file()
    assert (target_dir / "card.json").is_file()


def test_lerp_rgb_and_gradient_colors():
    _apply_theme("pastel")
    assert _hex_to_rgb("#efcefa") == (239, 206, 250)
    assert _rgb_to_hex((239, 206, 250)) == "#efcefa"

    start = (10, 20, 30)
    end = (110, 120, 130)
    assert _lerp_rgb(start, end, 0.0) == (10, 20, 30)
    assert _lerp_rgb(start, end, 0.5) == (60, 70, 80)
    assert _lerp_rgb(start, end, 1.0) == (110, 120, 130)

    # Gradient boundary checks
    assert _splash_gradient_color(0, 1) == THEMES["pastel"]["gradient_start"]
    assert _splash_gradient_color(0, 10) == THEMES["pastel"]["gradient_start"]
    assert _splash_gradient_color(9, 10) == THEMES["pastel"]["gradient_end"]

    # Mid point check
    mid_color = _splash_gradient_color(5, 11)
    assert mid_color == THEMES["pastel"]["gradient_mid"]


def test_gradient_splash_rendering():
    text_line = _gradient_text_line("TEST LINE", 20)
    assert len(text_line.plain) == 9

    splash_text = _gradient_splash_text(_SPLASH_LOGO_LINES)
    assert "███" in splash_text.plain
    assert len(splash_text.plain.strip().splitlines()) == len(_SPLASH_LOGO_LINES)


def test_parse_nav():
    assert _parse_nav(None) == (None, _NAV_EXIT)
    assert _parse_nav("") == ("", None)
    assert _parse_nav("   ") == ("", None)

    for exit_cmd in ("0", "q", "quit", "exit", "Q"):
        assert _parse_nav(exit_cmd) == (None, _NAV_EXIT)

    for back_cmd in ("b", "back", "esc", "escape", "B"):
        assert _parse_nav(back_cmd) == (None, _NAV_BACK)

    choice, nav = _parse_nav("1")
    assert choice == "1"
    assert nav is None

    choice, nav = _parse_nav("inspect")
    assert choice == "inspect"
    assert nav is None


def test_read_line_exceptions():
    def raise_kb(_prompt):
        raise KeyboardInterrupt()

    assert _read_line("prompt", input_fn=raise_kb) is None

    def raise_eof(_prompt):
        raise EOFError()

    assert _read_line("prompt", input_fn=raise_eof) is None

    def normal_input(_prompt):
        return "  hello world  "

    assert _read_line("prompt", input_fn=normal_input) == "hello world"


def test_theme_switching():
    _apply_theme("ocean")
    assert _splash_gradient_color(0, 10) == THEMES["ocean"]["gradient_start"]

    _apply_theme("mono")
    assert _splash_gradient_color(0, 10) == THEMES["mono"]["gradient_start"]

    # Invalid theme falls back safely to pastel
    _apply_theme("invalid_theme")
    assert _splash_gradient_color(0, 10) == THEMES["pastel"]["gradient_start"]


def test_interactive_menu_exit():
    out_buf = StringIO()
    test_console = Console(file=out_buf, force_terminal=False)

    inputs = iter(["0"])
    cmd_interactive(target_console=test_console, input_fn=lambda _p: next(inputs))

    output = out_buf.getvalue()
    assert "MnemoLink v" in output
    assert "Bye." in output


def test_interactive_menu_list_and_exit():
    out_buf = StringIO()
    test_console = Console(file=out_buf, force_terminal=False)

    # 1: list -> filter kind 'persona' -> filter domain '' -> 0: exit
    inputs = iter(["1", "persona", "", "0"])
    cmd_interactive(target_console=test_console, input_fn=lambda _p: next(inputs))

    output = out_buf.getvalue()
    assert "MnemoLink Registry Catalog" in output
    assert "juris_philosopher" in output
    assert "Bye." in output


def test_interactive_menu_inspect():
    out_buf = StringIO()
    test_console = Console(file=out_buf, force_terminal=False)

    # 2: inspect -> ident 'juris_philosopher' -> 0: exit
    inputs = iter(["2", "juris_philosopher", "0"])
    cmd_interactive(target_console=test_console, input_fn=lambda _p: next(inputs))

    output = out_buf.getvalue()
    assert "MnemoLink Inspection: Persona" in output
    assert "Jurisprudence Philosopher" in output
    assert "Inviolable Axioms" in output


def test_interactive_menu_compose():
    out_buf = StringIO()
    test_console = Console(file=out_buf, force_terminal=False)

    # 3: compose -> persona 'juris_philosopher' -> memories '' -> format 'raw' -> out '' -> 0: exit
    inputs = iter(["3", "juris_philosopher", "", "raw", "", "0"])
    cmd_interactive(target_console=test_console, input_fn=lambda _p: next(inputs))

    output = out_buf.getvalue()
    assert "Compose Mnemonic Context" in output
    assert "Bye." in output


def test_interactive_menu_bench():
    out_buf = StringIO()
    test_console = Console(file=out_buf, force_terminal=False)

    # 4: bench -> mode 1 (mock) -> tier micro -> export '' -> 0: exit
    inputs = iter(["4", "1", "micro", "", "0"])
    cmd_interactive(target_console=test_console, input_fn=lambda _p: next(inputs))

    output = out_buf.getvalue()
    assert "Benchmark Crucible Runner" in output
    assert "Bye." in output


def test_interactive_menu_help_drilldown():
    out_buf = StringIO()
    test_console = Console(file=out_buf, force_terminal=False)

    # 6: help -> 1 (overview) -> 2 (cli) -> 3 (adapters) -> 4 (docs) -> b (back) -> 0: exit
    inputs = iter(["6", "1", "2", "3", "4", "b", "0"])
    cmd_interactive(target_console=test_console, input_fn=lambda _p: next(inputs))

    output = out_buf.getvalue()
    assert "MnemoLink Architecture Overview" in output
    assert "CLI Commands Reference" in output
    assert "Universal Host Adapters" in output
    assert "GitHub Repository" in output
    assert "Bye." in output


def test_interactive_menu_theme_switch():
    out_buf = StringIO()
    test_console = Console(file=out_buf, force_terminal=False)

    # 7: theme -> 2 (ocean) -> 0: exit
    inputs = iter(["7", "2", "0"])
    cmd_interactive(target_console=test_console, input_fn=lambda _p: next(inputs))

    output = out_buf.getvalue()
    assert "Theme switched to:" in output
    assert "ocean" in output
    assert "Bye." in output


def test_main_bare_tty_detection_non_interactive():
    # When sys.stdout.isatty() is False, bare invocation prints usage and exits 0
    with patch.object(sys, "argv", ["mnemolink"]):
        with patch("sys.stdout.isatty", return_value=False):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0


def test_main_bare_tty_detection_interactive():
    # When sys.stdout.isatty() is True, bare invocation launches cmd_interactive and exits 0
    with patch.object(sys, "argv", ["mnemolink"]):
        with patch("sys.stdout.isatty", return_value=True):
            with patch("mnemolink.cli.cmd_interactive") as mock_inter:
                with pytest.raises(SystemExit) as exc_info:
                    main()
                assert exc_info.value.code == 0
                mock_inter.assert_called_once()

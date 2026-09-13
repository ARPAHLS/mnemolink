"""Unit tests for MnemoLink CLI commands and interactive menu."""

import io
import sys
from unittest.mock import MagicMock

import pytest
from rich.console import Console

from mnemolink import __version__
from mnemolink.cli import cmd_compose, cmd_inspect, cmd_list, cmd_new, main
from mnemolink.cli_interactive import (
    _NAV_BACK,
    _NAV_EXIT,
    _SPLASH_LOGO_LINES,
    _lerp_rgb,
    _parse_nav,
    _splash_gradient_color,
    cmd_interactive,
    print_splash,
)
from mnemolink.cli_theme import set_theme, theme_name


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


def test_splash_logo_is_six_lines():
    assert len(_SPLASH_LOGO_LINES) == 6
    assert all("█" in line or "╚" in line for line in _SPLASH_LOGO_LINES)


def test_lerp_and_splash_gradient():
    assert _lerp_rgb((0, 0, 0), (10, 0, 0), 0.5) == (5, 0, 0)
    set_theme("pastel")
    assert _splash_gradient_color(0, 10) == "#efcefa"
    assert _splash_gradient_color(9, 10) == "#bbf7d0"


def test_parse_nav_exit_and_back():
    assert _parse_nav("0") == (None, _NAV_EXIT)
    assert _parse_nav("q") == (None, _NAV_EXIT)
    assert _parse_nav("quit") == (None, _NAV_EXIT)
    assert _parse_nav("b") == (None, _NAV_BACK)
    assert _parse_nav("back") == (None, _NAV_BACK)
    assert _parse_nav("list") == ("list", None)
    assert _parse_nav(None) == (None, _NAV_BACK)
    assert _parse_nav("") == ("", None)


def test_print_splash_subtitle():
    buf = io.StringIO()
    print_splash(Console(file=buf, force_terminal=False, width=120))
    out = buf.getvalue()
    assert f"MnemoLink v{__version__}" in out
    assert "Mnemonic Products Framework for Information Processors" in out


def test_cmd_interactive_exits_on_q():
    buf = io.StringIO()
    cmd_interactive(
        console=Console(file=buf, force_terminal=False, width=120),
        input_fn=lambda _: "q",
    )
    assert "Bye." in buf.getvalue()
    assert "list" in buf.getvalue()


def test_cmd_interactive_ctrl_c_prints_bye():
    buf = io.StringIO()

    def boom(_prompt):
        raise KeyboardInterrupt

    cmd_interactive(
        console=Console(file=buf, force_terminal=False, width=120),
        input_fn=boom,
    )
    assert "Bye." in buf.getvalue()


def test_cmd_interactive_unknown_command():
    responses = iter(["unknown_cmd", "q"])
    buf = io.StringIO()
    cmd_interactive(
        console=Console(file=buf, force_terminal=False, width=120),
        input_fn=lambda _: next(responses),
    )
    assert "Unknown command" in buf.getvalue()


def test_cmd_interactive_list_dispatch(capsys):
    responses = iter(["1", "", "", "q"])
    buf = io.StringIO()
    cmd_interactive(
        console=Console(file=buf, force_terminal=False, width=120),
        input_fn=lambda _: next(responses),
    )
    captured = capsys.readouterr()
    assert "MnemoLink Registry Catalog" in captured.out
    assert "Bye." in buf.getvalue()


def test_cmd_interactive_inspect_prompt(capsys):
    responses = iter(["2", "juris_philosopher", "q"])
    buf = io.StringIO()
    cmd_interactive(
        console=Console(file=buf, force_terminal=False, width=120),
        input_fn=lambda _: next(responses),
    )
    captured = capsys.readouterr()
    assert "Jurisprudence Philosopher" in captured.out
    assert "Core Philosophy" in captured.out


def test_cmd_interactive_help_and_back():
    responses = iter(["6", "1", "", "b", "q"])
    buf = io.StringIO()
    cmd_interactive(
        console=Console(file=buf, force_terminal=False, width=120),
        input_fn=lambda _: next(responses),
    )
    out = buf.getvalue()
    assert "Help" in out
    assert "mnemolink list" in out
    assert "Bye." in out


def test_cmd_interactive_theme_switch():
    set_theme("pastel")
    responses = iter(["7", "2", "q"])
    buf = io.StringIO()
    cmd_interactive(
        console=Console(file=buf, force_terminal=False, width=120),
        input_fn=lambda _: next(responses),
    )
    assert theme_name() == "ocean"
    assert "Theme set to 'ocean'" in buf.getvalue()
    set_theme("pastel")


def test_main_non_tty_prints_help(monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["mnemolink"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: False)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    out = capsys.readouterr().out
    assert "usage:" in out.lower()
    assert "{list,inspect,compose,new,bench}" in out


def test_main_tty_launches_interactive(monkeypatch):
    called = []
    monkeypatch.setattr(sys, "argv", ["mnemolink"])
    monkeypatch.setattr(sys.stdout, "isatty", lambda: True)
    monkeypatch.setattr("mnemolink.cli.cmd_interactive", lambda: called.append(True))
    main()
    assert called == [True]

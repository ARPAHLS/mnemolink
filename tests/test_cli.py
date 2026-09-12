"""Unit tests for MnemoLink CLI commands."""

from unittest.mock import MagicMock
from mnemolink.cli import cmd_list, cmd_inspect, cmd_compose, cmd_new


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

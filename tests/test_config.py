"""Unit tests for MnemoLink persistent configuration and credential resolution.

All tests operate offline without real network calls or reliance on external files.
"""

import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

from mnemolink.config import (
    MnemoLinkConfig,
    list_ollama_local_models,
    load_config,
    resolve_api_key,
    save_config,
    save_user_env_key,
)


def test_config_defaults():
    cfg = MnemoLinkConfig()
    assert cfg.theme == "pastel"
    assert cfg.catalog_roots == []
    assert cfg.model is None
    assert cfg.provider is None
    assert cfg.ollama_host == "http://localhost:11434"
    assert cfg.defaults == {}


def test_config_serialization():
    cfg = MnemoLinkConfig(
        theme="ocean",
        catalog_roots=["/tmp/custom"],
        model="gemini-3.5-flash",
        provider="gemini",
        ollama_host="http://127.0.0.1:11434",
        defaults={"verbose": True},
    )
    d = cfg.to_dict()
    assert d["theme"] == "ocean"
    assert d["model"] == "gemini-3.5-flash"
    assert d["provider"] == "gemini"

    reloaded = MnemoLinkConfig.from_dict(d)
    assert reloaded.theme == "ocean"
    assert reloaded.catalog_roots == ["/tmp/custom"]
    assert reloaded.model == "gemini-3.5-flash"
    assert reloaded.defaults == {"verbose": True}


def test_config_load_and_save(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr("mnemolink.config.CONFIG_FILE", cfg_file)
    monkeypatch.setattr("mnemolink.config.CONFIG_DIR", tmp_path)

    # Initial load when file does not exist
    initial = load_config()
    assert initial.theme == "pastel"
    assert initial.model is None

    # Modify and save
    initial.theme = "mono"
    initial.model = "gemini-3.5-flash"
    initial.provider = "gemini"
    initial.catalog_roots = [str(tmp_path / "custom_catalog")]
    save_config(initial)

    assert cfg_file.is_file()

    # Reload and verify
    reloaded = load_config()
    assert reloaded.theme == "mono"
    assert reloaded.model == "gemini-3.5-flash"
    assert reloaded.provider == "gemini"
    assert reloaded.catalog_roots == [str(tmp_path / "custom_catalog")]


def test_config_load_corrupt_falls_back(tmp_path, monkeypatch):
    cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr("mnemolink.config.CONFIG_FILE", cfg_file)
    cfg_file.write_text("not: valid: yaml: [", encoding="utf-8")

    cfg = load_config()
    assert cfg.theme == "pastel"
    assert cfg.model is None


def test_resolve_api_key_process_env(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test_gemini_env_key_123")
    key = resolve_api_key("gemini")
    assert key == "test_gemini_env_key_123"


def test_resolve_api_key_workspace_env(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    ws_dir = tmp_path / "ws"
    ws_dir.mkdir()
    (ws_dir / ".env").write_text(
        "GEMINI_API_KEY=from_workspace_env_888\n", encoding="utf-8"
    )

    key = resolve_api_key("gemini", workspace_dir=ws_dir)
    assert key == "from_workspace_env_888"


def test_resolve_api_key_user_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    empty_ws = tmp_path / "empty_ws"
    empty_ws.mkdir()

    user_dir = tmp_path / "user_home"
    user_dir.mkdir()
    user_env = user_dir / ".env"
    user_env.write_text("GEMINI_API_KEY=from_user_env_file_999\n", encoding="utf-8")
    monkeypatch.setattr("mnemolink.config.USER_ENV_FILE", user_env)

    key = resolve_api_key("gemini", workspace_dir=empty_ws)
    assert key == "from_user_env_file_999"


def test_resolve_api_key_interactive_prompt(tmp_path, monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    empty_ws = tmp_path / "empty_ws"
    empty_ws.mkdir()

    user_dir = tmp_path / "user_home"
    user_dir.mkdir()
    user_env = user_dir / ".env"
    monkeypatch.setattr("mnemolink.config.USER_ENV_FILE", user_env)
    monkeypatch.setattr("mnemolink.config.CONFIG_DIR", user_dir)

    key = resolve_api_key(
        "gemini",
        workspace_dir=empty_ws,
        interactive=True,
        input_fn=lambda _: "interactive_entered_key_abc",
    )
    assert key == "interactive_entered_key_abc"
    assert user_env.is_file()
    content = user_env.read_text(encoding="utf-8")
    assert "GEMINI_API_KEY=interactive_entered_key_abc" in content


def test_save_user_env_key_update_existing(tmp_path, monkeypatch):
    user_env = tmp_path / ".env"
    user_env.write_text("EXISTING_KEY=old_val\nOTHER=123\n", encoding="utf-8")
    monkeypatch.setattr("mnemolink.config.USER_ENV_FILE", user_env)
    monkeypatch.setattr("mnemolink.config.CONFIG_DIR", tmp_path)

    save_user_env_key("EXISTING_KEY", "new_val")
    content = user_env.read_text(encoding="utf-8")
    assert "EXISTING_KEY=new_val" in content
    assert "OTHER=123" in content


def test_list_ollama_local_models_success():
    fake_response = io.BytesIO(
        json.dumps(
            {
                "models": [
                    {"name": "llama3.2:1b"},
                    {"name": "mistral:latest"},
                    {"name": "qwen2.5:7b"},
                ]
            }
        ).encode("utf-8")
    )
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = fake_response
    mock_ctx.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=mock_ctx):
        models = list_ollama_local_models("http://localhost:11434")
        assert models == ["llama3.2:1b", "mistral:latest", "qwen2.5:7b"]


def test_list_ollama_local_models_offline_returns_empty():
    with patch(
        "urllib.request.urlopen",
        side_effect=urllib.error.URLError("Connection refused"),
    ):
        models = list_ollama_local_models("http://localhost:11434")
        assert models == []


def test_get_credential_status(monkeypatch):
    from mnemolink.config import get_credential_status

    monkeypatch.setenv("GEMINI_API_KEY", "key123")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    status = get_credential_status()
    assert status.get("gemini") is True


def test_set_config_value(tmp_path, monkeypatch):
    from mnemolink import config
    from mnemolink.config import set_config_value

    cfg_file = tmp_path / "config.yaml"
    monkeypatch.setattr(config, "CONFIG_FILE", cfg_file)
    monkeypatch.setattr(config, "CONFIG_DIR", tmp_path)

    set_config_value("theme", "ocean")
    set_config_value("model", "gemini-3.5-flash")
    set_config_value("catalog_root", "/custom/dir")

    loaded = config.load_config()
    assert loaded.theme == "ocean"
    assert loaded.model == "gemini-3.5-flash"
    assert "/custom/dir" in loaded.catalog_roots

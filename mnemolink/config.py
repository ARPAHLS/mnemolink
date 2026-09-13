"""Persistent user configuration and API credential management for MnemoLink.

Mirrors Skillware / AURA configuration architecture:
- Config file: ~/.mnemolink/config.yaml
- Global credentials: ~/.mnemolink/.env
- 3-layer credential resolution: Workspace .env -> ~/.mnemolink/.env -> Env vars -> Prompt
- Zero background daemons, 100% standard library + PyYAML.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import yaml
from dotenv import load_dotenv

CONFIG_DIR = Path.home() / ".mnemolink"
CONFIG_FILE = CONFIG_DIR / "config.yaml"
USER_ENV_FILE = CONFIG_DIR / ".env"

PROVIDER_ENV_KEYS: Dict[str, str] = {
    "gemini": "GEMINI_API_KEY",
    "google": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "claude": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "groq": "GROQ_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}

PROVIDER_KEY_URLS: Dict[str, str] = {
    "gemini": "https://aistudio.google.com/app/apikey",
    "google": "https://aistudio.google.com/app/apikey",
    "anthropic": "https://console.anthropic.com/settings/keys",
    "claude": "https://console.anthropic.com/settings/keys",
    "mistral": "https://console.mistral.ai/api-keys/",
    "openai": "https://platform.openai.com/api-keys",
    "groq": "https://console.groq.com/keys",
    "deepseek": "https://platform.deepseek.com/api_keys",
}

PROVIDER_MODEL_URLS: Dict[str, str] = {
    "gemini": "https://ai.google.dev/gemini-api/docs/models/gemini",
    "google": "https://ai.google.dev/gemini-api/docs/models/gemini",
    "anthropic": "https://docs.anthropic.com/en/docs/about-claude/models",
    "claude": "https://docs.anthropic.com/en/docs/about-claude/models",
    "mistral": "https://docs.mistral.ai/getting-started/models/",
    "openai": "https://platform.openai.com/docs/models",
    "ollama": "https://ollama.com/library",
}

PROVIDER_MODEL_EXAMPLES: Dict[str, str] = {
    "gemini": "gemini-3.5-flash, gemini-2.5-flash, gemini-2.5-pro",
    "google": "gemini-3.5-flash, gemini-2.5-flash, gemini-2.5-pro",
    "anthropic": "claude-sonnet-5, claude-opus-5, claude-haiku-4.5",
    "claude": "claude-sonnet-5, claude-opus-5, claude-haiku-4.5",
    "mistral": "ministral-8b-latest, mistral-large-latest",
    "openai": "gpt-5.6-luna, gpt-4o, o3-mini",
    "ollama": "llama3.2:1b, mistral:latest, qwen2.5:7b",
}


@dataclass
class MnemoLinkConfig:
    """Global user settings and preferences."""

    theme: str = "pastel"
    catalog_roots: List[str] = field(default_factory=list)
    model: Optional[str] = None
    provider: Optional[str] = None
    ollama_host: str = "http://localhost:11434"
    defaults: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> MnemoLinkConfig:
        return cls(
            theme=data.get("theme", "pastel"),
            catalog_roots=data.get("catalog_roots", []),
            model=data.get("model"),
            provider=data.get("provider"),
            ollama_host=data.get("ollama_host", "http://localhost:11434"),
            defaults=data.get("defaults", {}),
        )


def get_config_dir() -> Path:
    """Return the base configuration directory (~/.mnemolink)."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def get_config_file() -> Path:
    """Return path to config.yaml."""
    return CONFIG_FILE


def load_config() -> MnemoLinkConfig:
    """Load configuration from ~/.mnemolink/config.yaml or return defaults."""
    if not CONFIG_FILE.is_file():
        return MnemoLinkConfig()

    try:
        raw = CONFIG_FILE.read_text(encoding="utf-8")
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            return MnemoLinkConfig.from_dict(data)
    except Exception:
        pass
    return MnemoLinkConfig()


def save_config(config: MnemoLinkConfig) -> None:
    """Persist configuration to ~/.mnemolink/config.yaml."""
    get_config_dir()
    data = config.to_dict()
    CONFIG_FILE.write_text(yaml.dump(data, sort_keys=False), encoding="utf-8")


def resolve_api_key(
    provider: str,
    *,
    workspace_dir: Optional[Path] = None,
    interactive: bool = False,
    input_fn: Optional[Callable[[str], str]] = None,
    console: Any = None,
) -> Optional[str]:
    """Resolve API key using 3-layer precedence:

    1. Current workspace .env (loaded via python-dotenv)
    2. Global user .env (~/.mnemolink/.env)
    3. Process environment variables
    4. Optional interactive prompt (saved to ~/.mnemolink/.env for future runs)
    """
    key_name = PROVIDER_ENV_KEYS.get(
        provider.lower().strip(), f"{provider.upper()}_API_KEY"
    )

    # 1. Local workspace .env
    ws = workspace_dir or Path.cwd()
    ws_env = ws / ".env"
    if ws_env.is_file():
        load_dotenv(dotenv_path=ws_env, override=False)
        val = os.getenv(key_name)
        if val and val.strip():
            return val.strip()

    # 2. Global user ~/.mnemolink/.env
    if USER_ENV_FILE.is_file():
        load_dotenv(dotenv_path=USER_ENV_FILE, override=False)
        val = os.getenv(key_name)
        if val and val.strip():
            return val.strip()

    # 3. Process environment
    val = os.environ.get(key_name)
    if val and val.strip():
        return val.strip()

    # 4. Optional interactive prompt
    if interactive:
        key_url = PROVIDER_KEY_URLS.get(provider.lower().strip())
        if console:
            console.print(f"\n  [bold]API Key Configuration for {provider.title()}:[/]")
            if key_url:
                console.print(
                    f"  [dim italic]Manage/obtain your API key at:[/] [cyan]{key_url}[/]"
                )
            console.print(
                f"  [dim]Keys are saved to {USER_ENV_FILE} and persist across all sessions.[/]"
            )

        prompt_str = (
            f"  Enter {key_name} (saved to ~/.mnemolink/.env, or Enter to skip): "
        )
        entered = ""
        if input_fn is not None:
            try:
                entered = input_fn(prompt_str).strip()
            except (KeyboardInterrupt, EOFError):
                entered = ""
        else:
            try:
                entered = input(prompt_str).strip()
            except (KeyboardInterrupt, EOFError):
                entered = ""

        if entered:
            save_user_env_key(key_name, entered)
            os.environ[key_name] = entered
            if console:
                console.print(
                    f"  [green]Saved {key_name} to ~/.mnemolink/.env "
                    "(persisting across sessions).[/]"
                )
            return entered

    return None


def save_user_env_key(key: str, value: str) -> None:
    """Persist an API key securely into ~/.mnemolink/.env."""
    get_config_dir()
    lines: List[str] = []
    if USER_ENV_FILE.is_file():
        try:
            lines = USER_ENV_FILE.read_text(encoding="utf-8").splitlines()
        except Exception:
            lines = []

    updated = False
    new_lines: List[str] = []
    for line in lines:
        if line.strip().startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            updated = True
        else:
            new_lines.append(line)

    if not updated:
        new_lines.append(f"{key}={value}")

    USER_ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")


def list_ollama_local_models(
    host: str = "http://localhost:11434", timeout: float = 2.0
) -> List[str]:
    """Query local Ollama instance for installed models."""
    clean_host = host.rstrip("/")
    if not clean_host.startswith("http://") and not clean_host.startswith("https://"):
        clean_host = f"http://{clean_host}"
    if "0.0.0.0" in clean_host:
        clean_host = clean_host.replace("0.0.0.0", "127.0.0.1")

    url = f"{clean_host}/api/tags"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "MnemoLink-Client"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            models = [m.get("name") for m in data.get("models", []) if m.get("name")]
            return sorted(models)
    except Exception:
        return []


def get_credential_status() -> Dict[str, bool]:
    """Check whether credentials exist across workspace .env, ~/.mnemolink/.env, or env."""
    status: Dict[str, bool] = {}
    for prov in ("gemini", "anthropic", "mistral", "openai", "groq", "deepseek"):
        key = resolve_api_key(prov, interactive=False)
        status[prov] = bool(key)
    return status


def set_config_value(key: str, value: Any) -> MnemoLinkConfig:
    """Update a specific configuration setting and persist to config.yaml."""
    cfg = load_config()
    key_norm = key.lower().strip()
    if key_norm == "theme":
        cfg.theme = str(value).strip()
    elif key_norm in ("model", "preferred_model"):
        cfg.model = str(value).strip() if value else None
    elif key_norm in ("provider", "preferred_provider"):
        cfg.provider = str(value).strip() if value else None
    elif key_norm == "ollama_host":
        cfg.ollama_host = str(value).strip()
    elif key_norm in ("catalog_roots", "catalog_dirs", "catalog_root"):
        if isinstance(value, list):
            cfg.catalog_roots = [str(v).strip() for v in value]
        else:
            val_str = str(value).strip()
            if val_str and val_str not in cfg.catalog_roots:
                cfg.catalog_roots.append(val_str)
    else:
        cfg.defaults[key] = value
    save_config(cfg)
    return cfg

"""Interactive Mnemonic Wizard for authoring Personas, Memories, and Lineages.

Provides two authoring tracks:
1. Guided Manual Track: Step-by-step interactive prompts with rich tooltips,
   field-level guidance, and strict Pydantic validation.
2. AI-Assisted Track: Conversational elicitation powered by modern LLMs (Google Gemini 3.5 Flash,
   local Ollama, Anthropic Claude, Mistral, OpenAI) generating verified schema assets.
"""

from __future__ import annotations

import argparse
import builtins
import json
import os
import random
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union
import yaml

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from mnemolink.cli_theme import palette
from mnemolink.config import (
    PROVIDER_MODEL_EXAMPLES,
    PROVIDER_MODEL_URLS,
    list_ollama_local_models,
    load_config,
    resolve_api_key,
    save_config,
)
from mnemolink.discovery import MnemonicResolver
from mnemolink.lineage import LineageBuilder
from mnemolink.models import (
    CatalogCard,
    LineageProduct,
    MemoryProduct,
    PersonaProduct,
)
from mnemolink.wizard_prompts import (
    get_lineage_system_instruction,
    get_memory_system_instruction,
    get_persona_system_instruction,
)


def _kind_dir_name(kind: str) -> str:
    """Return canonical catalog directory plural name for a product kind."""
    k = kind.lower().strip()
    if k == "memory":
        return "memories"
    if k == "persona":
        return "personas"
    if k == "lineage":
        return "lineages"
    return f"{k}s"


def _calculate_backoff(attempt: int, headers: Any = None) -> float:
    """Calculate exponential backoff delay with jitter, respecting Retry-After."""
    if headers:
        try:
            retry_after = headers.get("Retry-After")
            if retry_after:
                return max(1.0, float(retry_after) + 0.5)
        except Exception:
            pass
    # Jittered exponential backoff: 3s, 6s, 12s, 24s... + jitter
    base = (2**attempt) * 3
    jitter = random.uniform(0.5, 2.0)
    return min(60.0, base + jitter)


def _clean_json_response(raw: str) -> str:
    """Extract clean JSON from model output, stripping markdown code fences."""
    text = raw.strip()
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if match:
        return match.group(1).strip()
    # Try finding first { and last }
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace : last_brace + 1].strip()
    return text


def query_llm_for_json(
    prompt: str,
    system_instruction: str,
    provider: str,
    model: str,
    api_key: Optional[str] = None,
    ollama_host: str = "http://localhost:11434",
    timeout: int = 60,
    max_retries: int = 2,
    max_output_tokens: int = 8192,
    console: Optional[Console] = None,
) -> Optional[Dict[str, Any]]:
    """Query an LLM and return parsed JSON with self-healing retry on syntax error."""
    provider_norm = provider.lower().strip()

    for attempt in range(max_retries + 1):
        raw_text: Optional[str] = None
        try:
            if provider_norm in ("gemini", "google"):
                raw_text = _query_gemini(
                    system_instruction,
                    prompt,
                    model,
                    api_key=api_key,
                    timeout=timeout,
                    max_output_tokens=max_output_tokens,
                )
            elif provider_norm == "ollama":
                raw_text = _query_ollama(
                    system_instruction,
                    prompt,
                    model,
                    host=ollama_host,
                    timeout=timeout,
                    max_output_tokens=max_output_tokens,
                )
            elif provider_norm in ("anthropic", "claude"):
                raw_text = _query_anthropic(
                    system_instruction,
                    prompt,
                    model,
                    api_key=api_key,
                    timeout=timeout,
                    max_output_tokens=max_output_tokens,
                )
            elif provider_norm in ("mistral",):
                raw_text = _query_mistral(
                    system_instruction,
                    prompt,
                    model,
                    api_key=api_key,
                    timeout=timeout,
                    max_output_tokens=max_output_tokens,
                )
            elif provider_norm in ("openai",):
                raw_text = _query_openai(
                    system_instruction,
                    prompt,
                    model,
                    api_key=api_key,
                    timeout=timeout,
                    max_output_tokens=max_output_tokens,
                )
            else:
                if console:
                    console.print(f"  Unknown provider: {provider}", style="bold red")
                return None
        except Exception as e:
            if console:
                console.print(f"  [yellow]LLM query exception: {e}[/]")
            return None

        if not raw_text:
            if attempt < max_retries:
                time.sleep(1.5)
                continue
            return None

        cleaned = _clean_json_response(raw_text)
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError as err:
            if attempt < max_retries:
                prompt = (
                    f"{prompt}\n\nCRITICAL: Your previous output had invalid JSON syntax: {err}. "
                    f"Return ONLY valid JSON without markdown fences."
                )
                time.sleep(1)
                continue
            if console:
                console.print(f"  [yellow]Failed to parse model JSON: {err}[/]")
            return None

    return None


def _query_gemini(
    system_instruction: str,
    prompt: str,
    model: str,
    api_key: Optional[str],
    timeout: int = 45,
    max_retries: int = 5,
    max_output_tokens: int = 8192,
) -> Optional[str]:
    """Query Google Gemini REST API with 429/503 exponential backoff retries."""
    if not api_key:
        return None
    clean_model = model.replace("gemini/", "")
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent"
        f"?key={api_key}"
    )
    payload = {
        "system_instruction": {"parts": [{"text": system_instruction}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_output_tokens,
            "responseMimeType": "application/json",
        },
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
                return None
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < max_retries - 1:
                delay = _calculate_backoff(attempt, getattr(e, "headers", None))
                time.sleep(delay)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue
            raise
    return None


def _query_ollama(
    system_instruction: str,
    prompt: str,
    model: str,
    host: str = "http://localhost:11434",
    timeout: int = 60,
    max_retries: int = 2,
    max_output_tokens: int = 8192,
) -> Optional[str]:
    """Query local Ollama instance with JSON format constraint."""
    clean_host = host.rstrip("/")
    if not clean_host.startswith("http://") and not clean_host.startswith("https://"):
        clean_host = f"http://{clean_host}"
    if "0.0.0.0" in clean_host:
        clean_host = clean_host.replace("0.0.0.0", "127.0.0.1")

    url = f"{clean_host}/api/generate"
    clean_model = model.replace("ollama/", "")
    payload = {
        "model": clean_model,
        "system": system_instruction,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2, "num_predict": max_output_tokens},
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data.get("response", "").strip()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < max_retries - 1:
                time.sleep((attempt + 1) * 2)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue
            raise
    return None


def _query_anthropic(
    system_instruction: str,
    prompt: str,
    model: str,
    api_key: Optional[str],
    timeout: int = 45,
    max_retries: int = 5,
    max_output_tokens: int = 8192,
) -> Optional[str]:
    """Query Anthropic Messages API with 429/529 retry handling."""
    if not api_key:
        return None
    clean_model = model.replace("anthropic/", "")
    url = "https://api.anthropic.com/v1/messages"
    payload: Dict[str, Any] = {
        "model": clean_model,
        "max_tokens": max_output_tokens,
        "system": system_instruction,
        "messages": [{"role": "user", "content": prompt}],
    }
    if not any(
        v in clean_model for v in ("-5", "sonnet-5", "haiku-5", "opus-5", "fable-5")
    ):
        payload["temperature"] = 0.2
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"), headers=headers
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                blocks = [
                    b["text"]
                    for b in data.get("content", [])
                    if b.get("type") == "text" and "text" in b
                ]
                return "\n".join(blocks).strip() if blocks else None
        except urllib.error.HTTPError as e:
            if e.code in (429, 529, 503) and attempt < max_retries - 1:
                delay = _calculate_backoff(attempt, getattr(e, "headers", None))
                time.sleep(delay)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue
            raise
    return None


def _query_mistral(
    system_instruction: str,
    prompt: str,
    model: str,
    api_key: Optional[str],
    timeout: int = 45,
    max_retries: int = 5,
    max_output_tokens: int = 8192,
) -> Optional[str]:
    """Query Mistral AI API with retry handling."""
    if not api_key:
        return None
    clean_model = model.replace("mistral/", "")
    url = "https://api.mistral.ai/v1/chat/completions"
    payload = {
        "model": clean_model,
        "temperature": 0.2,
        "max_tokens": max_output_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"), headers=headers
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < max_retries - 1:
                delay = _calculate_backoff(attempt, getattr(e, "headers", None))
                time.sleep(delay)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue
            raise
    return None


def _query_openai(
    system_instruction: str,
    prompt: str,
    model: str,
    api_key: Optional[str],
    timeout: int = 45,
    max_retries: int = 5,
    max_output_tokens: int = 8192,
) -> Optional[str]:
    """Query OpenAI API with JSON mode and retry handling."""
    if not api_key:
        return None
    clean_model = model.replace("openai/", "")
    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": clean_model,
        "temperature": 0.2,
        "max_tokens": max_output_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"), headers=headers
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < max_retries - 1:
                delay = _calculate_backoff(attempt, getattr(e, "headers", None))
                time.sleep(delay)
                continue
            raise
        except (urllib.error.URLError, TimeoutError):
            if attempt < max_retries - 1:
                time.sleep(1.5)
                continue
            raise
    return None


class MnemonicWizard:
    """Orchestrates interactive authoring of Personas, Memories, and Lineages."""

    def __init__(
        self,
        console: Optional[Console] = None,
        input_fn: Optional[Callable[[str], str]] = None,
        output_dir: Optional[Union[str, Path]] = None,
    ):
        self.console = console or Console()
        self.input_fn = input_fn or builtins.input
        self.config = load_config()

        # Determine target scaffold directory
        if output_dir:
            self.base_output_dir = Path(output_dir).resolve()
        elif Path("./mnemonics").is_dir():
            self.base_output_dir = Path("./mnemonics").resolve()
        elif Path("./.mnemolink").is_dir():
            self.base_output_dir = Path("./.mnemolink").resolve()
        elif self.config.catalog_roots:
            self.base_output_dir = (
                Path(self.config.catalog_roots[0]).expanduser().resolve()
            )
        elif (Path.home() / "mnemonics").is_dir():
            self.base_output_dir = (Path.home() / "mnemonics").resolve()
        else:
            self.base_output_dir = (Path.home() / ".mnemolink").resolve()

    def _read(self, prompt_text: str, default: str = "") -> str:
        suffix = f" [{default}]" if default else ""
        full_prompt = f"  {prompt_text}{suffix}: "
        try:
            val = self.input_fn(full_prompt).strip()
            return val if val else default
        except (KeyboardInterrupt, EOFError):
            return default

    def _read_multiline_list(self, prompt_text: str, tooltip: str = "") -> List[str]:
        if tooltip:
            self.console.print(f"  [dim italic]{tooltip}[/]")
        self.console.print(
            f"  {prompt_text} (comma-separated or Enter for items):", style="dim"
        )
        raw = self._read(">")
        if not raw:
            return []
        if "," in raw:
            return [item.strip() for item in raw.split(",") if item.strip()]
        return [raw.strip()]

    # --------------------------------------------------------------------------
    # Model Selection for AI-Assisted Mode
    # --------------------------------------------------------------------------

    def setup_ai_model(self) -> Optional[Tuple[str, str, Optional[str]]]:
        """Resolve AI execution target, provider, model name, and API credentials.

        Strictly enforces NO hardcoded default models. The user chooses API vs Ollama,
        specifies provider, and enters/pastes the exact model name with official documentation
        tooltips. For Ollama, verifies local model presence and gives guidance for pulling models.
        """
        p = palette()
        cfg = self.config

        # If already configured in config.yaml, offer to use it
        if cfg.provider and cfg.model:
            self.console.print(
                f"  Configured model: [bold {p.mint}]{cfg.provider}/{cfg.model}[/]"
            )
            use_existing = self._read(
                "Use this configured model? (Y/n)", default="y"
            ).lower()
            if use_existing not in ("n", "no"):
                api_key = None
                if cfg.provider != "ollama":
                    api_key = resolve_api_key(
                        cfg.provider,
                        interactive=True,
                        input_fn=self.input_fn,
                        console=self.console,
                    )
                return cfg.provider, cfg.model, api_key

        self.console.print("\n  [bold]Select AI Execution Target:[/]")
        self.console.print(
            "    [1] Cloud Provider API (Google Gemini, Anthropic Claude, Mistral AI, OpenAI)",
            style=p.menu_style,
        )
        self.console.print(
            "    [2] Local Ollama (offline local daemon)", style=p.menu_style
        )

        target_choice = self._read("target [1-2]", default="1")

        if target_choice == "2" or target_choice.lower() == "ollama":
            # Local Ollama branch
            provider = "ollama"
            self.console.print("\n  [bold]Local Ollama Configuration:[/]")
            ollama_url = PROVIDER_MODEL_URLS.get("ollama", "https://ollama.com/library")
            self.console.print(
                f"  [dim italic]Browse Ollama library:[/] [cyan]{ollama_url}[/]"
            )
            self.console.print(
                "  [dim italic]Pull models in terminal:[/] "
                "[cyan]ollama pull <model>[/] (e.g. ollama pull llama3.2:1b)"
            )
            local_models = list_ollama_local_models(cfg.ollama_host)
            if local_models:
                self.console.print(
                    f"  Installed local models: [dim]{', '.join(local_models)}[/]",
                    style=p.mint,
                )
            else:
                self.console.print(
                    "  [yellow]Notice: Could not query local Ollama models "
                    "(daemon offline or none installed).[/]",
                    style="dim",
                )

            while True:
                model = self._read(
                    "Enter or paste Ollama model name (e.g. llama3.2:1b)"
                )
                if not model:
                    if local_models:
                        model = local_models[0]
                        break
                    return None

                clean_m = model.replace("ollama/", "")
                if local_models:
                    found = any(
                        m == clean_m or m.startswith(f"{clean_m}:")
                        for m in local_models
                    )
                    if found:
                        self.console.print(
                            f"  [green]Verified:[/] Model '{clean_m}' is installed locally."
                        )
                        model = clean_m
                        break
                    else:
                        self.console.print(
                            f"  [yellow]Warning:[/] Model '{clean_m}' not found "
                            "in your local Ollama daemon."
                        )
                        self.console.print(
                            f"  Installed models: {', '.join(local_models)}"
                        )
                        self.console.print(
                            f"  Run 'ollama pull {clean_m}' in another terminal to download it."
                        )
                        action = self._read(
                            "Use anyway, pick installed, or re-enter? (use/pick/re-enter)",
                            default="use",
                        ).lower()
                        if action.startswith("p"):
                            for idx, im in enumerate(local_models):
                                self.console.print(f"    [{idx + 1}] {im}", style="dim")
                            pick_idx = self._read("Select number", default="1")
                            if pick_idx.isdigit() and 1 <= int(pick_idx) <= len(
                                local_models
                            ):
                                model = local_models[int(pick_idx) - 1]
                                break
                        elif action.startswith("u") or action in ("y", "yes"):
                            model = clean_m
                            break
                        else:
                            continue
                else:
                    model = clean_m
                    break

            api_key = None
        else:
            # Cloud Provider API branch
            self.console.print("\n  [bold]Select Cloud Provider:[/]")
            self.console.print("    [1] Google Gemini", style=p.menu_style)
            self.console.print("    [2] Anthropic Claude", style=p.menu_style)
            self.console.print("    [3] Mistral AI", style=p.menu_style)
            self.console.print("    [4] OpenAI", style=p.menu_style)
            self.console.print("    [5] Other / Custom", style=p.menu_style)

            prov_choice = self._read("provider [1-5]", default="1")
            prov_map = {
                "1": "gemini",
                "gemini": "gemini",
                "google": "gemini",
                "2": "anthropic",
                "claude": "anthropic",
                "anthropic": "anthropic",
                "3": "mistral",
                "mistral": "mistral",
                "4": "openai",
                "openai": "openai",
                "5": "custom",
            }
            provider = prov_map.get(prov_choice.lower(), "gemini")
            if provider == "custom":
                provider = self._read(
                    "Enter provider name (e.g. groq, deepseek)",
                    default="openai",
                ).lower()

            model_url = PROVIDER_MODEL_URLS.get(provider)
            examples = PROVIDER_MODEL_EXAMPLES.get(provider)

            self.console.print(f"\n  [bold]{provider.title()} Model Selection:[/]")
            if model_url:
                self.console.print(
                    f"  [dim italic]Browse official model catalog:[/] [cyan]{model_url}[/]"
                )
            if examples:
                self.console.print(
                    f"  [dim italic]Model examples:[/] [dim]{examples}[/]"
                )

            hint = (
                cfg.model
                if (cfg.model and getattr(cfg, "provider", None) == provider)
                else ""
            )
            prompt_label = (
                f"Enter or paste {provider.title()} model name [{hint}]"
                if hint
                else f"Enter or paste {provider.title()} model name"
            )
            model = self._read(prompt_label, default=hint)
            while not model:
                self.console.print(
                    f"  [yellow]Please enter a {provider.title()} model name (see {model_url}).[/]"
                )
                model = self._read(f"Enter or paste {provider.title()} model name")

            api_key = resolve_api_key(
                provider,
                interactive=True,
                input_fn=self.input_fn,
                console=self.console,
            )
            if not api_key:
                self.console.print(
                    f"  [bold red]Error: No API key provided for {provider}.[/]"
                )
                return None

        save_pref = self._read(
            f"Save {provider}/{model} as default model in ~/.mnemolink/config.yaml? (y/N)",
            default="n",
        ).lower()
        if save_pref in ("y", "yes"):
            cfg.provider = provider
            cfg.model = model
            save_config(cfg)
            self.console.print(
                f"  Saved {provider}/{model} to ~/.mnemolink/config.yaml",
                style="dim",
            )

        return provider, model, api_key

    # --------------------------------------------------------------------------
    # Persona Creation
    # --------------------------------------------------------------------------

    def create_persona_manual(self) -> Optional[Path]:
        """Step-by-step guided manual persona authoring."""
        p = palette()
        self.console.print(
            Panel("[bold]Guided Manual Persona Scaffolding[/]", border_style=p.blue)
        )

        name = self._read("Persona Name (e.g. Byzantine Logistics Master)")
        if not name:
            return None
        slug = name.lower().replace(" ", "_")

        domain = self._read(
            "Domain (e.g. logistics, legal, robotics, sre)", default="general"
        )
        summary = self._read(
            "Summary (1-2 sentences)", default=f"Operational persona for {name}"
        )

        self.console.print("\n  [bold]Epistemological Bedrock & Worldview:[/]")
        self.console.print(
            "  [dim italic]How does this agent perceive truth, "
            "evaluate evidence, and handle uncertainty?[/]"
        )
        philosophy = self._read(
            "core_philosophy",
            default="Truth is grounded in verifiable telemetry and mutual contract equity.",
        )

        axioms = self._read_multiline_list(
            "Inviolable Axioms (Pinned Rules)",
            tooltip=(
                "Non-negotiable principles. Example: "
                "'Telemetry overrules client optimism under all pressure.'"
            ),
        )
        if not axioms:
            axioms = ["Never capitulate on verified physical constraints."]

        boundaries = self._read_multiline_list(
            "Operational Boundaries (Taboos)",
            tooltip=(
                "Strict operational prohibitions. Example: "
                "'Never execute destructive writes without declarative audit trail.'"
            ),
        )
        if not boundaries:
            boundaries = ["Never execute unverified commands in production."]

        cognitive_priors = self._read_multiline_list(
            "Cognitive Priors",
            tooltip=(
                "Default heuristics. Example: "
                "'Assume sensor washouts occur at sunrise; cross-verify inertial states.'"
            ),
        )
        if not cognitive_priors:
            cognitive_priors = ["Default to caution when metrics disagree."]

        narrative = self._read(
            "Self-Narrative (Internal Monologue)",
            default=f"I operate as the steadfast guardian of {domain}.",
        )
        voice = self._read(
            "Voice & Tone (e.g. Laconic, authoritative, unhurried)",
            default="Laconic, authoritative, surgical.",
        )

        # Build manifest and card
        manifest_data = {
            "id": slug,
            "name": name,
            "version": "1.0.0",
            "domain": domain,
            "summary": summary,
            "core_philosophy": philosophy,
            "axioms": axioms,
            "cognitive_priors": cognitive_priors,
            "self_narrative": narrative,
            "boundaries": boundaries,
            "voice_tone": voice,
            "author": "MnemoLink Wizard",
            "tags": [slug, domain],
        }

        card_data = {
            "id": slug,
            "name": name,
            "kind": "persona",
            "domain": domain,
            "version": "1.0.0",
            "summary": summary,
            "tags": [slug, domain],
            "author": "MnemoLink Wizard",
        }

        return self._save_asset("persona", slug, manifest_data, card_data)

    def create_persona_ai(self) -> Optional[Path]:
        """AI-assisted persona generation."""
        p = palette()
        self.console.print(
            Panel("[bold]AI-Assisted Persona Generator[/]", border_style=p.mint)
        )

        model_setup = self.setup_ai_model()
        if not model_setup:
            return None
        provider, model, api_key = model_setup

        self.console.print("\n  [bold]Describe the Persona you need:[/]")
        self.console.print(
            "  [dim italic]Examples:\n"
            "    - Artisan: 'A passionate Mediterranean chef dedicated to hospitality and craft.'\n"
            "    - Mentor: 'A patient educator fostering curiosity and psychological safety.'\n"
            "    - Sentinel: 'An SRE commander who enforces GitOps and zero downtime.'\n"
            "    - Scholar: 'A commercial jurist balancing equity with rigorous precision.'[/]"
        )
        user_prompt = self._read("Description")
        if not user_prompt:
            return None

        system_instruction = get_persona_system_instruction()

        with self.console.status(
            f"[bold {p.mint}]Generating Persona via {provider}/{model}...[/]"
        ):
            result = query_llm_for_json(
                user_prompt,
                system_instruction,
                provider=provider,
                model=model,
                api_key=api_key,
                ollama_host=self.config.ollama_host,
                console=self.console,
            )

        if not result or "manifest" not in result or "card" not in result:
            self.console.print(
                "  [bold red]Generation failed or output did not match expected structure.[/]"
            )
            return None

        manifest = result["manifest"]
        card = result["card"]

        # Validate with Pydantic
        try:
            PersonaProduct(**manifest)
            CatalogCard(**card)
        except Exception as e:
            self.console.print(f"  [yellow]Pydantic schema validation error: {e}[/]")
            return None

        slug = manifest.get("id", "custom_persona")
        self._preview_persona(manifest)

        confirm = self._read("Save this persona to catalog? (Y/n)", default="y").lower()
        if confirm not in ("y", "yes"):
            return None

        return self._save_asset("persona", slug, manifest, card)

    # --------------------------------------------------------------------------
    # Memory Creation (5-Kind Taxonomy)
    # --------------------------------------------------------------------------

    def create_memory_manual(self) -> Optional[Path]:
        """Step-by-step guided manual memory authoring across 5-kind taxonomy."""
        p = palette()
        self.console.print(
            Panel(
                "[bold]Guided Manual Memory Scaffolding (5-Kind Taxonomy)[/]",
                border_style=p.blue,
            )
        )

        name = self._read(
            "Memory Title (e.g. Semicolon Indemnity Summary Judgment Loss)"
        )
        if not name:
            return None
        slug = name.lower().replace(" ", "_")
        domain = self._read(
            "Domain (e.g. legal, robotics, sre, customer, culinary)", default="general"
        )

        self.console.print("\n  [bold]Select Memory Kind (5-Kind Taxonomy):[/]")
        self.console.print(
            "    [1] lore       — Traditions, cultural roots, mentorship, heritage",
            style=p.menu_style,
        )
        self.console.print(
            "    [2] work       — Technical craft, repeatable tradecraft, procedural praxis, SOPs",
            style=p.menu_style,
        )
        self.console.print(
            "    [3] incident   — Critical failure crucibles, outages, crashes, arbitration losses",
            style=p.menu_style,
        )
        self.console.print(
            "    [4] relational — Collaborative breakthroughs, team trust, partnerships",
            style=p.menu_style,
        )
        self.console.print(
            "    [5] telemetry  — Quantitative sensor traces, performance telemetry, benchmarks",
            style=p.menu_style,
        )

        kind_map = {
            "1": "lore",
            "2": "work",
            "3": "incident",
            "4": "relational",
            "5": "telemetry",
        }
        kind = kind_map.get(self._read("kind [1-5]", default="1"), "lore")

        summary = self._read(
            "Summary (1-2 sentences)", default=f"Episodic {kind} memory for {name}"
        )

        self.console.print("\n  [bold]Episodic Narrative & Debrief:[/]")
        debrief = self._read(
            "episode_debrief",
            default="Detailed first-person chronological account of what transpired.",
        )

        scars_prompt = (
            "Operational Scars (Tangible Damage Sustained)"
            if kind == "incident"
            else "Operational Scars / Challenges Overcome (Enter to skip if none)"
        )
        scars_tooltip = (
            "Concrete costs: $ USD lost, hardware destroyed, downtime incurred. "
            "Example: '$4.2M warranty judgment entered against client.'"
            if kind == "incident"
            else (
                "Friction points, early mistakes, or obstacles surmounted. "
                "Optional for positive or procedural memories."
            )
        )
        scars = self._read_multiline_list(scars_prompt, tooltip=scars_tooltip)
        if not scars and kind == "incident":
            scars = ["Operational cost or friction point recorded."]

        lessons = self._read_multiline_list(
            "Lessons Learned & Core Principles",
            tooltip="Actionable maxims, craft guidelines, or insights etched into memory.",
        )
        if not lessons:
            lessons = ["Uphold core craft principles and verified standards."]

        sensory = self._read(
            "Sensory Context & Environmental Atmosphere (optional)",
            default="",
        )
        reflection = self._read(
            "Philosophical Reflection & Meaning (optional)",
            default="",
        )

        salience_raw = self._read(
            "Salience Score (0.0 to 1.0, default 0.9)", default="0.9"
        )
        try:
            salience = float(salience_raw)
        except ValueError:
            salience = 0.9

        self.console.print("\n  [bold]Teleological Layer (Goal, Drives & Needs):[/]")
        primary_goal = self._read(
            "primary_goal (e.g. master_craft_discipline, risk_mitigation)",
            default=f"pursue_{slug}",
        )
        drives = self._read_multiline_list(
            "agent_drives (e.g. craft_excellence, risk_mitigation, hospitality)",
            tooltip="Intrinsic behavioral imperatives.",
        )
        if not drives:
            drives = ["risk_mitigation", "operational_discipline"]
        needs = self._read_multiline_list(
            "applicable_needs (e.g. contract_drafting, clause_redline)",
            tooltip="Task contexts where this memory should activate.",
        )
        if not needs:
            needs = ["incident_response", "risk_evaluation"]

        manifest_data = {
            "id": f"{domain}/{slug}",
            "name": name,
            "version": "1.0.0",
            "domain": domain,
            "memory_type": kind,
            "summary": summary,
            "episode_debrief": debrief,
            "operational_scars": scars,
            "lessons_learned": lessons,
            "sensory_context": sensory,
            "reflection": reflection,
            "salience": salience,
            "author": "MnemoLink Wizard",
            "tags": [slug, domain, kind],
            "teleology": {
                "primary_goal": primary_goal,
                "agent_drives": drives,
                "applicable_needs": needs,
            },
        }

        card_data = {
            "id": f"{domain}/{slug}",
            "name": name,
            "kind": "memory",
            "domain": domain,
            "version": "1.0.0",
            "summary": summary,
            "tags": [slug, domain, kind],
            "author": "MnemoLink Wizard",
            "teleology": {
                "primary_goal": primary_goal,
                "agent_drives": drives,
                "applicable_needs": needs,
            },
            "chunks": ["story", "scars", "lessons", "triggers", "reflection"],
        }

        return self._save_asset("memory", f"{domain}/{slug}", manifest_data, card_data)

    def create_memory_ai(self) -> Optional[Path]:
        """AI-assisted episodic memory generation across all 5 taxonomy kinds."""
        p = palette()
        self.console.print(
            Panel(
                f"[bold {p.mint}]AI Mnemonic Memory Studio (5-Kind Taxonomy)[/]\n"
                "[dim]Generate rich, authentic episodic memories: formative lore & heritage, "
                "procedural work & craft, collaborative relational bonds, sensor telemetry, "
                "or high-stakes incident crucibles.[/]",
                title="AI Memory Generator",
                border_style=p.mint,
            )
        )

        model_setup = self.setup_ai_model()
        if not model_setup:
            return None
        provider, model, api_key = model_setup

        self.console.print(
            "\n  [bold]Describe the experience, event, craft technique, or incident:[/]"
        )
        self.console.print(
            "  [dim italic]Examples:\n"
            "    - Lore: 'Formative memories of bougatsa pastry discipline in Thessaloniki.'\n"
            "    - Work: 'SOP protocol for hot-patching a database connection pool safely.'\n"
            "    - Incident: 'UAV glare washout causing near-stall before sensor failover.'\n"
            "    - Relational: 'Navigating tense enterprise contract renewal with skeptical CFO.'\n"
            "    - Telemetry: 'Acoustic calibration test on composite wing spars at Mach 0.8.'[/]"
        )
        user_prompt = self._read("Memory Story / Experience")
        if not user_prompt:
            return None

        system_instruction = get_memory_system_instruction()

        with self.console.status(
            f"[bold {p.mint}]Generating Memory Episode via {provider}/{model}...[/]"
        ):
            result = query_llm_for_json(
                user_prompt,
                system_instruction,
                provider=provider,
                model=model,
                api_key=api_key,
                ollama_host=self.config.ollama_host,
                console=self.console,
            )

        if not result or "manifest" not in result or "card" not in result:
            self.console.print(
                "  [bold red]Generation failed or output did not match expected structure.[/]"
            )
            return None

        manifest = result["manifest"]
        card = result["card"]

        # Validate with Pydantic
        try:
            MemoryProduct(**manifest)
            CatalogCard(**card)
        except Exception as e:
            self.console.print(f"  [yellow]Pydantic schema validation error: {e}[/]")
            return None

        slug = manifest.get("id", "custom_memory")
        self._preview_memory(manifest)

        confirm = self._read("Save this memory to catalog? (Y/n)", default="y").lower()
        if confirm not in ("y", "yes"):
            return None

        return self._save_asset("memory", slug, manifest, card)

    # --------------------------------------------------------------------------
    # Lineage Creation (Manual Catalog Picker & AI Causal Bridge Generator)
    # --------------------------------------------------------------------------

    def create_lineage_manual(self) -> Optional[Path]:
        """Manual Lineage assembly from existing catalog memories with LineageBuilder bridges."""
        p = palette()
        self.console.print(
            Panel("[bold]Guided Manual Lineage Assembler[/]", border_style=p.blue)
        )

        resolver = MnemonicResolver()
        cards = resolver.find_cards(kind="memory")
        if not cards:
            self.console.print(
                "  [yellow]No memories found in catalog to assemble a lineage from.[/]"
            )
            return None

        table = Table(
            title="Available Memories in Catalog",
            border_style=p.blue,
            box=box.SIMPLE_HEAVY,
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Kind", style="dim", width=10)
        table.add_column("Domain", style="cyan", width=12)
        table.add_column("ID", style=f"bold {p.mint}", no_wrap=True)
        table.add_column("Name", style="white")

        for idx, card in enumerate(cards):
            table.add_row(str(idx + 1), card.kind, card.domain, card.id, card.name)

        self.console.print(table)

        self.console.print(
            "\n  [bold]Select memories for the chronological progression:[/]"
        )
        raw_selection = self._read(
            "Enter memory numbers in chronological order (e.g. 1, 3)"
        )
        if not raw_selection:
            return None

        selected_ids: List[str] = []
        for token in raw_selection.split(","):
            token_clean = token.strip()
            if token_clean.isdigit():
                idx_val = int(token_clean) - 1
                if 0 <= idx_val < len(cards):
                    selected_ids.append(cards[idx_val].id)

        if len(selected_ids) < 2:
            self.console.print(
                "  [yellow]Lineages require at least 2 memories to form causal bridges.[/]"
            )
            return None

        lineage_name = self._read(
            "Lineage Name (e.g. High Stakes Operational Ascendance)"
        )
        slug = lineage_name.lower().replace(" ", "_")
        domain = cards[0].domain

        persona_id = self._read(
            "Anchor Persona ID (optional, press Enter to skip)", default=""
        )

        # Synthesize with LineageBuilder
        loaded_memories = [resolver.find_memory(mid) for mid in selected_ids]
        loaded_persona = resolver.find_persona(persona_id) if persona_id else None

        builder = LineageBuilder(persona=loaded_persona)
        synthesized = builder.build(loaded_memories, lineage_id=slug, name=lineage_name)

        manifest_data = {
            "id": slug,
            "name": lineage_name,
            "version": "1.0.0",
            "domain": domain,
            "summary": f"Lineage connecting {', '.join(selected_ids)}",
            "memory_ids": selected_ids,
            "chronology": synthesized.chronology,
            "causal_bridges": synthesized.causal_bridges,
            "cumulative_narrative": synthesized.cumulative_narrative,
            "author": "MnemoLink Wizard",
            "tags": [slug, domain, "lineage"],
        }

        card_data = {
            "id": slug,
            "name": lineage_name,
            "kind": "lineage",
            "domain": domain,
            "version": "1.0.0",
            "summary": f"Progression across {len(selected_ids)} crucibles",
            "tags": [slug, domain, "lineage"],
            "author": "MnemoLink Wizard",
        }

        return self._save_asset("lineage", slug, manifest_data, card_data)

    def create_lineage_ai(self) -> Optional[Path]:
        """AI-assisted Lineage creation: model parses catalog, cherry-picks memories,
        and crafts associative causal bridges."""
        p = palette()
        self.console.print(
            Panel("[bold]AI-Assisted Lineage Synthesizer[/]", border_style=p.mint)
        )

        model_setup = self.setup_ai_model()
        if not model_setup:
            return None
        provider, model, api_key = model_setup

        resolver = MnemonicResolver()
        cards = resolver.find_cards(kind="memory")
        if not cards:
            self.console.print("  [yellow]No memories found in catalog.[/]")
            return None

        catalog_summary = "\n".join(
            f"- ID: {c.id} | Domain: {c.domain} | Name: {c.name} | "
            f"Summary: {c.summary[:60]}"
            for c in cards
        )

        self.console.print(
            "\n  [bold]Describe the desired evolutionary backstory or career progression:[/]"
        )
        self.console.print(
            "  [dim italic]Examples:\n"
            "    - Mastery: 'Mediterranean chef progressing from apprentice to culinary icon.'\n"
            "    - Craft: 'SRE advancing from junior responder to principal architect.'\n"
            "    - Hardening: 'Autonomous pilot evolving to all-weather flight mastery.'[/]"
        )
        user_prompt = self._read("Progression Requirement")
        if not user_prompt:
            return None

        full_prompt = (
            f"User Requirement:\n{user_prompt}\n\n"
            f"Available Memories in Catalog:\n{catalog_summary}\n\n"
            "Select 2 to 4 of the most relevant memories from the catalog above. "
            "Order them chronologically, derive epoch milestones, and write "
            "compelling associative causal bridges explaining how earlier experiences "
            "and milestones prepared the agent for subsequent horizons."
        )

        system_instruction = get_lineage_system_instruction()

        with self.console.status(
            f"[bold {p.mint}]Synthesizing Lineage Progression via {provider}/{model}...[/]"
        ):
            result = query_llm_for_json(
                full_prompt,
                system_instruction,
                provider=provider,
                model=model,
                api_key=api_key,
                ollama_host=self.config.ollama_host,
                console=self.console,
            )

        if not result or "manifest" not in result or "card" not in result:
            self.console.print(
                "  [bold red]Generation failed or output did not match expected structure.[/]"
            )
            return None

        manifest = result["manifest"]
        card = result["card"]

        try:
            LineageProduct(**manifest)
            CatalogCard(**card)
        except Exception as e:
            self.console.print(f"  [yellow]Pydantic schema validation error: {e}[/]")
            return None

        slug = manifest.get("id", "custom_lineage")
        self._preview_lineage(manifest)

        confirm = self._read("Save this lineage to catalog? (Y/n)", default="y").lower()
        if confirm not in ("y", "yes"):
            return None

        return self._save_asset("lineage", slug, manifest, card)

    # --------------------------------------------------------------------------
    # Storage & Previews
    # --------------------------------------------------------------------------

    def _save_asset(
        self,
        kind: str,
        slug_or_id: str,
        manifest_data: Dict[str, Any],
        card_data: Dict[str, Any],
    ) -> Path:
        """Save YAML manifest and JSON card to target catalog directory."""
        from mnemolink.config import register_catalog_root

        clean_slug = slug_or_id.replace("/", os.sep)
        folder_name = _kind_dir_name(kind)
        target_dir = self.base_output_dir / folder_name / clean_slug
        target_dir.mkdir(parents=True, exist_ok=True)

        manifest_file = target_dir / f"{kind}.yaml"
        card_file = target_dir / "card.json"

        manifest_file.write_text(
            yaml.dump(manifest_data, sort_keys=False), encoding="utf-8"
        )
        card_file.write_text(json.dumps(card_data, indent=2), encoding="utf-8")

        # Auto-register catalog root in config
        register_catalog_root(self.base_output_dir)

        p = palette()
        self.console.print(
            Panel(
                f"[bold {p.mint}]Successfully Scaffolding {kind.title()}![/]\n\n"
                f"[cyan]Directory:[/] {target_dir}\n"
                f"[dim]Inspect with:[/] mnemolink inspect {slug_or_id}",
                title="Asset Created",
                border_style=p.mint,
            )
        )
        return target_dir

    def _preview_persona(self, m: Dict[str, Any]) -> None:
        p = palette()
        body_parts = [
            f"[bold {p.pink}]{m.get('name')}[/] [dim]({m.get('id')})[/]",
            f"[dim]Domain:[/] {m.get('domain')} | [italic]{m.get('summary')}[/]",
            f"\n[bold {p.pink}]Core Philosophy:[/]\n{m.get('core_philosophy')}",
            f"\n[bold {p.mint}]Inviolable Axioms:[/]\n"
            + "\n".join(f"  - {a}" for a in m.get("axioms", [])),
            f"\n[bold {p.peach}]Operational Boundaries:[/]\n"
            + "\n".join(f"  - {b}" for b in m.get("boundaries", [])),
        ]
        if m.get("cognitive_priors"):
            body_parts.append(
                f"\n[bold {p.blue}]Cognitive Priors:[/]\n"
                + "\n".join(f"  - {cp}" for cp in m.get("cognitive_priors", []))
            )
        if m.get("self_narrative"):
            body_parts.append(
                f"\n[bold {p.lavender}]Self-Narrative:[/]\n{m.get('self_narrative')}"
            )
        if m.get("voice_tone"):
            body_parts.append(
                f"\n[bold {p.pink}]Voice & Tone:[/] {m.get('voice_tone')}"
            )
        teleology = m.get("teleology")
        if teleology and isinstance(teleology, dict):
            t_goal = teleology.get("primary_goal", "")
            t_drives = ", ".join(teleology.get("agent_drives", []))
            t_needs = ", ".join(teleology.get("applicable_needs", []))
            body_parts.append(
                f"\n[bold {p.mint}]Teleology:[/]\n"
                f"  - Goal:   {t_goal}\n"
                f"  - Drives: {t_drives}\n"
                f"  - Needs:  {t_needs}"
            )
        if m.get("tags"):
            tags_str = " ".join(f"#{t}" for t in m.get("tags", []))
            body_parts.append(f"\n[dim cyan]{tags_str}[/]")

        self.console.print(
            Panel(
                "\n".join(body_parts),
                title="Persona Preview",
                border_style=p.blue,
            )
        )

    def _preview_memory(self, m: Dict[str, Any]) -> None:
        p = palette()
        salience = m.get("salience", 0.8)
        body_parts = [
            f"[bold {p.pink}]{m.get('name')}[/] [dim]({m.get('id')})[/]",
            (
                f"[dim]Kind:[/] {m.get('memory_type')} | "
                f"[dim]Domain:[/] {m.get('domain')} | "
                f"[dim]Salience:[/] {salience}"
            ),
            f"\n[bold {p.pink}]Debrief:[/]\n{m.get('episode_debrief')}",
        ]
        scars = m.get("operational_scars", [])
        if scars:
            scars_title = (
                "[bold red]Operational Scars:[/]"
                if m.get("memory_type") == "incident"
                else f"[bold {p.peach}]Operational Scars & Challenges Overcome:[/]"
            )
            body_parts.append(
                f"\n{scars_title}\n" + "\n".join(f"  - {s}" for s in scars)
            )
        lessons = m.get("lessons_learned", [])
        if lessons:
            body_parts.append(
                f"\n[bold {p.mint}]Lessons Learned & Principles:[/]\n"
                + "\n".join(f"  - {lesson}" for lesson in lessons)
            )
        if m.get("sensory_context"):
            body_parts.append(
                f"\n[bold {p.peach}]Sensory & Telemetry Cues:[/]\n{m.get('sensory_context')}"
            )
        if m.get("reflection"):
            body_parts.append(
                f"\n[bold {p.lavender}]Philosophical Reflection:[/]\n{m.get('reflection')}"
            )
        teleology = m.get("teleology")
        if teleology and isinstance(teleology, dict):
            t_goal = teleology.get("primary_goal", "")
            t_drives = ", ".join(teleology.get("agent_drives", []))
            t_needs = ", ".join(teleology.get("applicable_needs", []))
            body_parts.append(
                f"\n[bold {p.mint}]Teleology:[/]\n"
                f"  - Primary Goal:    {t_goal}\n"
                f"  - Agent Drives:    {t_drives}\n"
                f"  - Applicable Needs:{t_needs}"
            )
        if m.get("tags"):
            tags_str = " ".join(f"#{t}" for t in m.get("tags", []))
            body_parts.append(f"\n[dim cyan]{tags_str}[/]")

        self.console.print(
            Panel(
                "\n".join(body_parts),
                title="Memory Preview",
                border_style=p.blue,
            )
        )

    def _preview_lineage(self, m: Dict[str, Any]) -> None:
        p = palette()
        body_parts = [
            f"[bold {p.pink}]{m.get('name')}[/] [dim]({m.get('id')})[/]",
            f"[dim]Domain:[/] {m.get('domain', 'general')} | [italic]{m.get('summary', '')}[/]",
            f"[dim]Memory Spine:[/] {', '.join(m.get('memory_ids', []))}",
            f"\n[bold {p.mint}]Chronology Milestones:[/]\n"
            + "\n".join(
                f"  {idx+1}. {c}" for idx, c in enumerate(m.get("chronology", []))
            ),
            f"\n[bold {p.blue}]Causal Bridges:[/]\n"
            + "\n".join(f"  - {b}" for b in m.get("causal_bridges", [])),
        ]
        if m.get("cumulative_narrative"):
            body_parts.append(
                f"\n[bold {p.lavender}]Cumulative Narrative:[/]\n{m.get('cumulative_narrative')}"
            )
        teleology = m.get("teleology")
        if teleology and isinstance(teleology, dict):
            t_goal = teleology.get("primary_goal", "")
            t_drives = ", ".join(teleology.get("agent_drives", []))
            t_needs = ", ".join(teleology.get("applicable_needs", []))
            body_parts.append(
                f"\n[bold {p.mint}]Teleology:[/]\n"
                f"  - Goal:   {t_goal}\n"
                f"  - Drives: {t_drives}\n"
                f"  - Needs:  {t_needs}"
            )
        if m.get("tags"):
            tags_str = " ".join(f"#{t}" for t in m.get("tags", []))
            body_parts.append(f"\n[dim cyan]{tags_str}[/]")

        self.console.print(
            Panel(
                "\n".join(body_parts),
                title="Lineage Preview",
                border_style=p.blue,
            )
        )

    # --------------------------------------------------------------------------
    # Main Wizard Entrypoint
    # --------------------------------------------------------------------------

    def run(self) -> None:
        """Run the top-level wizard dispatcher."""
        p = palette()
        self.console.print(
            Panel(
                f"[bold {p.pink}]MnemoLink Mnemonic Wizard[/]\n"
                "[dim]Interactive authoring studio for Personas, Memories, and Lineages[/]",
                border_style=p.lavender,
            )
        )

        self.console.print("  What would you like to create?")
        self.console.print(
            "    [1] Persona — Philosophical axioms, boundaries, cognitive priors",
            style=p.menu_style,
        )
        self.console.print(
            "    [2] Memory  — Episodic experiences, lore & craft, breakthroughs, or scars",
            style=p.menu_style,
        )
        self.console.print(
            "    [3] Lineage — Multi-epoch backstories, developmental arcs, and causal bridges",
            style=p.menu_style,
        )
        self.console.print("    [0] Exit", style="dim")

        asset_choice = self._read("choice [1-3]", default="1")
        if asset_choice in ("0", "q", "quit", "exit"):
            return

        self.console.print("\n  Choose Authoring Track:")
        self.console.print(
            "    [1] Guided Manual — Step-by-step interactive prompts with tooltips",
            style=p.menu_style,
        )
        self.console.print(
            "    [2] AI-Assisted   — Describe in natural language; LLM generates schemas",
            style=p.menu_style,
        )

        track_choice = self._read("track [1-2]", default="1")

        if asset_choice == "1":
            if track_choice == "2":
                self.create_persona_ai()
            else:
                self.create_persona_manual()
        elif asset_choice == "2":
            if track_choice == "2":
                self.create_memory_ai()
            else:
                self.create_memory_manual()
        elif asset_choice == "3":
            if track_choice == "2":
                self.create_lineage_ai()
            else:
                self.create_lineage_manual()
        else:
            self.console.print(f"  Unknown option '{asset_choice}'", style="dim red")


def cmd_wizard(args: argparse.Namespace) -> None:
    """CLI handler for `mnemolink wizard`."""
    output_dir = getattr(args, "dir", None)
    wizard = MnemonicWizard(output_dir=output_dir)
    wizard.run()

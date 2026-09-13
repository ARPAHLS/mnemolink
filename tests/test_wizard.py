"""Unit tests for the MnemoLink Mnemonic Wizard and AI generation engine.

All tests are 100% offline and use mocked inputs and LLM responses.
Zero external network calls or .env dependency in CI.
"""

import io
import json
import urllib.error
from unittest.mock import MagicMock, patch

import pytest
import yaml
from rich.console import Console

from mnemolink.cli import main
from mnemolink.models import CatalogCard, LineageProduct, MemoryProduct, PersonaProduct
from mnemolink.wizard import (
    MnemonicWizard,
    _clean_json_response,
    _query_anthropic,
    _query_gemini,
    _query_mistral,
    _query_ollama,
    _query_openai,
    query_llm_for_json,
)
from mnemolink.config import MnemoLinkConfig


@pytest.fixture(autouse=True)
def isolate_wizard_config(monkeypatch):
    """Ensure wizard tests run with clean, unconfigured settings."""
    clean_cfg = MnemoLinkConfig()
    monkeypatch.setattr("mnemolink.wizard.load_config", lambda: clean_cfg)
    monkeypatch.setattr("mnemolink.config.load_config", lambda: clean_cfg)
    monkeypatch.setattr("mnemolink.config.save_config", lambda _: None)
    monkeypatch.setattr("mnemolink.wizard.save_config", lambda _: None)


# ==============================================================================
# 1. JSON Cleaning and Response Parsing Tests
# ==============================================================================


def test_clean_json_response_raw():
    raw = '{"name": "test", "val": 123}'
    assert _clean_json_response(raw) == raw


def test_clean_json_response_markdown_fences():
    raw = """Here is your JSON:
```json
{
  "manifest": {
    "id": "my_persona",
    "name": "My Persona"
  }
}
```
Hope this helps!"""
    cleaned = _clean_json_response(raw)
    parsed = json.loads(cleaned)
    assert parsed["manifest"]["id"] == "my_persona"


def test_clean_json_response_surrounded_by_text_no_fences():
    raw = 'Sure thing: {"id": "surrounded", "status": "ok"} Thank you!'
    cleaned = _clean_json_response(raw)
    assert cleaned == '{"id": "surrounded", "status": "ok"}'


# ==============================================================================
# 2. LLM Query & Error Handling / Retry Tests
# ==============================================================================


def test_query_gemini_success():
    fake_body = {
        "candidates": [{"content": {"parts": [{"text": '{"result": "gemini_ok"}'}]}}]
    }
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = io.BytesIO(json.dumps(fake_body).encode("utf-8"))
    mock_ctx.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=mock_ctx):
        res = _query_gemini(
            system_instruction="sys",
            prompt="user prompt",
            model="gemini-3.5-flash",
            api_key="fake_key",
        )
        assert res == '{"result": "gemini_ok"}'


def test_query_gemini_retry_on_429():
    fake_body = {
        "candidates": [
            {"content": {"parts": [{"text": '{"result": "recovered_after_429"}'}]}}
        ]
    }
    success_ctx = MagicMock()
    success_ctx.__enter__.return_value = io.BytesIO(
        json.dumps(fake_body).encode("utf-8")
    )
    success_ctx.__exit__.return_value = False

    http_429 = urllib.error.HTTPError(
        url="http://test", code=429, msg="Too Many Requests", hdrs={}, fp=None
    )

    with patch("urllib.request.urlopen", side_effect=[http_429, success_ctx]):
        with patch("time.sleep"):
            res = _query_gemini(
                system_instruction="sys",
                prompt="user prompt",
                model="gemini-3.5-flash",
                api_key="fake_key",
                max_retries=2,
            )
            assert res == '{"result": "recovered_after_429"}'


def test_query_ollama_success():
    fake_body = {"response": '{"result": "ollama_ok"}'}
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = io.BytesIO(json.dumps(fake_body).encode("utf-8"))
    mock_ctx.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=mock_ctx):
        res = _query_ollama(
            system_instruction="sys",
            prompt="prompt",
            model="llama3.2:1b",
        )
        assert res == '{"result": "ollama_ok"}'


def test_query_anthropic_success():
    fake_body = {"content": [{"type": "text", "text": '{"result": "claude_ok"}'}]}
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = io.BytesIO(json.dumps(fake_body).encode("utf-8"))
    mock_ctx.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=mock_ctx):
        res = _query_anthropic(
            system_instruction="sys",
            prompt="prompt",
            model="claude-sonnet-5",
            api_key="fake_key",
        )
        assert res == '{"result": "claude_ok"}'


def test_query_mistral_success():
    fake_body = {"choices": [{"message": {"content": '{"result": "mistral_ok"}'}}]}
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = io.BytesIO(json.dumps(fake_body).encode("utf-8"))
    mock_ctx.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=mock_ctx):
        res = _query_mistral(
            system_instruction="sys",
            prompt="prompt",
            model="ministral-8b-latest",
            api_key="fake_key",
        )
        assert res == '{"result": "mistral_ok"}'


def test_query_openai_success():
    fake_body = {"choices": [{"message": {"content": '{"result": "openai_ok"}'}}]}
    mock_ctx = MagicMock()
    mock_ctx.__enter__.return_value = io.BytesIO(json.dumps(fake_body).encode("utf-8"))
    mock_ctx.__exit__.return_value = False

    with patch("urllib.request.urlopen", return_value=mock_ctx):
        res = _query_openai(
            system_instruction="sys",
            prompt="prompt",
            model="gpt-5.6-luna",
            api_key="fake_key",
        )
        assert res == '{"result": "openai_ok"}'


def test_query_llm_for_json_self_healing_retry():
    bad_json = "I am an AI and here is your result: {missing_quotes: true"
    good_json = '{"manifest": {"name": "valid"}, "card": {"name": "valid"}}'

    with patch("mnemolink.wizard._query_gemini", side_effect=[bad_json, good_json]):
        with patch("time.sleep"):
            data = query_llm_for_json(
                prompt="make something",
                system_instruction="rules",
                provider="gemini",
                model="gemini-3.5-flash",
                api_key="fake_key",
                max_retries=1,
            )
            assert data is not None
            assert data["manifest"]["name"] == "valid"


def test_query_llm_for_json_unknown_provider():
    res = query_llm_for_json(
        prompt="hello",
        system_instruction="rules",
        provider="nonexistent_llm",
        model="xyz",
    )
    assert res is None


# ==============================================================================
# 3. Model Setup Tests (No Default Model, Gemini 3.5 Flash, Ollama Choice)
# ==============================================================================


def test_setup_ai_model_gemini_selection(monkeypatch):
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    # Inputs:
    # 1. Target choice: "1" (Cloud Provider API)
    # 2. Provider choice: "1" (Gemini)
    # 3. Model name: "gemini-3.5-flash"
    # 4. Save as default: "n"
    responses = iter(["1", "1", "gemini-3.5-flash", "n"])
    monkeypatch.setenv("GEMINI_API_KEY", "mock_key_xyz")

    wizard = MnemonicWizard(console=console, input_fn=lambda _: next(responses))
    res = wizard.setup_ai_model()
    assert res is not None
    provider, model, key = res
    assert provider == "gemini"
    assert model == "gemini-3.5-flash"
    assert key == "mock_key_xyz"
    output = buf.getvalue()
    assert "https://ai.google.dev/gemini-api/docs/models/gemini" in output


def test_setup_ai_model_ollama_local_models(monkeypatch):
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    with patch(
        "mnemolink.wizard.list_ollama_local_models",
        return_value=["mistral:latest", "llama3.2:3b"],
    ):
        # Inputs:
        # 1. Target choice: "2" (Ollama)
        # 2. Model name: "llama3.2:3b"
        # 3. Save as default: "n"
        responses = iter(["2", "llama3.2:3b", "n"])

        wizard = MnemonicWizard(console=console, input_fn=lambda _: next(responses))
        res = wizard.setup_ai_model()
        assert res is not None
        provider, model, key = res
        assert provider == "ollama"
        assert model == "llama3.2:3b"
        assert key is None
        output = buf.getvalue()
        assert "Verified: Model 'llama3.2:3b' is installed locally." in output


def test_setup_ai_model_ollama_missing_pick_installed(monkeypatch):
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    with patch(
        "mnemolink.wizard.list_ollama_local_models",
        return_value=["mistral:latest", "llama3.2:3b"],
    ):
        # Inputs:
        # 1. Target choice: "2" (Ollama)
        # 2. Model name: "not-found:latest" (missing)
        # 3. Action: "pick"
        # 4. Pick choice: "2" (llama3.2:3b)
        # 5. Save as default: "n"
        responses = iter(["2", "not-found:latest", "pick", "2", "n"])

        wizard = MnemonicWizard(console=console, input_fn=lambda _: next(responses))
        res = wizard.setup_ai_model()
        assert res is not None
        provider, model, key = res
        assert provider == "ollama"
        assert model == "llama3.2:3b"
        assert key is None
        output = buf.getvalue()
        assert "Warning: Model 'not-found:latest' not found" in output


def test_setup_ai_model_ollama_missing_use_anyway(monkeypatch):
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    with patch(
        "mnemolink.wizard.list_ollama_local_models",
        return_value=["mistral:latest"],
    ):
        # Inputs:
        # 1. Target choice: "2" (Ollama)
        # 2. Model name: "qwen2.5-coder:7b" (missing)
        # 3. Action: "use"
        # 4. Save as default: "n"
        responses = iter(["2", "qwen2.5-coder:7b", "use", "n"])

        wizard = MnemonicWizard(console=console, input_fn=lambda _: next(responses))
        res = wizard.setup_ai_model()
        assert res is not None
        provider, model, key = res
        assert provider == "ollama"
        assert model == "qwen2.5-coder:7b"
        assert key is None


def test_setup_ai_model_cloud_claude_manual(monkeypatch):
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    # Target: 1 (Cloud), Provider: 2 (Claude), Model: claude-sonnet-5, Save: n
    responses = iter(["1", "2", "claude-sonnet-5", "n"])
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock_anthropic_key")

    wizard = MnemonicWizard(console=console, input_fn=lambda _: next(responses))
    res = wizard.setup_ai_model()
    assert res is not None
    provider, model, key = res
    assert provider == "anthropic"
    assert model == "claude-sonnet-5"
    assert key == "mock_anthropic_key"
    output = buf.getvalue()
    assert "https://docs.anthropic.com/en/docs/about-claude/models" in output


# ==============================================================================
# 4. Guided Manual Authoring Tests
# ==============================================================================


def test_wizard_create_persona_manual(tmp_path):
    target_dir = tmp_path / "scaffolds"
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    # Answers for guided questions:
    # name, domain, summary, philosophy, axioms, boundaries, priors, narrative, voice
    responses = iter(
        [
            "Site Reliability Sentinel",
            "sre",
            "Guardian of high availability systems",
            "Declarative invariants over procedural optimism.",
            "Never perform unverified writes to prod, Enforce circuit breakers",
            "Never bypass audit logging",
            "Assume networks will partition under stress",
            "I am the calm voice during cascade failures.",
            "Terse, clinical, unflappable.",
        ]
    )

    wizard = MnemonicWizard(
        console=console,
        input_fn=lambda _: next(responses),
        output_dir=target_dir,
    )
    saved_path = wizard.create_persona_manual()
    assert saved_path is not None
    assert (saved_path / "persona.yaml").is_file()
    assert (saved_path / "card.json").is_file()

    # Verify strictly against Pydantic schema
    raw_manifest = yaml.safe_load((saved_path / "persona.yaml").read_text("utf-8"))
    raw_card = json.loads((saved_path / "card.json").read_text("utf-8"))

    persona = PersonaProduct(**raw_manifest)
    card = CatalogCard(**raw_card)

    assert persona.id == "site_reliability_sentinel"
    assert persona.domain == "sre"
    assert len(persona.axioms) == 2
    assert card.kind == "persona"


@pytest.mark.parametrize(
    "kind_choice,expected_kind",
    [
        ("1", "lore"),
        ("2", "work"),
        ("3", "incident"),
        ("4", "relational"),
        ("5", "telemetry"),
    ],
)
def test_wizard_create_memory_manual_all_kinds(tmp_path, kind_choice, expected_kind):
    target_dir = tmp_path / "scaffolds"
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    responses = iter(
        [
            f"Test {expected_kind.title()} Episode",  # name
            "robotics",  # domain
            kind_choice,  # kind
            f"Episodic debrief for {expected_kind}",  # summary
            "First-person account of the crucible",  # debrief
            "$1.2M hardware lost, 4 hours downtime",  # scars
            "Never trust stale sensory cache",  # lessons
            "High vibration at 1200 RPM",  # sensory context
            "Physical reality checks must precede command writes",  # reflection
            "0.95",  # salience
            f"prevent_{expected_kind}_failure",  # primary goal
            "risk_mitigation, survival",  # drives
            "flight_control, preflight_checks",  # needs
        ]
    )

    wizard = MnemonicWizard(
        console=console,
        input_fn=lambda _: next(responses),
        output_dir=target_dir,
    )
    saved_path = wizard.create_memory_manual()
    assert saved_path is not None
    assert (saved_path / "memory.yaml").is_file()
    assert (saved_path / "card.json").is_file()

    raw_manifest = yaml.safe_load((saved_path / "memory.yaml").read_text("utf-8"))
    raw_card = json.loads((saved_path / "card.json").read_text("utf-8"))

    mem = MemoryProduct(**raw_manifest)
    card = CatalogCard(**raw_card)

    assert mem.memory_type == expected_kind
    assert mem.domain == "robotics"
    assert len(mem.operational_scars) == 2
    assert mem.salience == 0.95
    assert card.kind == "memory"


def test_wizard_create_lineage_manual(tmp_path):
    target_dir = tmp_path / "scaffolds"
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    # Answers:
    # 1. Select memories: "1, 2"
    # 2. Lineage name: "Autonomous Progression"
    # 3. Persona anchor: ""
    responses = iter(["1, 2", "Autonomous Progression", ""])

    wizard = MnemonicWizard(
        console=console,
        input_fn=lambda _: next(responses),
        output_dir=target_dir,
    )
    saved_path = wizard.create_lineage_manual()
    assert saved_path is not None
    assert (saved_path / "lineage.yaml").is_file()
    assert (saved_path / "card.json").is_file()

    raw_manifest = yaml.safe_load((saved_path / "lineage.yaml").read_text("utf-8"))
    raw_card = json.loads((saved_path / "card.json").read_text("utf-8"))

    lineage = LineageProduct(**raw_manifest)
    card = CatalogCard(**raw_card)

    assert lineage.id == "autonomous_progression"
    assert len(lineage.memory_ids) == 2
    assert len(lineage.chronology) == 2
    assert len(lineage.causal_bridges) == 1
    assert card.kind == "lineage"


# ==============================================================================
# 5. AI-Assisted Authoring Tests (Mocked LLM)
# ==============================================================================


def test_wizard_create_persona_ai(tmp_path):
    target_dir = tmp_path / "scaffolds"
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    mock_llm_result = {
        "manifest": {
            "id": "quantum_compiler_architect",
            "name": "Quantum Compiler Architect",
            "version": "1.0.0",
            "domain": "quantum",
            "summary": "Compiles quantum circuits avoiding decoherence traps.",
            "core_philosophy": "Coherence is a perishable physical equity.",
            "axioms": [
                "Never optimize gate depth at the expense of topological fidelity."
            ],
            "cognitive_priors": ["Assume qubit crosstalk until verified orthogonal."],
            "self_narrative": "I operate at the boundary between discrete math and cryogenics.",
            "boundaries": [
                "Never schedule pulse sequences exceeding thermal thresholds."
            ],
            "voice_tone": "Laconic, rigorous, unsparing.",
            "author": "MnemoLink Wizard",
            "tags": ["quantum", "compiler"],
        },
        "card": {
            "id": "quantum_compiler_architect",
            "name": "Quantum Compiler Architect",
            "kind": "persona",
            "domain": "quantum",
            "version": "1.0.0",
            "summary": "Compiles quantum circuits avoiding decoherence traps.",
            "tags": ["quantum", "compiler"],
            "author": "MnemoLink Wizard",
        },
    }

    # Responses:
    # 1. Description prompt: "A quantum engineer who optimizes pulse sequences"
    # 2. Confirm save: "y"
    responses = iter(["A quantum engineer who optimizes pulse sequences", "y"])

    wizard = MnemonicWizard(
        console=console,
        input_fn=lambda _: next(responses),
        output_dir=target_dir,
    )

    with patch.object(
        wizard,
        "setup_ai_model",
        return_value=("gemini", "gemini-3.5-flash", "mock_key"),
    ):
        with patch("mnemolink.wizard.query_llm_for_json", return_value=mock_llm_result):
            saved_path = wizard.create_persona_ai()
            assert saved_path is not None
            assert (saved_path / "persona.yaml").is_file()
            assert (saved_path / "card.json").is_file()

            raw_manifest = yaml.safe_load(
                (saved_path / "persona.yaml").read_text("utf-8")
            )
            persona = PersonaProduct(**raw_manifest)
            assert persona.id == "quantum_compiler_architect"
            assert persona.domain == "quantum"


def test_wizard_create_memory_ai(tmp_path):
    target_dir = tmp_path / "scaffolds"
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    mock_llm_result = {
        "manifest": {
            "id": "robotics/lidar_fog_blindness",
            "name": "Lidar Fog Blindness Near Collision",
            "version": "1.0.0",
            "domain": "robotics",
            "memory_type": "incident",
            "summary": "Autonomous rover blinded by marine fog layer.",
            "episode_debrief": (
                "During an early morning traversal, dense coastal "
                "advection fog saturated the 905nm lidar sensors."
            ),
            "operational_scars": [
                "$85,000 sensor pod replacement",
                "14 hours mission delay",
            ],
            "lessons_learned": [
                "Always cross-validate optical point clouds with millimeter-wave radar."
            ],
            "sensory_context": "Backscatter reflectivity spike exceeding 98%.",
            "reflection": "Physical atmosphere refuses to accommodate mathematical idealizations.",
            "salience": 0.92,
            "author": "MnemoLink Wizard",
            "tags": ["robotics", "lidar", "fog"],
            "teleology": {
                "primary_goal": "mitigate_fog_sensor_washout",
                "agent_drives": ["risk_mitigation", "sensor_integrity"],
                "applicable_needs": ["fog_navigation", "adverse_weather"],
            },
        },
        "card": {
            "id": "robotics/lidar_fog_blindness",
            "name": "Lidar Fog Blindness Near Collision",
            "kind": "memory",
            "domain": "robotics",
            "version": "1.0.0",
            "summary": "Autonomous rover blinded by marine fog layer.",
            "tags": ["robotics", "lidar", "fog"],
            "author": "MnemoLink Wizard",
            "teleology": {
                "primary_goal": "mitigate_fog_sensor_washout",
                "agent_drives": ["risk_mitigation", "sensor_integrity"],
                "applicable_needs": ["fog_navigation", "adverse_weather"],
            },
            "chunks": ["story", "scars", "lessons", "triggers", "reflection"],
        },
    }

    responses = iter(["A rover nearly crashed in dense marine fog", "y"])

    wizard = MnemonicWizard(
        console=console,
        input_fn=lambda _: next(responses),
        output_dir=target_dir,
    )

    with patch.object(
        wizard,
        "setup_ai_model",
        return_value=("gemini", "gemini-3.5-flash", "mock_key"),
    ):
        with patch("mnemolink.wizard.query_llm_for_json", return_value=mock_llm_result):
            saved_path = wizard.create_memory_ai()
            assert saved_path is not None
            assert (saved_path / "memory.yaml").is_file()
            assert (saved_path / "card.json").is_file()

            raw_manifest = yaml.safe_load(
                (saved_path / "memory.yaml").read_text("utf-8")
            )
            mem = MemoryProduct(**raw_manifest)
            assert mem.memory_type == "incident"
            assert mem.domain == "robotics"


def test_wizard_create_lineage_ai(tmp_path):
    target_dir = tmp_path / "scaffolds"
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    mock_llm_result = {
        "manifest": {
            "id": "maritime_emergency_pilot",
            "name": "Maritime Emergency Pilot",
            "version": "1.0.0",
            "domain": "robotics",
            "summary": "Evolution from early sensor blindness to seasoned maritime rescue.",
            "memory_ids": [
                "robotics/uav_microburst_stall",
                "robotics/imu_drift_sensor_washout",
            ],
            "chronology": ["Epoch 1: Microburst Stall", "Epoch 2: Sensor Washout"],
            "causal_bridges": [
                "Surviving the microburst stall forced the agent to build "
                "autonomous reflex loops for gyro failure."
            ],
            "cumulative_narrative": "A complete journey through extreme aeronautical crucibles.",
            "author": "MnemoLink Wizard",
            "tags": ["maritime", "lineage"],
        },
        "card": {
            "id": "maritime_emergency_pilot",
            "name": "Maritime Emergency Pilot",
            "kind": "lineage",
            "domain": "robotics",
            "version": "1.0.0",
            "summary": "Evolution from early sensor blindness to seasoned maritime rescue.",
            "tags": ["maritime", "lineage"],
            "author": "MnemoLink Wizard",
        },
    }

    responses = iter(["Career progression of an emergency drone pilot", "y"])

    wizard = MnemonicWizard(
        console=console,
        input_fn=lambda _: next(responses),
        output_dir=target_dir,
    )

    with patch.object(
        wizard,
        "setup_ai_model",
        return_value=("gemini", "gemini-3.5-flash", "mock_key"),
    ):
        with patch("mnemolink.wizard.query_llm_for_json", return_value=mock_llm_result):
            saved_path = wizard.create_lineage_ai()
            assert saved_path is not None
            assert (saved_path / "lineage.yaml").is_file()
            assert (saved_path / "card.json").is_file()

            raw_manifest = yaml.safe_load(
                (saved_path / "lineage.yaml").read_text("utf-8")
            )
            lineage = LineageProduct(**raw_manifest)
            assert lineage.id == "maritime_emergency_pilot"


# ==============================================================================
# 6. CLI Entrypoint Integration Tests
# ==============================================================================


def test_cli_wizard_command_invocation(monkeypatch, tmp_path):
    called = []

    def mock_run(self):
        called.append(self.base_output_dir)

    monkeypatch.setattr(MnemonicWizard, "run", mock_run)
    monkeypatch.setattr("sys.argv", ["mnemolink", "wizard", "--dir", str(tmp_path)])

    main()
    assert len(called) == 1
    assert called[0] == tmp_path.resolve()


def test_wizard_saves_to_canonical_memories_dir(tmp_path):
    """Ensure memories are saved to 'memories/', NOT 'memorys/'."""
    target_dir = tmp_path / "catalog_root"
    wizard = MnemonicWizard(output_dir=target_dir)

    manifest_data = {
        "id": "startup/test_incident",
        "name": "Test Incident",
        "version": "1.0.0",
        "domain": "startup",
        "memory_type": "incident",
        "summary": "Summary of incident",
        "episode_debrief": "Full debrief",
        "operational_scars": ["$10,000 lost"],
        "lessons_learned": ["Always verify"],
        "salience": 0.9,
    }
    card_data = {
        "id": "startup/test_incident",
        "name": "Test Incident",
        "kind": "memory",
        "domain": "startup",
        "version": "1.0.0",
        "summary": "Summary of incident",
    }

    saved = wizard._save_asset(
        "memory", "startup/test_incident", manifest_data, card_data
    )
    assert saved.is_dir()
    # Path must be target_dir / "memories" / "startup" / "test_incident"
    assert "memories" in saved.parts
    assert "memorys" not in saved.parts
    assert (saved / "memory.yaml").is_file()
    assert (saved / "card.json").is_file()


def test_discovery_resolves_both_memories_and_legacy_memorys(tmp_path):
    """Verify MnemonicResolver discovers assets in both memories/ and legacy memorys/."""
    from mnemolink.discovery import MnemonicResolver

    # 1. Setup canonical asset under memories/
    can_dir = tmp_path / "memories" / "robotics" / "stall_incident"
    can_dir.mkdir(parents=True)
    (can_dir / "memory.yaml").write_text(
        yaml.dump(
            {
                "id": "robotics/stall_incident",
                "name": "Stall Incident",
                "version": "1.0.0",
                "domain": "robotics",
                "memory_type": "incident",
                "episode_debrief": "Debrief of canonical stall",
                "operational_scars": ["1 airframe destroyed"],
                "lessons_learned": ["Dive on stall"],
            }
        ),
        encoding="utf-8",
    )

    # 2. Setup legacy asset under memorys/ (as created previously by typo)
    leg_dir = tmp_path / "memorys" / "startup" / "fundraising_disillusionment"
    leg_dir.mkdir(parents=True)
    (leg_dir / "memory.yaml").write_text(
        yaml.dump(
            {
                "id": "startup/fundraising_disillusionment",
                "name": "Fundraising Disillusionment",
                "version": "1.0.0",
                "domain": "startup",
                "memory_type": "incident",
                "episode_debrief": "Debrief of legacy disillusionment",
                "operational_scars": ["100 rejections"],
                "lessons_learned": ["Build cashflow"],
            }
        ),
        encoding="utf-8",
    )

    resolver = MnemonicResolver(custom_roots=[tmp_path])

    # Resolving canonical asset
    mem_can = resolver.find_memory("robotics/stall_incident")
    assert mem_can.id == "robotics/stall_incident"

    # Resolving legacy typo asset
    mem_leg = resolver.find_memory("startup/fundraising_disillusionment")
    assert mem_leg.id == "startup/fundraising_disillusionment"

    # Listing catalog discovers both
    catalog = resolver.list_catalog(kind="memory")
    found_ids = {c.id for c in catalog}
    assert "robotics/stall_incident" in found_ids
    assert "startup/fundraising_disillusionment" in found_ids


def test_preview_memory_rendering():
    """Verify that _preview_memory displays rich fields without errors."""
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)
    wizard = MnemonicWizard(console=console)

    sample_memory = {
        "id": "finance/bootstrapping_crucible",
        "name": "Bootstrapping Crucible",
        "domain": "finance",
        "memory_type": "incident",
        "salience": 0.95,
        "summary": "Summary of crucible",
        "episode_debrief": "Detailed narrative of cashflow emergency.",
        "operational_scars": ["$25,000 personal savings deployed"],
        "lessons_learned": ["Customer revenue precedes hiring"],
        "sensory_context": "Late night glowing terminal with zero bank balance.",
        "reflection": "Freedom from predatory venture capital is priceless.",
        "teleology": {
            "primary_goal": "achieve_profitability",
            "agent_drives": ["sovereignty", "truth_anchoring"],
            "applicable_needs": ["runway_planning"],
        },
        "tags": ["finance", "bootstrapping", "cashflow"],
    }

    wizard._preview_memory(sample_memory)
    rendered = buf.getvalue()
    assert "Bootstrapping Crucible" in rendered
    assert "$25,000 personal savings deployed" in rendered
    assert "Customer revenue precedes hiring" in rendered
    assert "Late night glowing terminal" in rendered
    assert "Freedom from predatory venture capital" in rendered
    assert "achieve_profitability" in rendered
    assert "#bootstrapping" in rendered


def test_preview_memory_rendering_positive_lore_no_scars():
    """Verify that _preview_memory correctly handles positive memories without scars."""
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)
    wizard = MnemonicWizard(console=console)

    sample_lore = {
        "id": "culinary/bougatsa_mastery",
        "name": "Bougatsa Phyllo Mastery",
        "domain": "culinary",
        "memory_type": "lore",
        "salience": 0.88,
        "summary": "Mastering the aerial stretching of translucent phyllo dough.",
        "episode_debrief": "Dawn practice under master baker Stefanos in Thessaloniki.",
        "operational_scars": [],
        "lessons_learned": [
            "Flour gluten structure responds to patience, not hurried force.",
            "Butter temperature must match ambient room humidity.",
        ],
        "sensory_context": "Sweet semolina custard aroma, warm clarified butter.",
        "reflection": "True craftsmanship is passed hand-to-hand across generations.",
        "teleology": {
            "primary_goal": "perfect_phyllo_translucency",
            "agent_drives": ["culinary_heritage", "artisan_discipline"],
            "applicable_needs": ["pastry_crafting"],
        },
        "tags": ["culinary", "heritage", "pastry"],
    }

    wizard._preview_memory(sample_lore)
    rendered = buf.getvalue()
    assert "Bougatsa Phyllo Mastery" in rendered
    assert "Dawn practice under master baker" in rendered
    assert "Flour gluten structure responds to patience" in rendered
    assert "Sweet semolina custard aroma" in rendered
    assert "True craftsmanship is passed" in rendered
    assert "Operational Scars" not in rendered


def test_wizard_create_memory_ai_positive_lore(tmp_path):
    """Verify AI authoring of positive lore memories without requiring operational scars."""
    target_dir = tmp_path / "scaffolds"
    buf = io.StringIO()
    console = Console(file=buf, force_terminal=False, width=120)

    mock_llm_result = {
        "manifest": {
            "id": "culinary/bougatsa_mastery",
            "name": "Bougatsa Phyllo Mastery",
            "version": "1.0.0",
            "domain": "culinary",
            "memory_type": "lore",
            "summary": "Mastering the aerial stretching of translucent phyllo dough.",
            "episode_debrief": (
                "Dawn apprenticeships in Ano Poli kneading semolina dough by hand."
            ),
            "operational_scars": [],
            "lessons_learned": [
                "Gluten strands require gentle cadence rather than brute force."
            ],
            "sensory_context": "Warm butter, powdered cinnamon, marble rolling tables.",
            "reflection": "Craft is an unbroken lineage of dedicated teachers.",
            "salience": 0.85,
            "author": "MnemoLink Wizard",
            "tags": ["culinary", "mastery", "lore"],
            "teleology": {
                "primary_goal": "pastry_perfection",
                "agent_drives": ["artisan_excellence"],
                "applicable_needs": ["baking_precision"],
            },
        },
        "card": {
            "id": "culinary/bougatsa_mastery",
            "name": "Bougatsa Phyllo Mastery",
            "kind": "memory",
            "domain": "culinary",
            "version": "1.0.0",
            "summary": "Mastering the aerial stretching of translucent phyllo dough.",
            "tags": ["culinary", "mastery", "lore"],
            "author": "MnemoLink Wizard",
            "teleology": {
                "primary_goal": "pastry_perfection",
                "agent_drives": ["artisan_excellence"],
                "applicable_needs": ["baking_precision"],
            },
            "chunks": ["story", "lessons", "reflection"],
        },
    }

    responses = iter(["Mastering authentic bougatsa pastry in Thessaloniki", "y"])

    wizard = MnemonicWizard(
        console=console,
        input_fn=lambda _: next(responses),
        output_dir=target_dir,
    )

    with patch.object(
        wizard,
        "setup_ai_model",
        return_value=("gemini", "gemini-3.5-flash", "mock_key"),
    ):
        with patch("mnemolink.wizard.query_llm_for_json", return_value=mock_llm_result):
            saved_path = wizard.create_memory_ai()
            assert saved_path is not None
            assert (saved_path / "memory.yaml").is_file()
            assert (saved_path / "card.json").is_file()

            raw_manifest = yaml.safe_load(
                (saved_path / "memory.yaml").read_text("utf-8")
            )
            mem = MemoryProduct(**raw_manifest)
            assert mem.memory_type == "lore"
            assert mem.domain == "culinary"
            assert mem.operational_scars == []
            assert len(mem.lessons_learned) == 1

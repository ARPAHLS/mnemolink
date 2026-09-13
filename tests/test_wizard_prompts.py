"""
Unit tests for MnemoLink AI Wizard dedicated system instructions and exemplars.
"""

from mnemolink.wizard_prompts import (
    get_lineage_system_instruction,
    get_memory_system_instruction,
    get_persona_system_instruction,
)


def _assert_zero_emojis(text: str):
    """Assert that text contains no Unicode emoji characters."""
    for char in text:
        code = ord(char)
        # Check standard emoji Unicode ranges
        if (
            (0x1F600 <= code <= 0x1F64F)
            or (0x1F300 <= code <= 0x1F5FF)
            or (0x1F680 <= code <= 0x1F6FF)
            or (0x2600 <= code <= 0x26FF)
            or (0x2700 <= code <= 0x27BF)
            or (0x1F900 <= code <= 0x1F9FF)
            or (0x1FA70 <= code <= 0x1FAFF)
        ):
            raise AssertionError(f"Emoji detected in text: '{char}' (U+{code:04X})")


def test_persona_system_instruction():
    """Verify persona system instruction structure, rules, and few-shot exemplars."""
    prompt = get_persona_system_instruction()
    assert isinstance(prompt, str)
    assert len(prompt) > 500

    # Format and schema requirements
    assert "'manifest'" in prompt
    assert "'card'" in prompt
    assert "core_philosophy" in prompt
    assert "axioms" in prompt
    assert "cognitive_priors" in prompt
    assert "self_narrative" in prompt
    assert "boundaries" in prompt
    assert "voice_tone" in prompt
    assert "teleology" in prompt

    # Gap-filling and extrapolation guidance
    assert "Extrapolate, Do Not Hardcode" in prompt
    assert "Archetype Alignment" in prompt

    # Few-shot exemplars across archetypes
    assert "EXEMPLAR 1: ARTISAN / CRAFT ARCHETYPE" in prompt
    assert "thessaloniki_master_baker" in prompt
    assert "EXEMPLAR 2: OPERATIONAL SENTINEL ARCHETYPE" in prompt
    assert "site_reliability_sentinel" in prompt
    assert "EXEMPLAR 3: SCHOLAR / MENTOR ARCHETYPE" in prompt
    assert "admiralty_juris_scholar" in prompt

    # Zero emoji enforcement
    _assert_zero_emojis(prompt)


def test_memory_system_instruction():
    """Verify memory system instruction covers 5 kinds, dynamic scars, and exemplars."""
    prompt = get_memory_system_instruction()
    assert isinstance(prompt, str)
    assert len(prompt) > 800

    # 5-kind taxonomy guidance
    for kind in ["lore", "work", "incident", "relational", "telemetry"]:
        assert f"'{kind}'" in prompt

    # Dynamic scar rule
    assert "DYNAMIC SCAR RULE" in prompt
    assert "empty list ([])" in prompt
    assert "NEVER force financial ruin" in prompt

    # Few-shot exemplars across all 5 kinds
    assert "EXEMPLAR 1: 'lore'" in prompt
    assert "bougatsa-aerial-phyllo" in prompt
    assert "EXEMPLAR 2: 'work'" in prompt
    assert "postgres-pool-hot-reload" in prompt
    assert "EXEMPLAR 3: 'incident'" in prompt
    assert "subsea-rov-net-entanglement" in prompt
    assert "EXEMPLAR 4: 'relational'" in prompt
    assert "security-audit-renewal" in prompt
    assert "EXEMPLAR 5: 'telemetry'" in prompt
    assert "wing-spar-acoustic-resonance" in prompt

    # Zero emoji enforcement
    _assert_zero_emojis(prompt)


def test_lineage_system_instruction():
    """Verify lineage system instruction covers causal bridges and progression arcs."""
    prompt = get_lineage_system_instruction()
    assert isinstance(prompt, str)
    assert len(prompt) > 600

    # Causal bridge and narrative methodology
    assert "CAUSAL BRIDGE METHODOLOGY" in prompt
    assert "associative causal bridges" in prompt
    assert "cumulative_narrative" in prompt
    assert "chronology" in prompt

    # Few-shot exemplars across developmental arcs
    assert "EXEMPLAR 1: ARTISAN MASTERY ARC" in prompt
    assert "thessaloniki_baking_evolution" in prompt
    assert "EXEMPLAR 2: ENGINEERING RESILIENCE ARC" in prompt
    assert "sre_resilience_architecture_evolution" in prompt

    # Zero emoji enforcement
    _assert_zero_emojis(prompt)

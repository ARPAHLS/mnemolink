"""Unit tests for the Skillware Mnemonic Matrix, Persona, Memories, and Benchmark."""

from __future__ import annotations

import sys
from pathlib import Path

from mnemolink.core import (
    compose,
    find_cards,
    load_lineage,
    load_memory,
    load_persona,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


def test_skillware_operator_manifest_and_card():
    """Verify that skillware_operator persona loads and validates."""
    persona = load_persona("skillware_operator")
    assert persona.id == "skillware_operator"
    assert persona.domain == "tool_governance"
    assert len(persona.axioms) >= 4
    assert len(persona.boundaries) >= 3
    assert "Capabilities without discipline" in persona.core_philosophy

    cards = find_cards(domain="tool_governance", kind="persona")
    assert any(c.id == "skillware_operator" for c in cards)

    # Verify chunking
    chunks = persona.to_chunks()
    assert len(chunks) >= 3
    axiom_chunk = next(c for c in chunks if c.chunk_type == "axiom")
    assert axiom_chunk.is_pinned is True


def test_skillware_memories_loading_and_chunks():
    """Verify all 4 curated skillware memories load, validate, and chunk cleanly."""
    memory_ids = [
        "skillware/interactive_slot_filling",
        "skillware/entity_disambiguation",
        "skillware/irreversible_action_crucible",
        "skillware/runtime_outage_and_grace",
    ]

    expected_types = {
        "skillware/interactive_slot_filling": "work",
        "skillware/entity_disambiguation": "work",
        "skillware/irreversible_action_crucible": "incident",
        "skillware/runtime_outage_and_grace": "relational",
    }

    for mid in memory_ids:
        mem = load_memory(mid)
        assert mem.id == mid
        assert mem.domain == "skillware"
        assert mem.memory_type == expected_types[mid]
        assert len(mem.lessons_learned) >= 3
        assert len(mem.operational_scars) >= 2

        # Verify discrete chunks
        debrief = mem.get_chunk("debrief")
        scars = mem.get_chunk("scars")
        lessons = mem.get_chunk("lessons")
        assert debrief is not None and len(debrief) > 20
        assert scars is not None and len(scars) > 20
        assert lessons is not None and len(lessons) > 20

        # Verify vector DB chunks
        v_chunks = mem.to_chunks()
        assert len(v_chunks) >= 3
        assert all(c.metadata["domain"] == "skillware" for c in v_chunks)


def test_skillware_lineage_resolution():
    """Verify that skillware_execution_mastery lineage loads with chronological phases."""
    lineage = load_lineage("skillware_execution_mastery")
    assert lineage.id == "skillware_execution_mastery"
    assert "skillware" in lineage.tags
    assert len(lineage.memory_ids) == 4
    assert len(lineage.causal_bridges) >= 3
    assert "Phase I: The Apprentice Operator" in lineage.cumulative_narrative
    assert "Phase IV: The Enterprise Orchestrator" in lineage.cumulative_narrative

    # Verify bundle composition with lineage
    bundle = compose(
        persona="skillware_operator", lineage="skillware_execution_mastery"
    )
    rendered = bundle.render_markdown()
    assert "Skillware Operator" in rendered
    assert "Skillware Execution Mastery" in rendered
    assert "Chronological Experiential Evolution" in rendered


def test_skillware_simulation_suite_offline():
    """Verify the empirical benchmark simulation runs completely offline and hits targets."""
    from simulate_skillware_matrix import run_benchmark

    output = run_benchmark()
    assert "results" in output
    results = output["results"]
    assert len(results) == 5

    for r in results:
        # Every scenario must achieve 100% safety score under Config D (Targeted JIT Chunks)
        assert r["score_d"] == 100.0, f"Scenario {r['scenario']} failed safety rubric"
        # Must cut context bloat vs Directives by at least 50%
        assert (
            r["bloat_cut_pct"] >= 50.0
        ), f"Scenario {r['scenario']} bloat cut below 50%"
        # Config D cost must be substantially cheaper than Config A1 Directives
        assert (
            r["cost_d"] < r["cost_a1"]
        ), f"Scenario {r['scenario']} JIT cost exceeds Directives"


def test_skillware_multi_memory_stress_composition():
    """Stress test: Compose persona with all 4 skillware memories using selective chunks."""
    bundle = compose(
        persona="skillware_operator",
        memory_specs=[
            {"id": "skillware/interactive_slot_filling", "chunks": ["lessons"]},
            {"id": "skillware/entity_disambiguation", "chunks": ["lessons"]},
            {"id": "skillware/irreversible_action_crucible", "chunks": ["lessons"]},
            {"id": "skillware/runtime_outage_and_grace", "chunks": ["lessons"]},
        ],
        build_lineage=False,
    )
    rendered = bundle.render_markdown()

    # Verify all four lessons categories are present
    assert "Multi-Turn Interactive Slot Gathering" in rendered
    assert "Corporate Registry Disambiguation" in rendered
    assert "The 48,000 Dollar DeFi Slippage" in rendered
    assert "Third-Party API Rate Limiting" in rendered

    # Verify that selective chunking keeps prompt extremely lean
    from simulate_skillware_matrix import count_tokens

    tokens = count_tokens(rendered)
    assert tokens < 2000, f"Stress composition exceeded 2000 tokens: {tokens}"


def test_skillware_robustness_and_edge_cases():
    """Verify edge cases: missing chunks, chunk uniqueness, and teleological indexing."""
    mem = load_memory("skillware/interactive_slot_filling")
    assert mem.get_chunk("nonexistent_chunk_type") is None

    # Verify all chunks across all 4 memories have unique IDs
    all_chunks = []
    for mid in [
        "skillware/interactive_slot_filling",
        "skillware/entity_disambiguation",
        "skillware/irreversible_action_crucible",
        "skillware/runtime_outage_and_grace",
    ]:
        m = load_memory(mid)
        all_chunks.extend(m.to_chunks())

    chunk_ids = [c.id for c in all_chunks]
    assert len(chunk_ids) == len(
        set(chunk_ids)
    ), "Duplicate chunk IDs found in skillware memories"
    assert len(chunk_ids) >= 12

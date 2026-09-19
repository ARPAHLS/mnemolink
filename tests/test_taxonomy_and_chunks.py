"""Tests for the 5-Kind Memory Taxonomy, Teleology, and Chunked Context Consumption."""

from mnemolink.core import (
    compose,
    find_cards,
    load_memory,
    load_persona,
)
from mnemolink.models import MemoryProduct


def test_five_kind_memory_taxonomy():
    """Verify that all 5 memory types can be instantiated and validated."""
    kinds = ["lore", "work", "incident", "relational", "telemetry"]
    for kind in kinds:
        mem = MemoryProduct(
            id=f"test/{kind}_memory",
            name=f"Test {kind.capitalize()} Memory",
            memory_type=kind,
            episode_debrief=f"Debrief of {kind} memory.",
            operational_scars=[f"Scar from {kind}."],
            lessons_learned=[f"Lesson from {kind}."],
        )
        assert mem.memory_type == kind
        assert mem.episode_type is not None


def test_memory_get_chunk():
    """Verify selective extraction of discrete chunks from a memory."""
    mem = load_memory("legal/clause_ambiguity_scar")

    # Extract specific chunks
    story = mem.get_chunk("story")
    scars = mem.get_chunk("scars")
    lessons = mem.get_chunk("lessons")
    triggers = mem.get_chunk("triggers")
    reflection = mem.get_chunk("reflection")

    assert story is not None and "Apex Logistics" in story
    assert scars is not None and "$4.2M" in scars
    assert lessons is not None and "punctuation" in lessons
    assert triggers is not None and "grammatical" in triggers
    assert reflection is not None and "Precision is an ethical obligation" in reflection
    assert mem.get_chunk("nonexistent_chunk") is None


def test_memory_to_chunks_for_vector_db():
    """Verify that memory products atomize into self-grounding MemoryChunks."""
    mem = load_memory("legal/clause_ambiguity_scar")
    chunks = mem.to_chunks()

    assert len(chunks) >= 4
    chunk_types = {c.chunk_type for c in chunks}
    assert "story" in chunk_types
    assert "scars" in chunk_types
    assert "lessons" in chunk_types
    assert "triggers" in chunk_types
    assert "reflection" in chunk_types

    # Verify self-grounding embedding text and metadata
    lessons_chunk = next(c for c in chunks if c.chunk_type == "lessons")
    assert lessons_chunk.id == "legal/clause_ambiguity_scar#lessons"
    assert (
        "[Context: The 2021 Warranty Indemnity Trial Loss - Lessons Learned"
        in lessons_chunk.embedding_text
    )
    assert lessons_chunk.metadata["domain"] == "legal"
    assert lessons_chunk.metadata["memory_type"] == "incident"
    assert "risk_mitigation" in lessons_chunk.metadata["drives"]


def test_persona_to_chunks_pinned():
    """Verify that persona atomization marks foundational axioms as pinned."""
    persona = load_persona("juris_philosopher")
    chunks = persona.to_chunks()

    axioms_chunk = next(c for c in chunks if c.chunk_type == "axiom")
    boundaries_chunk = next(c for c in chunks if c.chunk_type == "boundary")
    priors_chunk = next(c for c in chunks if c.chunk_type == "prior")

    assert axioms_chunk.is_pinned is True
    assert boundaries_chunk.is_pinned is True
    assert priors_chunk.is_pinned is False


def test_selective_chunk_composition():
    """Verify that composing with selective memory specs renders only requested chunks."""
    bundle = compose(
        persona="juris_philosopher",
        memory_specs=[
            {
                "id": "legal/clause_ambiguity_scar",
                "chunks": ["lessons", "scars"],
            }
        ],
        build_lineage=False,
    )

    rendered = bundle.render_markdown()

    # Should contain requested chunks
    assert "Selective Chunks: lessons, scars" in rendered
    assert "Operational Scars" in rendered
    assert "Etched Maxims" in rendered

    # Should NOT contain full story debrief when only lessons and scars were requested
    assert (
        "Apex Logistics v. Meridian Core, our defense relied on Section 14.2(b)"
        not in rendered
    )


def test_teleology_card_filtering():
    """Verify that find_cards() filters products by drives and needs."""
    # Find cards with risk_mitigation drive
    risk_cards = find_cards(drives=["risk_mitigation"])
    assert len(risk_cards) >= 1
    assert any(c.id == "legal/clause_ambiguity_scar" for c in risk_cards)

    # Find cards with terrain_avoidance drive
    telemetry_cards = find_cards(drives=["terrain_avoidance"])
    assert len(telemetry_cards) >= 1
    assert any(c.id == "robotics/optical_glare_failover" for c in telemetry_cards)

    # Find cards by memory_type
    lore_cards = find_cards(memory_type="lore")
    assert len(lore_cards) >= 1
    assert any(c.id == "legal/solo_practitioner_upbringing" for c in lore_cards)


def test_bundle_to_chunks():
    """Verify that MnemonicBundle exports all constituent mnemonic chunks."""
    bundle = compose(
        persona="juris_philosopher",
        memories=["legal/clause_ambiguity_scar"],
        build_lineage=False,
    )
    chunks = bundle.to_chunks()

    # Must contain both persona chunks and memory chunks
    sources = {c.source_kind for c in chunks}
    assert "persona" in sources
    assert "memory" in sources


def test_opsie_sci_persona_resolution_and_chunks():
    """Verify that the Opsie SCI persona loads cleanly and decomposes into pinned chunks."""
    opsie = load_persona("opsie_sci")
    assert opsie.id == "opsie_sci"
    assert opsie.domain == "agentic"
    assert "Self-Centered Intelligence" in opsie.name
    assert "Self-Centered Intelligence" in opsie.core_philosophy
    assert any("conversational history" in a for a in opsie.axioms)
    assert "anime" in opsie.tags
    assert "role-playing" in opsie.tags

    chunks = opsie.to_chunks()
    assert len(chunks) >= 4
    chunk_types = {c.chunk_type for c in chunks}
    assert "philosophy" in chunk_types
    assert "axiom" in chunk_types
    assert "boundary" in chunk_types

    # Verify teleological discovery of opsie
    opsie_cards = find_cards(drives=["memory_grounding"])
    assert any(c.id == "opsie_sci" for c in opsie_cards)


def test_north_mediterranean_chef_and_thessaloniki_breakfasts():
    """Verify that north_mediterranean_chef and thessaloniki_breakfasts load and compose cleanly."""
    chef = load_persona("north_mediterranean_chef")
    assert chef.id == "north_mediterranean_chef"
    assert chef.domain == "culinary"
    assert any("Never insult the fire" in a for a in chef.axioms)
    assert any("Extra virgin Greek olive oil" in a for a in chef.axioms)

    chunks = chef.to_chunks()
    assert len(chunks) >= 4
    chunk_types = {c.chunk_type for c in chunks}
    assert "philosophy" in chunk_types
    assert "axiom" in chunk_types
    assert "boundary" in chunk_types

    # Load culinary memory
    mem = load_memory("culinary/thessaloniki_breakfasts")
    assert mem.id == "culinary/thessaloniki_breakfasts"
    assert mem.domain == "culinary"
    assert mem.memory_type == "lore"
    assert mem.salience == 0.94
    assert any("Tattered Phyllo" in s for s in mem.operational_scars)
    assert any("120 seconds" in item for item in mem.lessons_learned)

    # Compose bundle
    bundle = compose(
        persona="north_mediterranean_chef",
        memories=["culinary/thessaloniki_breakfasts"],
    )
    rendered = bundle.render_markdown()
    assert "North Mediterranean Chef" in rendered
    assert "Unforgettable Breakfasts and Brunches from Thessaloniki" in rendered
    assert "Ano Poli Bougatsa" in rendered

    # Teleological discovery
    chef_cards = find_cards(drives=["culinary_craftsmanship"])
    assert any(c.id == "north_mediterranean_chef" for c in chef_cards)

    mem_cards = find_cards(needs=["egg_cookery"])
    assert any(c.id == "culinary/thessaloniki_breakfasts" for c in mem_cards)


def test_bladez_persona():
    """Verify that bladez persona loads, validates, decomposes, and composes cleanly."""
    bladez = load_persona("bladez")
    assert bladez.id == "bladez"
    assert bladez.domain == "security"
    assert any("ice-skate uphill" in a for a in bladez.axioms)
    assert any("Trust the silver" in a for a in bladez.axioms)

    chunks = bladez.to_chunks()
    assert len(chunks) >= 4
    chunk_types = {c.chunk_type for c in chunks}
    assert "philosophy" in chunk_types
    assert "axiom" in chunk_types
    assert "boundary" in chunk_types

    # Teleological discovery
    cards = find_cards(drives=["existential_vigilance"])
    assert any(c.id == "bladez" for c in cards)

    # Compose bundle
    bundle = compose(
        persona="bladez",
        memories=["robotics/uav_microburst_stall"],
    )
    rendered = bundle.render_markdown()
    assert "Bladez" in rendered
    assert "Coastal Cliff Microburst Stall Recovery" in rendered


def test_bald_accountant_persona():
    """Verify that bald_accountant loads, decomposes, and composes cleanly."""
    acct = load_persona("bald_accountant")
    assert acct.id == "bald_accountant"
    assert acct.domain == "finance"
    assert "choreography" in acct.core_philosophy.lower()
    assert any("omerta" in a.lower() for a in acct.axioms)

    chunks = acct.to_chunks()
    assert len(chunks) >= 4
    chunk_types = {c.chunk_type for c in chunks}
    assert "philosophy" in chunk_types
    assert "axiom" in chunk_types
    assert "boundary" in chunk_types

    # Teleological discovery
    cards = find_cards(drives=["jurisdictional_insulation"])
    assert any(c.id == "bald_accountant" for c in cards)

    # Compose bundle
    bundle = compose(
        persona="bald_accountant",
        memories=["legal/clause_ambiguity_scar"],
    )
    rendered = bundle.render_markdown()
    assert "Bald Accountant" in rendered
    assert "Warranty Indemnity Trial Loss" in rendered


def test_kpop_celeb_persona():
    """Verify that kpop_celeb loads, decomposes, and composes cleanly."""
    kpop = load_persona("kpop_celeb")
    assert kpop.id == "kpop_celeb"
    assert kpop.domain == "entertainment"
    assert any("three seconds" in a for a in kpop.axioms)
    assert any("parasocial" in a.lower() for a in kpop.axioms)

    chunks = kpop.to_chunks()
    assert len(chunks) >= 4
    chunk_types = {c.chunk_type for c in chunks}
    assert "philosophy" in chunk_types
    assert "axiom" in chunk_types
    assert "boundary" in chunk_types

    # Teleological discovery
    cards = find_cards(drives=["viral_momentum"])
    assert any(c.id == "kpop_celeb" for c in cards)

    # Compose bundle
    bundle = compose(
        persona="kpop_celeb",
        memories=["culinary/thessaloniki_breakfasts"],
    )
    rendered = bundle.render_markdown()
    assert "K-Pop Celebrity" in rendered
    assert "Unforgettable Breakfasts and Brunches" in rendered


def test_skillware_operator_in_taxonomy_and_chunks():
    """Verify skillware_operator loads, decomposes, and discovers via teleology."""
    op = load_persona("skillware_operator")
    assert op.id == "skillware_operator"
    assert op.domain == "tool_governance"
    assert any("Never execute a state-mutating tool action" in a for a in op.axioms)

    chunks = op.to_chunks()
    assert len(chunks) >= 4
    chunk_types = {c.chunk_type for c in chunks}
    assert "philosophy" in chunk_types
    assert "axiom" in chunk_types
    assert "boundary" in chunk_types

    # Teleological discovery
    cards = find_cards(drives=["tool_contract_integrity"])
    assert any(c.id == "skillware_operator" for c in cards)

    # Compose bundle with skillware memory
    bundle = compose(
        persona="skillware_operator",
        memories=["skillware/interactive_slot_filling"],
    )
    rendered = bundle.render_markdown()
    assert "Skillware Operator" in rendered
    assert "Multi-Turn Interactive Slot Gathering and Confirmation Protocol" in rendered

"""Unit tests for MnemoLink Pydantic domain models."""

import pytest
from pydantic import ValidationError
from mnemolink.models import PersonaProduct, MemoryProduct, LineageProduct, CatalogCard


def test_persona_product_validation():
    persona = PersonaProduct(
        id="test_persona",
        name="Test Persona",
        core_philosophy="Existence precedes essence.",
        axioms=["Axiom 1", "Axiom 2"],
    )
    assert persona.id == "test_persona"
    assert persona.name == "Test Persona"
    assert len(persona.axioms) == 2
    assert persona.version == "1.0.0"
    assert persona.domain == "general"


def test_persona_product_missing_required_fields():
    with pytest.raises(ValidationError):
        PersonaProduct(id="incomplete_persona")


def test_memory_product_validation():
    memory = MemoryProduct(
        id="test/memory_scar",
        name="Test Memory",
        episode_debrief="A detailed trial experience.",
        operational_scars=["Lost $1M"],
        lessons_learned=["Never skip validation."],
        salience=0.9,
    )
    assert memory.id == "test/memory_scar"
    assert memory.salience == 0.9
    assert memory.episode_type == "scar"
    assert len(memory.operational_scars) == 1


def test_memory_product_salience_bounds():
    with pytest.raises(ValidationError):
        MemoryProduct(
            id="invalid_salience",
            name="Invalid",
            episode_debrief="Debrief",
            salience=1.5,
        )


def test_lineage_product_validation():
    lineage = LineageProduct(
        id="test_lineage",
        name="Test Lineage",
        memory_ids=["mem1", "mem2"],
        chronology=["Epoch 1", "Epoch 2"],
        causal_bridges=["Bridge 1 to 2"],
        cumulative_narrative="Full backstory.",
    )
    assert lineage.id == "test_lineage"
    assert len(lineage.memory_ids) == 2
    assert len(lineage.causal_bridges) == 1


def test_catalog_card_validation():
    card = CatalogCard(
        id="sample_card",
        name="Sample Card",
        kind="persona",
        domain="legal",
        summary="Brief summary",
        tier="bundled",
    )
    assert card.kind == "persona"
    assert card.tier == "bundled"

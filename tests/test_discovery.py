"""Unit tests for MnemoLink discovery and 3-tier resolution engine."""

import pytest
from mnemolink.discovery import MnemonicResolver, get_bundled_catalog_root


def test_bundled_catalog_root_exists():
    root = get_bundled_catalog_root()
    assert root.is_dir()
    assert (root / "personas").is_dir()
    assert (root / "memories").is_dir()
    assert (root / "lineages").is_dir()


def test_resolve_bundled_persona():
    resolver = MnemonicResolver()
    persona = resolver.find_persona("juris_philosopher")
    assert persona.id == "juris_philosopher"
    assert "mutual intent" in persona.core_philosophy.lower()
    assert len(persona.axioms) > 0


def test_resolve_bundled_memory():
    resolver = MnemonicResolver()
    mem = resolver.find_memory("legal/clause_ambiguity_scar")
    assert mem.id == "legal/clause_ambiguity_scar"
    assert "semicolon" in mem.episode_debrief.lower()
    assert len(mem.operational_scars) > 0


def test_resolve_bundled_lineage():
    resolver = MnemonicResolver()
    lin = resolver.find_lineage("legal_crucible")
    assert lin.id == "legal_crucible"
    assert len(lin.memory_ids) >= 2
    assert len(lin.causal_bridges) >= 1


def test_list_catalog():
    resolver = MnemonicResolver()
    all_items = resolver.list_catalog()
    assert len(all_items) >= 5

    personas = resolver.list_catalog(kind="persona")
    assert all(c.kind == "persona" for c in personas)
    assert any(c.id == "juris_philosopher" for c in personas)

    memories = resolver.list_catalog(kind="memory")
    assert all(c.kind == "memory" for c in memories)
    assert any(c.id == "legal/clause_ambiguity_scar" for c in memories)


def test_nonexistent_product_raises_error():
    resolver = MnemonicResolver()
    with pytest.raises(FileNotFoundError):
        resolver.find_persona("non_existent_persona_xyz")

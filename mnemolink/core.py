"""Main entrypoint and orchestration facade for MnemoLink.

Provides high-level ergonomics for loading, composing, filtering,
and injecting mnemonic products.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from mnemolink.adapters import MnemonicBundle
from mnemolink.discovery import MnemonicResolver
from mnemolink.lineage import LineageBuilder
from mnemolink.models import CatalogCard, LineageProduct, MemoryProduct, PersonaProduct


class MnemoLinkEngine:
    """Core runtime engine for loading, discovering, and synthesizing mnemonic products."""

    def __init__(self, custom_roots: Optional[List[Path]] = None):
        self.resolver = MnemonicResolver(custom_roots=custom_roots)

    def load_persona(
        self, identifier: Union[str, Path, PersonaProduct]
    ) -> PersonaProduct:
        """Resolve and load a PersonaProduct by ID, path, or passthrough."""
        if isinstance(identifier, PersonaProduct):
            return identifier
        return self.resolver.find_persona(str(identifier))

    def load_memory(self, identifier: Union[str, Path, MemoryProduct]) -> MemoryProduct:
        """Resolve and load a MemoryProduct by ID, path, or passthrough."""
        if isinstance(identifier, MemoryProduct):
            return identifier
        return self.resolver.find_memory(str(identifier))

    def load_lineage(
        self, identifier: Union[str, Path, LineageProduct]
    ) -> LineageProduct:
        """Resolve and load a LineageProduct by ID, path, or passthrough."""
        if isinstance(identifier, LineageProduct):
            return identifier
        return self.resolver.find_lineage(str(identifier))

    def list_catalog(self, kind: Optional[str] = None) -> List[CatalogCard]:
        """List available personas, memories, and lineages across the search hierarchy."""
        return self.resolver.list_catalog(kind=kind)

    def find_cards(
        self,
        kind: Optional[str] = None,
        domain: Optional[str] = None,
        memory_type: Optional[str] = None,
        drives: Optional[List[str]] = None,
        needs: Optional[List[str]] = None,
    ) -> List[CatalogCard]:
        """Query catalog presentation cards based on kind, domain, memory_type, or teleology."""
        return self.resolver.find_cards(
            kind=kind,
            domain=domain,
            memory_type=memory_type,
            drives=drives,
            needs=needs,
        )

    def build_lineage(
        self,
        memories: List[Union[str, Path, MemoryProduct]],
        persona: Optional[Union[str, Path, PersonaProduct]] = None,
        lineage_id: str = "dynamic_lineage",
        name: str = "Synthesized Lineage",
    ) -> LineageProduct:
        """Dynamically assemble a lego-brick Lineage from an ordered list of memories."""
        loaded_memories = [self.load_memory(m) for m in memories]
        loaded_persona = self.load_persona(persona) if persona else None
        builder = LineageBuilder(persona=loaded_persona)
        return builder.build(loaded_memories, lineage_id=lineage_id, name=name)

    def compose(
        self,
        persona: Optional[Union[str, Path, PersonaProduct]] = None,
        memories: Optional[
            List[Union[str, Path, MemoryProduct, Dict[str, Any]]]
        ] = None,
        memory_specs: Optional[List[Dict[str, Any]]] = None,
        lineage: Optional[Union[str, Path, LineageProduct]] = None,
        build_lineage: bool = True,
    ) -> MnemonicBundle:
        """Compose a Persona, Memories, and Lineage into an integrated MnemonicBundle.

        Supports both monolithic assembly (all memories in full) and selective
        chunking (e.g. memory_specs=[{"id": "legal/scar", "chunks": ["lessons"]}]).

        Args:
            persona: Persona identifier, path, or instance.
            memories: List of memory identifiers, paths, instances, or spec dicts.
            memory_specs: Optional list of granular memory specs with chunk selections.
            lineage: Optional pre-existing Lineage. If omitted and build_lineage is True,
                     memories are automatically synthesized into a dynamic lego lineage.
            build_lineage: If True and memories are provided without a lineage, dynamically
                           constructs a coherent causal lineage narrative.

        Returns:
            A compiled MnemonicBundle with universal model adapter methods.
        """
        resolved_persona = self.load_persona(persona) if persona else None

        raw_memory_inputs: List[Any] = []
        selected_chunks: Dict[str, List[str]] = {}

        # Handle memory_specs parameter if supplied
        if memory_specs:
            for spec in memory_specs:
                m_id = spec.get("id") or spec.get("memory_id")
                if m_id:
                    raw_memory_inputs.append(m_id)
                    chunks = spec.get("chunks")
                    if chunks:
                        selected_chunks[str(m_id)] = chunks

        # Handle memories parameter
        if memories:
            for m in memories:
                if isinstance(m, dict):
                    m_id = m.get("id") or m.get("memory_id")
                    if m_id:
                        raw_memory_inputs.append(m_id)
                        chunks = m.get("chunks")
                        if chunks:
                            selected_chunks[str(m_id)] = chunks
                else:
                    raw_memory_inputs.append(m)

        resolved_memories: List[MemoryProduct] = []
        for raw_m in raw_memory_inputs:
            mem = self.load_memory(raw_m)
            resolved_memories.append(mem)

        resolved_lineage = self.load_lineage(lineage) if lineage else None

        if resolved_memories and not resolved_lineage and build_lineage:
            builder = LineageBuilder(persona=resolved_persona)
            resolved_lineage = builder.build(
                resolved_memories,
                lineage_id=f"lineage_{resolved_persona.id if resolved_persona else 'composite'}",
                name=(
                    f"Lineage of {resolved_persona.name}"
                    if resolved_persona
                    else "Synthesized Experiential Lineage"
                ),
            )

        return MnemonicBundle(
            persona=resolved_persona,
            memories=resolved_memories,
            lineage=resolved_lineage,
            selected_chunks=selected_chunks,
        )


# Global default engine instance for top-level convenience functions
_DEFAULT_ENGINE = MnemoLinkEngine()


def compose(
    persona: Optional[Union[str, Path, PersonaProduct]] = None,
    memories: Optional[List[Union[str, Path, MemoryProduct, Dict[str, Any]]]] = None,
    memory_specs: Optional[List[Dict[str, Any]]] = None,
    lineage: Optional[Union[str, Path, LineageProduct]] = None,
    build_lineage: bool = True,
) -> MnemonicBundle:
    """Top-level convenience function to compose a MnemonicBundle."""
    return _DEFAULT_ENGINE.compose(
        persona=persona,
        memories=memories,
        memory_specs=memory_specs,
        lineage=lineage,
        build_lineage=build_lineage,
    )


def load_persona(identifier: Union[str, Path, PersonaProduct]) -> PersonaProduct:
    """Top-level convenience function to load a PersonaProduct."""
    return _DEFAULT_ENGINE.load_persona(identifier)


def load_memory(identifier: Union[str, Path, MemoryProduct]) -> MemoryProduct:
    """Top-level convenience function to load a MemoryProduct."""
    return _DEFAULT_ENGINE.load_memory(identifier)


def load_lineage(identifier: Union[str, Path, LineageProduct]) -> LineageProduct:
    """Top-level convenience function to load a LineageProduct."""
    return _DEFAULT_ENGINE.load_lineage(identifier)


def build_lineage(
    memories: List[Union[str, Path, MemoryProduct]],
    persona: Optional[Union[str, Path, PersonaProduct]] = None,
    lineage_id: str = "dynamic_lineage",
    name: str = "Synthesized Lineage",
) -> LineageProduct:
    """Top-level convenience function to build a dynamic lego Lineage."""
    return _DEFAULT_ENGINE.build_lineage(
        memories=memories, persona=persona, lineage_id=lineage_id, name=name
    )


def list_catalog(kind: Optional[str] = None) -> List[CatalogCard]:
    """Top-level convenience function to list available products."""
    return _DEFAULT_ENGINE.list_catalog(kind=kind)


def find_cards(
    kind: Optional[str] = None,
    domain: Optional[str] = None,
    memory_type: Optional[str] = None,
    drives: Optional[List[str]] = None,
    needs: Optional[List[str]] = None,
) -> List[CatalogCard]:
    """Top-level convenience function to search catalog cards by domain, type, or teleology."""
    return _DEFAULT_ENGINE.find_cards(
        kind=kind,
        domain=domain,
        memory_type=memory_type,
        drives=drives,
        needs=needs,
    )

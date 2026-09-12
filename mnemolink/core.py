"""Main entrypoint and orchestration facade for MnemoLink.

Provides high-level ergonomics for loading, composing, and injecting mnemonic products.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Union

from mnemolink.adapters import MnemonicBundle
from mnemolink.discovery import MnemonicResolver
from mnemolink.lineage import LineageBuilder
from mnemolink.models import CatalogCard, LineageProduct, MemoryProduct, PersonaProduct


class MnemoLinkEngine:
    """Core runtime engine for loading and synthesizing mnemonic products."""

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
        memories: Optional[List[Union[str, Path, MemoryProduct]]] = None,
        lineage: Optional[Union[str, Path, LineageProduct]] = None,
        build_lineage: bool = True,
    ) -> MnemonicBundle:
        """Compose a Persona, Memories, and Lineage into an integrated MnemonicBundle.

        Args:
            persona: Persona identifier, path, or instance.
            memories: List of memory identifiers, paths, or instances.
            lineage: Optional pre-existing Lineage. If omitted and build_lineage is True,
                     memories are automatically synthesized into a dynamic lego lineage.
            build_lineage: If True and memories are provided without a lineage, dynamically
                           constructs a coherent causal lineage narrative.

        Returns:
            A compiled MnemonicBundle with universal model adapter methods.
        """
        resolved_persona = self.load_persona(persona) if persona else None
        resolved_memories = [self.load_memory(m) for m in (memories or [])]
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
        )


# Global default engine instance for top-level convenience functions
_DEFAULT_ENGINE = MnemoLinkEngine()


def compose(
    persona: Optional[Union[str, Path, PersonaProduct]] = None,
    memories: Optional[List[Union[str, Path, MemoryProduct]]] = None,
    lineage: Optional[Union[str, Path, LineageProduct]] = None,
    build_lineage: bool = True,
) -> MnemonicBundle:
    """Top-level convenience function to compose a MnemonicBundle."""
    return _DEFAULT_ENGINE.compose(
        persona=persona,
        memories=memories,
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

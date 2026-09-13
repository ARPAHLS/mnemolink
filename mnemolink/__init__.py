"""MnemoLink: Lightweight Framework & Registry for Mnemonic Products.

Serving the mnemonic industry for information processors:
AI agents, UAVs, edge robotics, smart appliances, and brain-machine interfaces.
"""

from __future__ import annotations

from mnemolink.adapters import MnemonicBundle
from mnemolink.core import (
    MnemoLinkEngine,
    build_lineage,
    compose,
    find_cards,
    list_catalog,
    load_lineage,
    load_memory,
    load_persona,
)
from mnemolink.discovery import DiscoveryTier, MnemonicResolver
from mnemolink.lineage import LineageBuilder
from mnemolink.models import (
    CatalogCard,
    ChunkType,
    LineageProduct,
    MemoryChunk,
    MemoryKind,
    MemoryProduct,
    PersonaProduct,
    Teleology,
)

# Friendly alias for engine class
MnemoLink = MnemoLinkEngine

__version__ = "0.2.2"
__all__ = [
    "__version__",
    "MnemoLink",
    "MnemoLinkEngine",
    "MnemonicBundle",
    "PersonaProduct",
    "MemoryProduct",
    "LineageProduct",
    "CatalogCard",
    "MemoryChunk",
    "Teleology",
    "MemoryKind",
    "ChunkType",
    "DiscoveryTier",
    "MnemonicResolver",
    "LineageBuilder",
    "compose",
    "load_persona",
    "load_memory",
    "load_lineage",
    "build_lineage",
    "list_catalog",
    "find_cards",
]

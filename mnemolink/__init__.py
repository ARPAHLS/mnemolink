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
    list_catalog,
    load_lineage,
    load_memory,
    load_persona,
)
from mnemolink.discovery import DiscoveryTier, MnemonicResolver
from mnemolink.lineage import LineageBuilder
from mnemolink.models import (
    CatalogCard,
    LineageProduct,
    MemoryProduct,
    PersonaProduct,
)

# Friendly alias for engine class
MnemoLink = MnemoLinkEngine

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "MnemoLink",
    "MnemoLinkEngine",
    "MnemonicBundle",
    "PersonaProduct",
    "MemoryProduct",
    "LineageProduct",
    "CatalogCard",
    "DiscoveryTier",
    "MnemonicResolver",
    "LineageBuilder",
    "compose",
    "load_persona",
    "load_memory",
    "load_lineage",
    "build_lineage",
    "list_catalog",
]

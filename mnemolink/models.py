"""Typed domain models for MnemoLink mnemonic products.

Defines schemas for Personas, Memories, Lineages, and compiled MnemonicBundles.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PersonaProduct(BaseModel):
    """A foundational philosophical and behavioral template for an information processor.

    Rather than superficial roleplay directives ('You are a pirate'), a Persona encodes
    the philosophical axioms, epistemological anchors, cognitive priors, and self-narrative
    that organically generate authentic, resilient behavior.
    """

    id: str = Field(..., description="Unique slug or category/slug identifier")
    name: str = Field(..., description="Human-readable title of the persona")
    version: str = Field(default="1.0.0", description="Semantic version string")
    domain: str = Field(
        default="general", description="Application domain (legal, robotics, etc.)"
    )
    summary: str = Field(default="", description="Brief description of the persona")
    core_philosophy: str = Field(
        ...,
        description="Bedrock worldview and epistemic stance on reality, duty, truth, and action",
    )
    axioms: List[str] = Field(
        default_factory=list,
        description="Inviolable principles and cognitive anchors guiding choices",
    )
    cognitive_priors: List[str] = Field(
        default_factory=list,
        description="Default intuition biases when interpreting ambiguous or conflicting data",
    )
    self_narrative: str = Field(
        default="",
        description="Internal self-perception and formative tone (how the persona views itself)",
    )
    boundaries: List[str] = Field(
        default_factory=list,
        description="Hard operational and ethical boundaries the persona will organically reject",
    )
    voice_tone: str = Field(
        default="",
        description="Linguistic register, pacing, and style (e.g., measured, terse, empathetic)",
    )
    author: str = Field(
        default="ARPA Hellenic Logical Systems", description="Creator or provenance"
    )
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary extension metadata"
    )


class MemoryProduct(BaseModel):
    """An episodic memory, operational scar, or digital-twin experience.

    Encodes real or synthetic experiential scars that grant deep domain intuition,
    lessons learned from costly errors, and tactile operational context.
    """

    id: str = Field(..., description="Unique slug or domain/slug identifier")
    name: str = Field(..., description="Human-readable title of the memory episode")
    version: str = Field(default="1.0.0", description="Semantic version string")
    domain: str = Field(default="general", description="Application domain")
    episode_type: str = Field(
        default="scar",
        description="Type of episode: scar, breakthrough, operational_intuition, formative_event",
    )
    summary: str = Field(default="", description="High-level synopsis of what occurred")
    episode_debrief: str = Field(
        ...,
        description="First-person or digital-twin debrief detailing the exact event and aftermath",
    )
    operational_scars: List[str] = Field(
        default_factory=list,
        description="Concrete damages, losses, or systemic failures endured during the episode",
    )
    lessons_learned: List[str] = Field(
        default_factory=list,
        description="Distilled, immutable maxims etched into operational memory from this episode",
    )
    sensory_context: Optional[str] = Field(
        default=None,
        description="Physical or sensor-telemetry context (wind, voltage, tension, noise)",
    )
    salience: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Experiential weight coefficient (0.0=trivial, 1.0=identity-defining)",
    )
    author: str = Field(
        default="ARPA Hellenic Logical Systems", description="Creator or provenance"
    )
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary extension metadata"
    )


class LineageProduct(BaseModel):
    """A chronological sequence of chained episodic memories with dynamic causal bridges.

    Lineages act like lego towers of experience, connecting discrete scars and triumphs
    into a coherent historical narrative that grounds an agent's long-term identity.
    """

    id: str = Field(..., description="Unique slug or category/slug identifier")
    name: str = Field(..., description="Human-readable title of the lineage")
    version: str = Field(default="1.0.0", description="Semantic version string")
    summary: str = Field(
        default="", description="Synopsis of the historical progression"
    )
    memory_ids: List[str] = Field(
        default_factory=list,
        description="Ordered list of Memory IDs forming the spine of this lineage",
    )
    chronology: List[str] = Field(
        default_factory=list,
        description="Time markers or sequence labels corresponding to memory steps",
    )
    causal_bridges: List[str] = Field(
        default_factory=list,
        description="Narrative connective tissue explaining how one episode evolved into the next",
    )
    cumulative_narrative: str = Field(
        default="",
        description="Synthesized unified backstory uniting all memories in the sequence",
    )
    author: str = Field(
        default="ARPA Hellenic Logical Systems", description="Creator or provenance"
    )
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary extension metadata"
    )


class CatalogCard(BaseModel):
    """Catalog presentation and marketplace metadata for browsing UI and tools."""

    id: str
    name: str
    kind: str = Field(..., description="'persona', 'memory', or 'lineage'")
    domain: str
    summary: str
    version: str = "1.0.0"
    tags: List[str] = Field(default_factory=list)
    tier: str = Field(default="bundled", description="'bundled', 'user', or 'project'")
    path: str = Field(default="", description="Filesystem location")

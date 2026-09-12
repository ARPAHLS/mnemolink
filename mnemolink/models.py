"""Typed domain models for MnemoLink mnemonic products.

Defines schemas for Personas, Memories, Lineages, CatalogCards,
Teleology (goals & drives), and atomic MemoryChunks (mnemonic chunks).
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field, model_validator

MemoryKind = Literal["lore", "work", "incident", "relational", "telemetry"]
ChunkType = Literal["story", "scars", "lessons", "triggers", "reflection"]


class Teleology(BaseModel):
    """The motivational, intentional, and teleological layer of a mnemonic product.

    Explains the agent's goals, underlying psychological/operational drives,
    and applicable operational needs during an experiential episode.
    """

    primary_goal: Optional[str] = Field(
        default=None,
        description="The primary objective the agent was actively pursuing during this episode",
    )
    agent_drives: List[str] = Field(
        default_factory=list,
        description="Core motivational drivers at play (e.g. risk_mitigation, survival)",
    )
    applicable_needs: List[str] = Field(
        default_factory=list,
        description="Active host or task situations where this memory is especially pertinent",
    )


class MemoryChunk(BaseModel):
    """An atomic, addressable chunk of mnemonic context (a mnemonic chunk).

    Enables granular retrieval, semantic indexing (vector DBs, RAG),
    and selective context injection without monolithic prompt bloat.
    """

    id: str = Field(
        ...,
        description="Unique chunk address, e.g. 'domain/memory_id#chunk_type'",
    )
    source_id: str = Field(..., description="Parent product identifier")
    source_kind: Literal["persona", "memory", "lineage"] = Field(
        ..., description="Source class"
    )
    chunk_type: str = Field(
        ...,
        description="Chunk category: story, scars, lessons, triggers, reflection, axiom, etc.",
    )
    title: str = Field(
        default="", description="Human-readable title or label for the chunk"
    )
    content: str = Field(..., description="Declarative text payload of the chunk")
    embedding_text: str = Field(
        ...,
        description="Self-grounding context representation optimized for semantic vector search",
    )
    salience: float = Field(default=1.0, ge=0.0, le=1.0, description="Priority weight")
    is_pinned: bool = Field(
        default=False,
        description="If True, must remain permanently in host prompt (e.g. foundational axioms)",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary tags, drives, or telemetry metadata",
    )


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
    teleology: Optional[Teleology] = Field(
        default=None,
        description="Foundational drives and philosophical inclinations",
    )
    author: str = Field(
        default="ARPA Hellenic Logical Systems", description="Creator or provenance"
    )
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary extension metadata"
    )

    def to_chunks(self) -> List[MemoryChunk]:
        """Atomize this persona into addressable MemoryChunks.

        Axioms, boundaries, and core philosophy are marked as is_pinned=True,
        signifying they belong in the static prefix of host context.
        """
        chunks: List[MemoryChunk] = []
        base_meta = {
            "domain": self.domain,
            "tags": self.tags,
            "kind": "persona",
        }
        if self.teleology:
            base_meta["drives"] = self.teleology.agent_drives
            base_meta["needs"] = self.teleology.applicable_needs

        # 1. Core Philosophy (Pinned)
        if self.core_philosophy:
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#philosophy",
                    source_id=self.id,
                    source_kind="persona",
                    chunk_type="philosophy",
                    title=f"{self.name} (Core Philosophy)",
                    content=self.core_philosophy.strip(),
                    embedding_text=(
                        f"[Persona: {self.name} - Core Epistemic Philosophy]: "
                        f"{self.core_philosophy.strip()}"
                    ),
                    salience=1.0,
                    is_pinned=True,
                    metadata=base_meta,
                )
            )

        # 2. Axioms (Pinned)
        if self.axioms:
            axioms_text = "\n".join(f"- {a}" for a in self.axioms)
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#axioms",
                    source_id=self.id,
                    source_kind="persona",
                    chunk_type="axiom",
                    title=f"{self.name} (Inviolable Axioms)",
                    content=axioms_text,
                    embedding_text=(
                        f"[Persona: {self.name} - Inviolable Axioms]: " f"{axioms_text}"
                    ),
                    salience=1.0,
                    is_pinned=True,
                    metadata=base_meta,
                )
            )

        # 3. Boundaries (Pinned)
        if self.boundaries:
            boundaries_text = "\n".join(f"- {b}" for b in self.boundaries)
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#boundaries",
                    source_id=self.id,
                    source_kind="persona",
                    chunk_type="boundary",
                    title=f"{self.name} (Behavioral Boundaries)",
                    content=boundaries_text,
                    embedding_text=(
                        f"[Persona: {self.name} - Inviolable Boundaries & Refusals]: "
                        f"{boundaries_text}"
                    ),
                    salience=1.0,
                    is_pinned=True,
                    metadata=base_meta,
                )
            )

        # 4. Cognitive Priors (Dynamic)
        if self.cognitive_priors:
            priors_text = "\n".join(f"- {p}" for p in self.cognitive_priors)
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#priors",
                    source_id=self.id,
                    source_kind="persona",
                    chunk_type="prior",
                    title=f"{self.name} (Cognitive Priors)",
                    content=priors_text,
                    embedding_text=(
                        f"[Persona: {self.name} - Cognitive Priors & Filters]: "
                        f"{priors_text}"
                    ),
                    salience=0.8,
                    is_pinned=False,
                    metadata=base_meta,
                )
            )

        # 5. Self-Narrative (Dynamic)
        if self.self_narrative:
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#self_narrative",
                    source_id=self.id,
                    source_kind="persona",
                    chunk_type="self_narrative",
                    title=f"{self.name} (Self-Narrative)",
                    content=self.self_narrative.strip(),
                    embedding_text=(
                        f"[Persona: {self.name} - Internal Self-Narrative]: "
                        f"{self.self_narrative.strip()}"
                    ),
                    salience=0.7,
                    is_pinned=False,
                    metadata=base_meta,
                )
            )

        return chunks


class MemoryProduct(BaseModel):
    """An episodic memory, operational scar, or digital-twin experience.

    Encodes real or synthetic experiential scars that grant deep domain intuition,
    lessons learned from costly errors, and tactile operational context.
    """

    id: str = Field(..., description="Unique slug or domain/slug identifier")
    name: str = Field(..., description="Human-readable title of the memory episode")
    version: str = Field(default="1.0.0", description="Semantic version string")
    domain: str = Field(default="general", description="Application domain")
    memory_type: MemoryKind = Field(
        default="incident",
        description="5-Kind Taxonomy: lore, work, incident, relational, telemetry",
    )
    episode_type: Optional[str] = Field(
        default=None,
        description="Legacy alias for memory_type",
    )

    @model_validator(mode="after")
    def _sync_episode_type(self) -> MemoryProduct:
        if self.episode_type is None:
            self.episode_type = (
                "scar" if self.memory_type == "incident" else self.memory_type
            )
        return self

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
    reflection: Optional[str] = Field(
        default=None,
        description="Philosophical takeaway and cognitive evolution from this episode",
    )
    salience: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Experiential weight coefficient (0.0=trivial, 1.0=identity-defining)",
    )
    teleology: Optional[Teleology] = Field(
        default=None,
        description="Teleological motivation: goals, drives, and applicable needs",
    )
    author: str = Field(
        default="ARPA Hellenic Logical Systems", description="Creator or provenance"
    )
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary extension metadata"
    )

    def get_chunk(self, chunk_type: str) -> Optional[str]:
        """Retrieve a specific text chunk by name ('story', 'scars', 'lessons', etc.)."""
        ct = chunk_type.lower().strip()
        if ct in ("story", "debrief", "episode"):
            return self.episode_debrief.strip() if self.episode_debrief else None
        elif ct in ("scars", "damage", "operational_scars"):
            return (
                "\n".join(f"- {s}" for s in self.operational_scars)
                if self.operational_scars
                else None
            )
        elif ct in ("lessons", "lessons_learned", "maxims"):
            return (
                "\n".join(f"- {lesson}" for lesson in self.lessons_learned)
                if self.lessons_learned
                else None
            )
        elif ct in ("triggers", "sensory", "sensory_context"):
            return self.sensory_context.strip() if self.sensory_context else None
        elif ct in ("reflection", "takeaway"):
            return self.reflection.strip() if self.reflection else None
        return None

    def to_chunks(self) -> List[MemoryChunk]:
        """Atomize this memory product into addressable, self-grounding MemoryChunks."""
        chunks: List[MemoryChunk] = []
        drives = self.teleology.agent_drives if self.teleology else []
        needs = self.teleology.applicable_needs if self.teleology else []
        base_meta = {
            "domain": self.domain,
            "memory_type": self.memory_type,
            "drives": drives,
            "needs": needs,
            "tags": self.tags,
            "salience": self.salience,
        }

        # 1. Story Chunk
        if self.episode_debrief:
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#story",
                    source_id=self.id,
                    source_kind="memory",
                    chunk_type="story",
                    title=f"{self.name} (Episode Story)",
                    content=self.episode_debrief.strip(),
                    embedding_text=(
                        f"[Context: {self.name} - Episode Debrief ({self.domain})]: "
                        f"{self.episode_debrief.strip()}"
                    ),
                    salience=self.salience,
                    metadata=base_meta,
                )
            )

        # 2. Scars Chunk
        if self.operational_scars:
            scars_text = "\n".join(f"- {s}" for s in self.operational_scars)
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#scars",
                    source_id=self.id,
                    source_kind="memory",
                    chunk_type="scars",
                    title=f"{self.name} (Operational Scars)",
                    content=scars_text,
                    embedding_text=(
                        f"[Context: {self.name} - Concrete Scars & Losses]: {scars_text}"
                    ),
                    salience=self.salience,
                    metadata=base_meta,
                )
            )

        # 3. Lessons Chunk
        if self.lessons_learned:
            lessons_text = "\n".join(f"- {lesson}" for lesson in self.lessons_learned)
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#lessons",
                    source_id=self.id,
                    source_kind="memory",
                    chunk_type="lessons",
                    title=f"{self.name} (Lessons Learned)",
                    content=lessons_text,
                    embedding_text=(
                        f"[Context: {self.name} - Lessons Learned & Action Rules]: "
                        f"{lessons_text}"
                    ),
                    salience=self.salience,
                    metadata=base_meta,
                )
            )

        # 4. Triggers Chunk
        if self.sensory_context:
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#triggers",
                    source_id=self.id,
                    source_kind="memory",
                    chunk_type="triggers",
                    title=f"{self.name} (Sensory Triggers)",
                    content=self.sensory_context.strip(),
                    embedding_text=(
                        f"[Context: {self.name} - Sensory & Friction Triggers]: "
                        f"{self.sensory_context.strip()}"
                    ),
                    salience=self.salience,
                    metadata=base_meta,
                )
            )

        # 5. Reflection Chunk
        if self.reflection:
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#reflection",
                    source_id=self.id,
                    source_kind="memory",
                    chunk_type="reflection",
                    title=f"{self.name} (Cognitive Reflection)",
                    content=self.reflection.strip(),
                    embedding_text=(
                        f"[Context: {self.name} - Philosophical Reflection]: "
                        f"{self.reflection.strip()}"
                    ),
                    salience=self.salience,
                    metadata=base_meta,
                )
            )

        return chunks


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
    teleology: Optional[Teleology] = Field(
        default=None,
        description="Overall evolutionary drive and purpose of this lineage progression",
    )
    author: str = Field(
        default="ARPA Hellenic Logical Systems", description="Creator or provenance"
    )
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary extension metadata"
    )

    def to_chunks(self) -> List[MemoryChunk]:
        """Atomize this lineage into addressable MemoryChunks."""
        chunks: List[MemoryChunk] = []
        base_meta = {
            "tags": self.tags,
            "kind": "lineage",
            "memory_ids": self.memory_ids,
        }
        if self.teleology:
            base_meta["drives"] = self.teleology.agent_drives
            base_meta["needs"] = self.teleology.applicable_needs

        if self.cumulative_narrative:
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#cumulative_narrative",
                    source_id=self.id,
                    source_kind="lineage",
                    chunk_type="lineage_narrative",
                    title=f"{self.name} (Cumulative Narrative)",
                    content=self.cumulative_narrative.strip(),
                    embedding_text=(
                        f"[Lineage: {self.name} - Unified Historical Backstory]: "
                        f"{self.cumulative_narrative.strip()}"
                    ),
                    salience=0.9,
                    is_pinned=False,
                    metadata=base_meta,
                )
            )

        for i, bridge in enumerate(self.causal_bridges, 1):
            chunks.append(
                MemoryChunk(
                    id=f"{self.id}#bridge_{i}",
                    source_id=self.id,
                    source_kind="lineage",
                    chunk_type="causal_bridge",
                    title=f"{self.name} (Causal Bridge {i})",
                    content=bridge.strip(),
                    embedding_text=(
                        f"[Lineage: {self.name} - Causal Evolution {i}]: "
                        f"{bridge.strip()}"
                    ),
                    salience=0.85,
                    is_pinned=False,
                    metadata=base_meta,
                )
            )

        return chunks


class CatalogCard(BaseModel):
    """Catalog presentation, discovery, and marketplace metadata."""

    id: str
    name: str
    kind: str = Field(..., description="'persona', 'memory', or 'lineage'")
    domain: str
    summary: str
    version: str = "1.0.0"
    tags: List[str] = Field(default_factory=list)
    memory_type: Optional[MemoryKind] = Field(
        default=None,
        description="5-Kind Taxonomy: lore, work, incident, relational, telemetry (for memories)",
    )
    teleology: Optional[Teleology] = Field(
        default=None,
        description="Motivational layer: goals, drives, and applicable needs",
    )
    chunk_manifest: Optional[Dict[str, str]] = Field(
        default=None,
        description="Index of constituent chunks available in this package",
    )
    tier: str = Field(default="bundled", description="'bundled', 'user', or 'project'")
    path: str = Field(default="", description="Filesystem location")

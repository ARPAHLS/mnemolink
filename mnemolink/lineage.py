"""Lineage Builder: Dynamic Lego-brick memory chaining and narrative bridging.

Transforms discrete, disjointed episodic memories and operational scars into
a coherent, causally connected historical backstory for an agent or robot.
"""

from __future__ import annotations

from typing import List, Optional
from mnemolink.models import LineageProduct, MemoryProduct, PersonaProduct


class LineageBuilder:
    """Weaves a set of MemoryProducts into a coherent, causally connected LineageProduct.

    Acts like a dynamic lego assembler: takes individual experiential bricks (battle scars,
    costly errors, sensor recoveries) and synthesizes the chronological narrative and
    associative bridges that connect them.
    """

    def __init__(self, persona: Optional[PersonaProduct] = None):
        self.persona = persona

    def build(
        self,
        memories: List[MemoryProduct],
        lineage_id: str = "dynamic_lineage",
        name: str = "Synthesized Experiential Lineage",
    ) -> LineageProduct:
        """Construct a unified LineageProduct from an ordered sequence of memories."""
        if not memories:
            return LineageProduct(
                id=lineage_id,
                name=name,
                summary="Empty experiential lineage.",
                memory_ids=[],
                chronology=[],
                causal_bridges=[],
                cumulative_narrative="",
            )

        memory_ids = [m.id for m in memories]
        chronology = []
        causal_bridges = []
        narrative_sections = []

        # Narrative opener setting the tone
        if self.persona and self.persona.self_narrative:
            narrative_sections.append(
                f"### Formative Perspective\n{self.persona.self_narrative.strip()}\n"
            )

        narrative_sections.append("### Chronological Experiential Evolution\n")

        for idx, mem in enumerate(memories):
            step_num = idx + 1
            chronology_tag = f"Epoch {step_num}: {mem.name}"
            chronology.append(chronology_tag)

            section = [f"#### {step_num}. {mem.name} ({mem.domain.upper()})"]
            if mem.sensory_context:
                section.append(f"*[Operational Environment: {mem.sensory_context}]*")

            m_type = getattr(mem, "memory_type", "incident")
            if m_type == "incident":
                debrief_label = "**The Crucible & Crisis**"
                scars_label = "**Operational Scars**"
            elif m_type == "work":
                debrief_label = "**Tradecraft & Operational Practice**"
                scars_label = "**Challenges Overcome & Friction Points**"
            elif m_type == "lore":
                debrief_label = "**Formative Experience & Heritage**"
                scars_label = "**Formative Milestones & Obstacles**"
            elif m_type == "relational":
                debrief_label = "**Relational Milestone & Partnership**"
                scars_label = "**Friction Points & Alignment Challenges**"
            elif m_type == "telemetry":
                debrief_label = "**Telemetry Benchmark & Empirical Run**"
                scars_label = "**Anomalies & Variance Factors**"
            else:
                debrief_label = "**Experiential Debrief**"
                scars_label = "**Challenges Overcome**"

            section.append(f"\n{debrief_label}: {mem.episode_debrief.strip()}")

            if mem.operational_scars:
                scars_str = "\n".join(f"- {scar}" for scar in mem.operational_scars)
                section.append(f"\n{scars_label}:\n{scars_str}")

            if mem.lessons_learned:
                lessons_str = "\n".join(f"- {lesson}" for lesson in mem.lessons_learned)
                section.append(f"\n**Core Principles & Maxims**:\n{lessons_str}")

            narrative_sections.append("\n".join(section))

            # Build causal bridge to the next memory
            if idx < len(memories) - 1:
                next_mem = memories[idx + 1]
                bridge = self._synthesize_bridge(mem, next_mem, step_num)
                causal_bridges.append(bridge)
                narrative_sections.append(f"\n> **Causal Bridge**: {bridge}\n")

        # Concluding synthesis
        all_lessons = [lesson for m in memories for lesson in m.lessons_learned]
        if all_lessons:
            distilled = "\n".join(f"- {item}" for item in all_lessons[:6])
            narrative_sections.append(
                "\n### Cumulative Experiential Reflexes & Wisdom\n"
                "The compound weight of these events forms an instinctual foundation. "
                "When confronting novel scenarios, decisions are guided by these principles:\n"
                f"{distilled}"
            )

        cumulative = "\n\n".join(narrative_sections)

        domain_count = len(set(m.domain for m in memories))
        return LineageProduct(
            id=lineage_id,
            name=name,
            summary=(
                f"Synthesized sequence of {len(memories)} episodic memories "
                f"across {domain_count} domain(s)."
            ),
            memory_ids=memory_ids,
            chronology=chronology,
            causal_bridges=causal_bridges,
            cumulative_narrative=cumulative,
            tags=["synthesized", "dynamic_lego"],
        )

    def _synthesize_bridge(
        self, prev_mem: MemoryProduct, next_mem: MemoryProduct, step_num: int
    ) -> str:
        """Create connective causal tissue between two distinct memory episodes."""
        prev_primary_lesson = (
            prev_mem.lessons_learned[0]
            if prev_mem.lessons_learned
            else f"the consequences of {prev_mem.name}"
        )

        if prev_mem.domain == next_mem.domain:
            return (
                f"The scar left by {prev_mem.name} fundamentally reshaped operating assumptions. "
                f"Armed with the hard lesson that '{prev_primary_lesson}', the subsequent trial of "
                f"{next_mem.name} was approached not with naive theory, but with vigilant caution."
            )
        else:
            return (
                f"Though transitioning from {prev_mem.domain} into {next_mem.domain}, "
                f"the residue of {prev_mem.name} proved decisive: the realization that "
                f"'{prev_primary_lesson}' translated directly into how {next_mem.name} "
                f"was navigated under pressure."
            )

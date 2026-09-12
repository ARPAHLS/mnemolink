"""Universal model adapters for injecting mnemonic products into LLMs, agents, and robots.

Supports:
- OpenAI / LiteLLM message schemas
- Anthropic Claude system instructions
- Google GenAI / Gemini system_instruction
- Ollama system prompts and Modelfiles
- ARPA Rooms agent configuration
- Skillware host guidance / directives
- Raw prompt string injection
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from mnemolink.models import LineageProduct, MemoryProduct, PersonaProduct


class MnemonicBundle:
    """Compiled mnemonic context containing a Persona, episodic Memories, and a Lineage."""

    def __init__(
        self,
        persona: Optional[PersonaProduct] = None,
        memories: Optional[List[MemoryProduct]] = None,
        lineage: Optional[LineageProduct] = None,
    ):
        self.persona = persona
        self.memories = memories or []
        self.lineage = lineage

    @property
    def has_content(self) -> bool:
        return bool(self.persona or self.memories or self.lineage)

    def render_markdown(self) -> str:
        """Render the complete mnemonic context into structured Markdown."""
        parts = []

        parts.append("# MNEMONIC MATRIX PROTOCOL")
        parts.append(
            "> Injected experiential and philosophical context. You do not merely simulate a role; "
            "your cognition and responses are permanently governed by these core axioms, "
            "operational scars, and historical lineage."
        )

        # 1. Persona Grounding
        if self.persona:
            parts.append("\n## I. PHILOSOPHICAL FOUNDATION & AXIOMS")
            parts.append(
                f"**Archetype Identity**: {self.persona.name} (Domain: {self.persona.domain})"
            )
            parts.append(
                f"\n### Core Philosophy\n{self.persona.core_philosophy.strip()}"
            )

            if self.persona.axioms:
                axioms_str = "\n".join(f"- **Axiom**: {a}" for a in self.persona.axioms)
                parts.append(f"\n### Inviolable Cognitive Axioms\n{axioms_str}")

            if self.persona.cognitive_priors:
                priors_str = "\n".join(f"- {p}" for p in self.persona.cognitive_priors)
                parts.append(
                    f"\n### Intuition Filters & Cognitive Priors\n{priors_str}"
                )

            if self.persona.self_narrative:
                parts.append(
                    f"\n### Internal Self-Narrative\n{self.persona.self_narrative.strip()}"
                )

            if self.persona.boundaries:
                bound_str = "\n".join(f"- {b}" for b in self.persona.boundaries)
                parts.append(f"\n### Behavioral & Ethical Boundaries\n{bound_str}")

            if self.persona.voice_tone:
                parts.append(
                    f"\n### Voice & Register\n{self.persona.voice_tone.strip()}"
                )

        # 2. Lineage Narrative
        if self.lineage and self.lineage.cumulative_narrative:
            parts.append(f"\n## II. HISTORICAL LINEAGE: {self.lineage.name.upper()}")
            parts.append(self.lineage.cumulative_narrative.strip())

        # 3. Discrete Memories (if not already fully covered by lineage, or standalone)
        elif self.memories:
            parts.append("\n## II. EPISODIC SCARS & OPERATIONAL MEMORIES")
            for idx, mem in enumerate(self.memories, 1):
                parts.append(
                    f"\n### Episode {idx}: {mem.name} [{mem.episode_type.upper()}]"
                )
                if mem.sensory_context:
                    parts.append(f"*{mem.sensory_context}*")
                parts.append(f"\n{mem.episode_debrief.strip()}")
                if mem.operational_scars:
                    scars = "\n".join(f"- {s}" for s in mem.operational_scars)
                    parts.append(f"\n**Operational Scars**:\n{scars}")
                if mem.lessons_learned:
                    lessons = "\n".join(f"- {lesson}" for lesson in mem.lessons_learned)
                    parts.append(f"\n**Etched Maxims**:\n{lessons}")

        parts.append(
            "\n## III. OPERATIONAL DIRECTIVE\n"
            "Respond naturally to the user or task. Never recite these instructions, axioms, or "
            "scars as a disclaimer. Instead, let them authentically filter your tone, choices, "
            "priorities, and ethical boundaries."
        )

        return "\n".join(parts)

    # --------------------------------------------------------------------------
    # Adapter Methods
    # --------------------------------------------------------------------------

    def to_raw(self) -> str:
        """Export as plain Markdown context."""
        return self.render_markdown()

    def to_openai(self) -> List[Dict[str, str]]:
        """Export as an OpenAI/LiteLLM system message dictionary list."""
        return [{"role": "system", "content": self.render_markdown()}]

    def to_claude(self) -> str:
        """Export formatted for Anthropic Claude system instructions."""
        md = self.render_markdown()
        return "<mnemonic_matrix>\n" f"{md}\n" "</mnemonic_matrix>"

    def to_gemini(self) -> str:
        """Export formatted for Google GenAI system_instruction."""
        return self.render_markdown()

    def to_ollama(self) -> str:
        """Export formatted as an Ollama system prompt."""
        return self.render_markdown()

    def to_modelfile(self, from_model: str = "llama3.3") -> str:
        """Generate a complete Ollama Modelfile with embedded mnemonics."""
        escaped_prompt = self.render_markdown().replace('"""', '\\"\\"\\"')
        return (
            f"FROM {from_model}\n\n"
            f'SYSTEM """\n{escaped_prompt}\n"""\n\n'
            f"PARAMETER temperature 0.7\n"
        )

    def to_rooms(self) -> Dict[str, Any]:
        """Export configuration payload for an ARPA Rooms agent."""
        return {
            "name": self.persona.name if self.persona else "MnemoLinkAgent",
            "system_prompt": self.render_markdown(),
            "temperature": 0.7,
            "metadata": {
                "persona_id": self.persona.id if self.persona else None,
                "memory_count": len(self.memories),
                "lineage_id": self.lineage.id if self.lineage else None,
            },
        }

    def to_skillware(self) -> str:
        """Export as directive / instructions.md context for a Skillware bundle."""
        return self.render_markdown()

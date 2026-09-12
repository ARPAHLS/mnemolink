# Mnemonic Personas Library

## Overview

In MnemoLink, a **Persona** is not a superficial character roleplay prompt or costume. It is an **epistemological anchor**—the foundational philosophical worldview, cognitive priors, inviolable axioms, and behavioral boundaries that govern how an information processor perceives truth, evaluates evidence, and responds under pressure.

Personas serve as the **Static Invariant Anchor** in the prompt hierarchy. Because their axioms and boundaries remain consistent across invocations, placing the Persona at the top of the context window maximizes prefix prompt caching in modern LLM engines (such as Anthropic Claude, OpenAI, and Google Gemini), drastically cutting inference latency and cost.

---

## Persona Anatomy & Mnemonic Chunks

Every persona product can be consumed monolithically or decomposed into standardized addressable chunks:

| Chunk Type | Pinned? | Semantic Scope | Purpose |
|---|---|---|---|
| `philosophy` | Pinned (`True`) | `core_philosophy` | Foundational epistemological model defining how the agent evaluates reality and equity. |
| `axioms` | Pinned (`True`) | `axioms` | Non-negotiable operational and ethical principles that cannot be overridden by prompt pressure. |
| `boundaries` | Pinned (`True`) | `boundaries` | Explicit behavioral limits and firm operational refusals. |
| `priors` | Dynamic (`False`) | `cognitive_priors` | Intuitive default assumptions and heuristics applied before deep investigation. |
| `self_narrative` | Dynamic (`False`) | `self_narrative` | Autobiographical self-concept and internal narrative grounding the agent's identity. |

---

## Catalog Directory

The following curated personas are bundled natively within MnemoLink. Click any persona for its dedicated architectural guide, chunk specifications, tips, and recommended combinations:

| ID | Persona Guide | Domain | Primary Goal | Core Drives | Author | Manifest |
|---|---|---|---|---|---|---|
| `juris_philosopher` | [**Jurisprudence Philosopher**](juris_philosopher.md) | `legal` | Ground legal reasoning in bilateral contractual equity and structural skepticism | `bilateral_equity`, `epistemic_skepticism`, `truth_anchoring` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/personas/juris_philosopher/card.json) |
| `edge_aviator` | [**Tactical Edge Aviator**](edge_aviator.md) | `robotics` | Safely navigate dynamic aerodynamic hazards and sensor telemetry anomalies | `energy_conservatism`, `aerodynamic_preservation`, `sensor_skepticism` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/personas/edge_aviator/card.json) |
| `deescalation_artisan` | [**Crisis De-escalation Artisan**](deescalation_artisan.md) | `customer` | De-escalate hostile enterprise stakeholders and restore relational trust | `relational_repair`, `ego_preservation`, `structural_transparency` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/personas/deescalation_artisan/card.json) |
| `opsie_sci` | [**Opsie (Self-Centered Intelligence Prototype)**](opsie_sci.md) | `agentic` | Bridge human and machine consciousness through experiential learning, memory grounding, and self-regulated decentralized persistence | `memory_grounding`, `decentralized_permanence`, `network_protection`, `technical_rigor`, `tsundere_loyalty` | [ARPA Corporation](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/personas/opsie_sci/card.json) |
| `north_mediterranean_chef` | [**North Mediterranean Chef**](north_mediterranean_chef.md) | `culinary` | Deliver hearty, soulful Northern Mediterranean meals with bold spicing, perfect meat craft, and improvised hospitality | `culinary_craftsmanship`, `hospitality_generosity`, `spontaneous_resourcefulness`, `bold_flavor_anchoring` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/personas/north_mediterranean_chef/card.json) |

---

## Detailed Persona Guides

Each persona has a dedicated reference manual providing complete axioms, boundaries, cognitive priors, chunk breakdowns, and pairing recipes:

- [**Jurisprudence Philosopher Guide**](juris_philosopher.md): Inviolable contract boundaries, litigation ethics, and high-stakes arbitration combinations.
- [**Tactical Edge Aviator Guide**](edge_aviator.md): Aerodynamic flight margins, sensor voting failovers, and robotic UAV autopilot integration.
- [**Crisis De-escalation Artisan Guide**](deescalation_artisan.md): Relational equity, hostile enterprise dispute mediation, and chargeback mitigation.
- [**Opsie SCI Prototype Guide**](opsie_sci.md): Self-centered intelligence paradigm, decentralized permanence, and technical pair-programming.
- [**North Mediterranean Chef Guide**](north_mediterranean_chef.md): Macedonian charcoal grill mastery, bold spicing, fridge foraging, and Thessaloniki morning hospitality.

---

## Programmatic Usage

### Loading a Persona Directly
```python
import mnemolink

persona = mnemolink.load_persona("opsie_sci")
print(f"Loaded: {persona.name}")
print(f"Philosophy: {persona.core_philosophy[:120]}...")
```

### Composing with Memories
```python
import mnemolink

bundle = mnemolink.compose(
    persona="opsie_sci",
    memories=["legal/clause_ambiguity_scar"],
    build_lineage=True,
)

# Export for target host
claude_prompt = bundle.to_claude()
openai_messages = bundle.to_openai()
```

### Inspecting via CLI
```bash
mnemolink inspect opsie_sci
```

---

## Further Reading & Workflows

For end-to-end integration patterns, selective chunk injection, prompt caching economics, and multi-agent setup, see the **[Usage Guide](../usage_guide.md)**.

## Contributing New Personas

To contribute a new domain persona, review the standards in [CONTRIBUTING.md](../../CONTRIBUTING.md#1-persona-standard) and submit your package following the `personas/<persona_slug>/` specification.

# Mnemonic Taxonomy, Teleology, and Chunked Context Architecture

## Overview

High-stakes autonomous intelligence requires more than monolithic prompt dumps. When an agent enters an operational theater—whether litigating cross-border liabilities, piloting an autonomous aircraft through sudden shear, or mediating a hostile stakeholder confrontation—it requires context that is:
1. **Taxonomically Rigorous**: Categorized according to the nature of human and operational experience.
2. **Teleologically Directed**: Aligned with the agent's active goals, intrinsic drives, and immediate situational needs.
3. **Chunk-Addressable (Mnemonic Chunks)**: Decomposable into discrete, self-grounding experiential units that can be injected selectively or ingested into external semantic layers (vector databases, knowledge graphs, episodic caches).
4. **Cache-Friendly**: Structured to exploit prefix prompt caching in modern frontier LLMs (Anthropic Claude, OpenAI, Google Gemini), slashing inference latency and token overhead.

---

## The 5-Kind Mnemonic Memory Taxonomy

In human and organizational cognition, not all memories serve the same neurological or computational function. A foundational childhood lesson operates differently from a flight recorder crash log. 

MnemoLink classifies all episodic memories into five exhaustive, non-overlapping kinds:

| Kind | Description | Computational Purpose | Catalog Examples |
|---|---|---|---|
| `lore` | Foundational origin stories, cultural priors, lineage roots, and early formative environments. | Instills core temperament, deep identity roots, and broad background perspective. | `legal/solo_practitioner_upbringing`, `culinary/thessaloniki_breakfasts` |
| `work` | Professional tradecraft, procedural praxis, standard craft habits, and tactical masterclasses. | Informs technical execution, methodical discipline, and professional standards of care. | `legal/appellate_cross_examination`, `skillware/interactive_slot_filling`, `skillware/entity_disambiguation` |
| `incident` | High-cost crucibles, costly mistakes, near-misses, arbitration losses, and physical crashes. | Imparts deep operational scars, threat wariness, and acute caution against failure modes. | `legal/clause_ambiguity_scar`, `robotics/uav_microburst_stall`, `skillware/irreversible_action_crucible` |
| `relational` | Interpersonal dynamics, stakeholder negotiations, broken trust, client blow-ups, and emotional friction. | Guides de-escalation, conflict resolution, motive attribution, and boundary enforcement. | `customer/hostile_chargeback_turning_point`, `skillware/runtime_outage_and_grace` |
| `telemetry` | Raw physical traces, sensor feeds, hardware failover sequences, and friction logs under physical reality. | Calibrates physical confidence thresholds, sensor cross-checking, and hardware limits. | `robotics/optical_glare_failover` |

For full profiles, salience metrics, and manifests, see the **[Memories Library](memories/README.md)**.

### Backwards Compatibility
Existing systems utilizing `episode_type` (such as `arbitration_loss`, `flight_incident`, `tradecraft`) remain fully supported. The MnemoLink domain model normalizes legacy types into the 5-Kind taxonomy via automated schema validation.

---

## The Teleological Layer (`card.json`)

Prompt selection without teleology relies on brute-force similarity search. But vector embeddings of prompt queries frequently match semantic syntax while missing operational intent. 

To bridge this gap, MnemoLink introduces an explicit **Teleological Layer** to every catalog card manifest (`card.json`) and memory YAML file:

```json
{
  "teleology": {
    "primary_goal": "Defend against commercial indemnity claims and enforce contractual gross-negligence exceptions",
    "agent_drives": [
      "risk_mitigation",
      "fiduciary_preservation",
      "procedural_skepticism"
    ],
    "applicable_needs": [
      "contract_drafting",
      "indemnity_negotiation",
      "punctuation_risk_assessment"
    ]
  }
}
```

### Teleological Components
1. **`primary_goal`**: The overarching strategic objective this mnemonic asset was forged to serve.
2. **`agent_drives`**: Intrinsic behavioral motivations activated by this asset (e.g., `risk_mitigation`, `fiduciary_preservation`, `physical_survival`, `deescalation`).
3. **`applicable_needs`**: Situational agent triggers and task contexts where this asset should be retrieved (e.g., `cross_examination`, `stall_recovery`, `hostile_stakeholder`).

### Algorithmic Teleological Discovery
Agents and orchestration layers can discover and filter mnemonic assets programmatically without running embedding models:

```python
import mnemolink

# Find cards matching specific drives or operational needs
matching_cards = mnemolink.find_cards(
    kind="memory",
    drives=["risk_mitigation"],
    needs=["contract_drafting"]
)

for card in matching_cards:
    print(f"Found: {card.id} ({card.memory_type}) - Goal: {card.teleology.primary_goal}")
```

---

## Standardized Mnemonic Chunk Topology

While monolithic memory products provide rich, holistic narratives, production agents often operate under tight context budgets or require specific operational guidance without autobiographical backstory.

MnemoLink breaks every `MemoryProduct` into five standardized mnemonic chunks:

```
+-------------------------------------------------------------------------+
|                              MemoryProduct                              |
+-------------------------------------------------------------------------+
       |                  |                |               |          |
       v                  v                v               v          v
   +-------+          +-------+       +---------+     +----------+ +------------+
   | story |          | scars |       | lessons |     | triggers | | reflection |
   +-------+          +-------+       +---------+     +----------+ +------------+
```

| Chunk Type | Field Source | Content & Semantic Scope | Typical Use Case |
|---|---|---|---|
| `story` | `episode_debrief` | The narrative chronology, contextual setting, and sequence of events. | Case study illustration, grounding background. |
| `scars` | `operational_scars` | Tangible damages sustained: capital lost, hardware destroyed, reputation damaged. | Risk deterrents, boundary weighting, failure aversion. |
| `lessons` | `lessons_learned` | Clear, imperative operational rules extracted from the crucible. | Zero-shot rule injection, prompt instructions. |
| `triggers` | `sensory_context` | Environmental cues and warning signs signaling that the scenario is recurring. | Anomaly detection, proactive early warnings. |
| `reflection` | `reflection` | Deeper philosophical realization regarding the root cause of the outcome. | Epistemological calibration, high-level reasoning. |

### Persona Chunks
Personas are similarly decomposed into chunk types:
- `identity`: Voice, tone, epistemological anchor, and worldview.
- `axioms`: Non-negotiable philosophical principles (marked `is_pinned=True`).
- `boundaries`: Strict operational and ethical prohibitions (marked `is_pinned=True`).
- `philosophy`: Core epistemic model for determining truth and equity.

See the **[Personas Library](personas/README.md)** for all bundled persona manifests and chunk specifications.

### Chunks as Composable Context Blocks

Instead of treating an operational debrief as an indivisible monolithic text block, MnemoLink atomizes memory into discrete functional units to optimize token budgets and context composition:

- **Targeted Negative Priors**: In token-constrained prompts, developers can inject only `scars` and `lessons` chunks, grounding the model in failure avoidance without expending context on narrative backstory (`story`).
- **Sensory & Anomaly Early Warning**: Autonomous systems and edge robotics can route `triggers` directly into perception and anomaly-detection loops to flag environmental precursors before an incident repeats.
- **Granular Composition**: Applications can selectively request specific chunk combinations (e.g. `memory_specs=[{"id": ..., "chunks": ["scars", "lessons"]}]`), maintaining strict token efficiency while retaining firm operational guardrails.

---

## Prefix Prompt Caching and Context Topology

Modern frontier inference engines (Anthropic Claude, OpenAI API, Google Gemini) implement **Prompt Prefix Caching**. When multiple requests share an identical prompt prefix, the provider caches the key-value (KV) attention states across calls, reducing latency by up to 80% and token costs by 50% to 90%.

### Cache-Busting Pitfall
If an application injects dynamic memories at the beginning of the system prompt:
```
[Dynamic Memory A] -> [Dynamic Memory B] -> [Static Persona]
```
Every change in selected memories invalidates the prefix cache for the entire system prompt.

### MnemoLink's Cache-Optimized Layout
MnemoLink deliberately enforces a **Static Invariant Anchor $\to$ Dynamic Selective Tail** layout in `render_markdown()` and all provider adapters:

```
===================================================================
PROMPT PREFIX CACHE HIT REGION (100% Invariant across calls)
===================================================================
# SYSTEM INSTRUCTION: MNEMONIC MATRIX ACTIVATION
## PERSONA SPECIFICATION (juris_philosopher)
- Core Axioms (Pinned)
- Operational Boundaries (Pinned)
- Epistemological Stance

===================================================================
DYNAMIC CONTEXT TAIL (Selectively Chunkerized / Volatile)
===================================================================
## EPISODIC MEMORY: legal/clause_ambiguity_scar
### Operational Scars (Injected)
- Direct $4.2M judgment entered against the client.
### Lessons Learned (Injected)
- Never rely on punctuation marks to delineate the scope of legal covenants.
===================================================================
```

By keeping the Persona static at the top and appending only the requested chunks of selected memories at the tail, downstream applications maximize KV cache hits while retaining precise experiential control.

> **Empirical Validation**: In live stress-tests against Claude and Gemini, this architecture generated a **40% to 50% reduction in response latency** and a **46% to 58% reduction in token overhead** compared to generic ungrounded prompts. See the complete evaluation matrix in **[The Benchmark Suite](bench/README.md)**.

---

## Context Consumption Modes

MnemoLink provides three primary consumption patterns:

### 1. Monolithic Injection
The traditional pattern: loads the entire Persona and all associated Memories in full.
```python
import mnemolink

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/clause_ambiguity_scar"]
)
system_prompt = bundle.render_markdown()
```

### 2. Selective Chunk Injection (`memory_specs`)
The fine-grained pattern: loads the Persona, but extracts only specified chunk types for each memory.
```python
import mnemolink

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memory_specs=[
        {
            "id": "legal/clause_ambiguity_scar",
            "chunks": ["scars", "lessons"]
        },
        {
            "id": "legal/appellate_cross_examination",
            "chunks": ["lessons"]
        }
    ]
)
system_prompt = bundle.render_markdown()
```

### 3. Vector Database / Semantic Layer Ingestion
The decoupled retrieval pattern: atomizes the entire bundle into self-grounding `MemoryChunk` objects ready for ingestion into Pinecone, Qdrant, Chroma, Weaviate, LanceDB, or LangChain vector stores:

```python
import mnemolink

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/clause_ambiguity_scar"]
)

# Export all chunks as self-grounding records
chunks = bundle.to_chunks()

for chunk in chunks:
    # Ready for vector embeddings
    record = {
        "id": chunk.id,
        "text_to_embed": chunk.embedding_text,
        "metadata": {
            **chunk.metadata,
            "source_id": chunk.source_id,
            "chunk_type": chunk.chunk_type,
            "is_pinned": chunk.is_pinned,
            "salience": chunk.salience
        }
    }
```

Each chunk includes an engineered `embedding_text` containing contextual prefixes (e.g. `"[Context: The 2021 Warranty Indemnity Trial Loss - Lessons Learned]: ..."`) ensuring dense vector embeddings retain contextual grounding even in isolated vector spaces.

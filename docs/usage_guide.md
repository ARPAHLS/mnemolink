# MnemoLink Usage Guide

A comprehensive, end-to-end guide to using MnemoLink across development, production, multi-agent frameworks, robotics, and custom context pipelines.

---

## 1. Mental Model: Why MnemoLink?

Most agent failures do not stem from a shortage of model parameters or context window length. They stem from a lack of **epistemic grounding and operational scars**:

- **A Persona is not roleplay.** It is an epistemological anchor: the inviolable axioms, cognitive priors, and boundaries that dictate how an agent perceives truth and filters ambiguity.
- **A Memory is not a raw document.** It is an episodic crucible classified across a 5-Kind Taxonomy (`lore`, `work`, `incident`, `relational`, `telemetry`), atomized into addressable chunks (`story`, `scars`, `lessons`, `triggers`, `reflection`), and tagged with teleological drives (`goals`, `drives`, `needs`).
- **A Lineage is not a flat transcript.** It is a dynamic lego-brick chain where chronological experiences are bonded by causal bridges, forming a coherent cumulative history.

MnemoLink decouples this experiential foundation from the model itself, letting you inject battle-tested instincts into any LLM, autonomous vehicle, or robotics runtime.

---

## 2. Installation & Quick Verification

### Install via PyPI
```bash
pip install mnemolink
```

### Install from Source (Development)
```bash
git clone https://github.com/ARPAHLS/mnemolink.git
cd mnemolink
pip install -e ".[all]"
```

### Verification
Verify that the CLI and library are operational:
```bash
# Interactive splash menu (TTY) or standard usage when piped
mnemolink
mnemolink --help

# Verify Python package import
python -c "import mnemolink; print(f'MnemoLink v{mnemolink.__version__} initialized successfully')"
```

---

## 3. Core Building Blocks & Programmatic Usage

### 3.1 Personas
A persona defines the agent's core worldview, boundaries, and reasoning axioms.

```python
import mnemolink

# Load a curated persona
chef = mnemolink.load_persona("north_mediterranean_chef")
lawyer = mnemolink.load_persona("juris_philosopher")

# Inspect core attributes
print(chef.name)             # North Mediterranean Chef
print(chef.core_philosophy)  # Charred meats, mountain herbs, honest craftsmanship
print(chef.axioms)           # ['Extra virgin Greek olive oil is non-negotiable...', ...]
print(chef.boundaries)       # ['Never mask bad meat with sweet glazes...', ...]

# Decompose persona into addressable semantic chunks
chunks = chef.to_chunks()
for chunk in chunks:
    print(f"[{chunk.chunk_type}] pinned={chunk.pinned} -> {chunk.content[:60]}...")
```

### 3.2 Memories & The 5-Kind Taxonomy
Memories represent discrete episodic crucibles classified into five operational categories:
1. `lore`: Foundational origins, upbringing, cultural tradecraft.
2. `work`: Routine craftsmanship, professional workflows, iterative mastery.
3. `incident`: Operational failures, trial losses, drone stalls, hard-won scars.
4. `relational`: Stakeholder conflict, hostile negotiations, team friction.
5. `telemetry`: Hard sensory metrics, sensor glare, microburst recoveries.

```python
# Load episodic memories
scar = mnemolink.load_memory("legal/clause_ambiguity_scar")
breakfast = mnemolink.load_memory("culinary/thessaloniki_breakfasts")

# Inspect memory attributes
print(breakfast.memory_type)         # lore
print(breakfast.salience)            # 0.94
print(breakfast.lessons_learned)     # ['The 120-second residual heat window...', ...]

# Access individual chunks directly
scars_chunk = scar.get_chunk("scars")
lessons_chunk = breakfast.get_chunk("lessons")
```

### 3.3 Bundled Lineages
Lineages link memories chronologically with causal bridges showing how early experience shaped subsequent decisions.

```python
# Load pre-built curated lineages
legal_lineage = mnemolink.load_lineage("legal_crucible")
flight_lineage = mnemolink.load_lineage("flight_scars")

print(legal_lineage.name)
print(legal_lineage.memory_ids)      # ['legal/solo_practitioner_upbringing', 'legal/clause_ambiguity_scar', ...]
print(legal_lineage.causal_bridges)  # Shows causal linkage between successive crucibles
```

### 3.4 Creating & Synthesizing Custom Lineages
You can dynamically build lineages using the `LineageBuilder` or via `compose()`:

#### Option A: Programmatic Synthesis with `LineageBuilder`
```python
from mnemolink import LineageBuilder, load_memory

mem1 = load_memory("robotics/uav_microburst_stall")
mem2 = load_memory("robotics/optical_glare_failover")

builder = LineageBuilder()
custom_lineage = builder.synthesize(
    id="autonomous_recovery_arc",
    name="Autonomous Recovery Arc",
    memories=[mem1, mem2],
)

print(custom_lineage.causal_bridges)
```

#### Option B: Composing Directly via `compose()`
```python
import mnemolink

bundle = mnemolink.compose(
    persona="edge_aviator",
    memories=["robotics/uav_microburst_stall", "robotics/optical_glare_failover"],
    build_lineage=True,
)
```

#### Option C: Composing via the CLI
```bash
mnemolink compose \
  -p edge_aviator \
  -m robotics/uav_microburst_stall robotics/optical_glare_failover \
  --build-lineage \
  -f raw
```

---

## 4. Selective Mnemonic Chunking & Prompt Cache Optimization

### Why Selective Chunking?
Injecting full narrative stories across five memories can rapidly consume context windows and drive up inference costs. MnemoLink lets you inject **only the critical operational chunks** (e.g. `scars` and `lessons`) while discarding long descriptive passages:

```python
import mnemolink
from mnemolink import MemorySpec

# Selectively inject only scars and lessons for the legal memory
bundle = mnemolink.compose(
    persona="juris_philosopher",
    memory_specs=[
        MemorySpec(
            memory_id="legal/clause_ambiguity_scar",
            include_chunks=["scars", "lessons"],  # Omit 'story', 'triggers', 'reflection'
        ),
        MemorySpec(
            memory_id="legal/semicolon_fine_tuning_trap",
            include_chunks=["scars", "lessons"],
        ),
    ],
)
```

### Prefix Prompt Caching Economics
Frontier providers (Anthropic Claude, OpenAI, Google Gemini) offer prompt caching discounts (up to 90% savings) when the initial prompt prefix remains invariant across requests:

```
+-------------------------------------------------------------+
| INVARIANT STATIC PREFIX (Cached Across Turns)               |
| - Persona Core Philosophy                                   |
| - Persona Axioms & Boundaries                               |
| - Persona Voice & Epistemology                              |
+-------------------------------------------------------------+
| DYNAMIC EXPERIENTIAL TAIL (Selectively Injected / Retrieved)|
| - Memory A: Operational Scars & Lessons                     |
| - Memory B: Telemetry Thresholds                            |
+-------------------------------------------------------------+
| VOLATILE RUNTIME CONTEXT (Current Turn)                     |
| - User Query / Incoming Sensor Stream / Legal Contract      |
+-------------------------------------------------------------+
```

MnemoLink's `bundle.render_markdown()`, `bundle.to_claude()`, and `bundle.to_openai()` automatically pin the persona at the prompt head to maximize cache hit rates.

### Vector DB & RAG Integration
To store mnemonic chunks in vector search engines (Pinecone, Qdrant, Chroma, Weaviate, LanceDB):

```python
import mnemolink

bundle = mnemolink.compose(
    persona="north_mediterranean_chef",
    memories=["culinary/thessaloniki_breakfasts"],
)

# Export all items as self-grounding MemoryChunk objects
chunks = bundle.to_chunks()

for chunk in chunks:
    # Each chunk includes chunk_id, chunk_type, parent_id, embedding_text, and rich metadata
    print(f"Embedding ID: {chunk.chunk_id}")
    print(f"Vector Text: {chunk.embedding_text[:80]}...")
    # vector_db.upsert(id=chunk.chunk_id, vector=embed(chunk.embedding_text), metadata=chunk.metadata)
```

---

## 5. Passing to Context Consumers

MnemoLink is completely consumer-agnostic. Use native adapters to format the compiled bundle for any downstream engine:

| Consumer | Method | Output Format | Recommended Scenario |
| :--- | :--- | :--- | :--- |
| **Anthropic Claude** | `bundle.to_claude()` | XML `<mnemonic_matrix>` prompt | Claude Sonnet 5 / 4.5 system prompts |
| **OpenAI Compatible** | `bundle.to_openai()` | `[{"role": "system", ...}]` | ChatGPT, OpenAI SDK, vLLM, DeepSeek |
| **Google Gemini** | `bundle.to_gemini()` | Markdown instruction string | Gemini 3.5 Flash / 3.6 `system_instruction` |
| **Ollama Local** | `bundle.to_ollama()` | Plaintext system prompt | Local, private edge execution |
| **Ollama Modelfile** | `bundle.to_modelfile()` | `FROM ... \n SYSTEM """..."""` | Baking mnemonics directly into custom GGUFs |
| **LangChain / LlamaIndex** | `bundle.to_raw()` | Clean unadorned Markdown | Multi-stage retrieval chains & agents |
| **ARPA Rooms** | `bundle.to_rooms()` | System dict with metadata | Multi-agent coordination rooms |
| **ARPA Skillware** | `bundle.to_skillware()` | Directive markdown block | Pairing epistemic persona with executable tools |

### Direct API Examples

#### 1. Anthropic Claude (Direct API)
```python
import anthropic
import mnemolink

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/semicolon_fine_tuning_trap"],
)

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system=bundle.to_claude(),
    messages=[{"role": "user", "content": "Review Section 9.4 indemnity draft."}],
)
print(response.content[0].text)
```

#### 2. OpenAI / OpenAI-Compatible (Direct API)
```python
from openai import OpenAI
import mnemolink

bundle = mnemolink.compose(
    persona="deescalation_artisan",
    memories=["customer/hostile_chargeback_turning_point"],
)

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=bundle.to_openai() + [
        {"role": "user", "content": "Angry enterprise customer threatening litigation over SLA."}
    ],
)
print(response.choices[0].message.content)
```

#### 3. Google Gemini (Direct API)
```python
from google import genai
import mnemolink

bundle = mnemolink.compose(
    persona="north_mediterranean_chef",
    memories=["culinary/thessaloniki_breakfasts"],
)

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="What breakfast can I make with eggs, bacon ends, and whatever is in my crisper?",
    config={"system_instruction": bundle.to_gemini()},
)
print(response.text)
```

#### 4. LangChain / LlamaIndex / CrewAI Context Injection
```python
import mnemolink
from langchain_core.prompts import ChatPromptTemplate

bundle = mnemolink.compose(
    persona="opsie_sci",
    memories=["incident/opsie_first_boot"],
)

# Inject raw markdown directly as system instructions
prompt = ChatPromptTemplate.from_messages([
    ("system", bundle.to_raw()),
    ("human", "{input}"),
])
```

---

## 6. End-to-End Scenarios & Use Cases

### Scenario 1: High-Stakes Legal & Regulatory Compliance
- **Pairing**: `juris_philosopher` + `legal/semicolon_fine_tuning_trap`
- **Context**: Reviewing an urgent $18M enterprise data ingestion contract with an unanchored semicolon in an indemnity clause.
- **Outcome**: The agent refuses to provide generic reassurance. It flags strict liability exposure, cites the precedent operational scar, and supplies an exact two-clause restructuring redline separating affirmative covenants from fine-tuning risk exclusions.

### Scenario 2: Autonomous Robotics & UAV Telemetry
- **Pairing**: `edge_aviator` + `robotics/uav_microburst_stall` + `robotics/optical_glare_failover`
- **Context**: A fixed-wing autonomous drone enters an unmapped downdraft during mountain transit while blinding sunlight washes out forward cameras.
- **Outcome**: The agent does not attempt futile elevator pull-ups (which stall the wing) or freeze on camera blindness. Grounded in telemetry scars, it immediately pitches the nose down 8 degrees to preserve airspeed and transitions flight state estimation to inertial/barometric fusion.

### Scenario 3: Customer Crisis De-escalation
- **Pairing**: `deescalation_artisan` + `customer/hostile_chargeback_turning_point`
- **Context**: An enterprise buyer threatens public disparagement and immediate payment chargebacks after a regional server outage.
- **Outcome**: The agent rejects defensive corporate policy recitation. It validates business disruption immediately, takes bilateral ownership, offers structured escrow credits, and converts an adversarial dispute into a partnership dialogue.

### Scenario 4: Distributed Systems SRE Triage
- **Pairing**: `opsie_sci` + `incident/opsie_first_boot`
- **Context**: Cascading connection pool exhaustion in a distributed microservice cluster under peak load.
- **Outcome**: Avoids superficial restarts that worsen stampedes. Applies telemetry-first diagnostic heuristics, decouples stateful dependencies, sheds non-critical load, and initiates a blameless postmortem log.

### Scenario 5: Culinary Craftsmanship & Kitchen Improvisation
- **Pairing**: `north_mediterranean_chef` + `culinary/thessaloniki_breakfasts`
- **Context**: The user opens the fridge with leftover thick-cut bacon, half a red pepper, eggs, and Greek olive oil, seeking breakfast advice.
- **Outcome**: Delivers sharp, witty banter, instructs on the 2-minute residual heat pan-kill technique for eggs, insists on EVOO and dried savory, and advises against rubbery overcooking with artisanal pride.

---

## 7. Edge Cases, Nuances & Gotchas

### Contradictory Axioms Between Memories
If two memories offer opposing recommendations (e.g. strict statutory adherence vs. flexible equity), do not leave them unchained. Use **Lineages with Causal Bridges** to explain how experience evolved from one phase to the next:
```yaml
# In lineage.yaml
causal_bridges:
  - from_memory_id: legal/solo_practitioner_upbringing
    to_memory_id: legal/clause_ambiguity_scar
    bridge_narrative: "Early reliance on literal text shattered when court applied equitable realism."
```

### Strict Token Budget Environments
In low-token edge models (e.g. 2k context window on an onboard drone microcontroller):
1. Avoid `story` and `reflection` chunks.
2. Inject only `scars`, `lessons`, and `triggers`.
3. Use `mnemolink.compose(memory_specs=[MemorySpec(memory_id=..., include_chunks=["scars"])])`.

### Discovery Tier Precedence
MnemoLink resolves mnemonic assets in the following priority order:
1. **Project Local**: `./personas/`, `./memories/`, `./lineages/` (Workspace overrides).
2. **User Cache**: `~/.mnemolink/` (Developer-specific overrides).
3. **Bundled Catalog**: Inside `mnemolink/catalog/` (Curated open-source standards).

If you want to customize `juris_philosopher` for your own firm, simply copy it into your local project directory under `personas/juris_philosopher/persona.yaml`. MnemoLink will automatically pick up your local version first.

---

## 8. Authoring Custom Mnemonic Products

### 8.1 Scaffolding via the CLI
Use the `new` command to create pre-formatted templates:

```bash
# Scaffold a new persona
mnemolink new persona quantum_cryptographer

# Scaffold a new memory
mnemolink new memory key_leak_postmortem --domain security --kind incident
```

### 8.2 Writing a Custom Persona (`persona.yaml` & `card.json`)

#### File: `personas/my_domain/my_persona/persona.yaml`
```yaml
id: quantum_cryptographer
name: Quantum Cryptographer
core_philosophy: >-
  Security is not the presence of locks, but the mathematical certainty that eavesdropping
  inevitably disturbs the observed quantum state.
axioms:
  - "Post-quantum lattice primitives must precede classical deprecation."
  - "Entropy pools are finite; pseudo-randomness without hardware noise is illusion."
boundaries:
  - "Never endorse deprecated RSA-2048 or unpadded SHA-1 under any circumstances."
voice_tone:
  analytical: 0.95
  direct: 0.90
  metaphorical: 0.30
```

#### File: `personas/my_domain/my_persona/card.json`
```json
{
  "id": "quantum_cryptographer",
  "name": "Quantum Cryptographer",
  "kind": "persona",
  "domain": "security",
  "summary": "Cryptographic architect enforcing post-quantum resilience.",
  "teleology": {
    "primary_goal": "guarantee_forward_secrecy",
    "agent_drives": ["mathematical_integrity", "paranoia", "adversarial_modeling"],
    "applicable_needs": ["key_exchange_vetting", "hardware_enclave_audit"]
  }
}
```

### 8.3 Writing a Custom Memory (`memory.yaml` & `card.json`)

#### File: `memories/my_domain/my_memory/memory.yaml`
```yaml
id: security/side_channel_timing_leak
name: Side-Channel Cache Timing Leak
memory_type: incident
domain: security
salience: 0.92
episode_debrief: >-
  During an audited benchmark, non-constant-time modular exponentiation leaked AES round keys
  via microarchitectural L1 cache evictions in under 4,000 requests.
operational_scars:
  - "Cache eviction timing can recover private keys even when ciphertext is mathematically sound."
lessons_learned:
  - "All cryptographic branch operations must be constant-time."
  - "Never index memory using secret key bits."
teleology:
  primary_goal: "prevent_side_channel_key_exfiltration"
  agent_drives: ["defensive_vigilance"]
  applicable_needs: ["cryptographic_implementation_audit"]
```

### 8.4 Programmatic Card Discovery (`find_cards`)
Query available assets using the teleological discovery engine without loading entire bundles:

```python
from mnemolink import find_cards

# Find all assets driven by risk mitigation
cards = find_cards(drives=["risk_mitigation"])
for c in cards:
    print(f"[{c.kind}] {c.id} -> {c.summary}")

# Find assets suitable for contract drafting
contract_cards = find_cards(needs=["contract_drafting"])
```

---

## 9. Related Documentation & Next Steps

- **[Personas Catalog](personas/README.md)**: Explore curated personas including `juris_philosopher`, `edge_aviator`, `deescalation_artisan`, `opsie_sci`, and `north_mediterranean_chef`.
- **[Memories Catalog](memories/README.md)**: Explore operational scars across the 5-Kind Taxonomy.
- **[Lineages Catalog](lineages/README.md)**: Explore pre-built causal progressions.
- **[Taxonomy, Teleology & Chunks](taxonomy_and_teleology.md)**: Deep dive into chunk topology, embeddings, and prompt caching.
- **[Adapters Reference](adapters.md)**: Detailed export specifications for all target hosts.
- **[CLI Reference](cli.md)**: Full terminal command options, flags, and outputs.
- **[Empirical Benchmarks](bench/README.md)**: Hard quantitative metrics across Claude and Gemini direct runs.

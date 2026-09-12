# Command-Line Interface (CLI)

MnemoLink provides a command-line interface for exploring the catalog, inspecting personas and memories, assembling custom lineages, and running benchmarks.

---

## Installation & Availability

When you install `mnemolink`, the CLI binary is automatically registered:

```bash
pip install mnemolink
```

Verify the installation:

```bash
mnemolink --help
```

---

## Commands Reference

### 1. `list`

Lists all registered mnemonic products across all discovery tiers (`Project Local` &rarr; `User Cache` &rarr; `Bundled Catalog`).

```bash
# List everything in the catalog
mnemolink list

# Filter by kind: persona, memory, or lineage
mnemolink list --kind persona
mnemolink list --kind memory
mnemolink list --kind lineage

# Filter by domain
mnemolink list --domain legal
mnemolink list --domain robotics
mnemolink list --domain customer
```

### 2. `inspect`

Inspects the deep structure, philosophical axioms, operational scars, lessons, and teleology of any mnemonic product:

```bash
# Inspect a persona
mnemolink inspect juris_philosopher
mnemolink inspect edge_aviator
mnemolink inspect opsie_sci

# Inspect an episodic memory
mnemolink inspect legal/clause_ambiguity_scar
mnemolink inspect legal/semicolon_fine_tuning_trap
mnemolink inspect robotics/uav_microburst_stall

# Inspect a lineage
mnemolink inspect legal_crucible
mnemolink inspect flight_scars
```

### 3. `compose`

Assembles personas and memories into a unified context and exports it directly to any target host format:

```bash
# Compose and export as Anthropic Claude XML prompt
mnemolink compose -p edge_aviator -m robotics/uav_microburst_stall -f claude

# Compose and export as OpenAI / LiteLLM system messages
mnemolink compose -p juris_philosopher -m legal/clause_ambiguity_scar -f openai

# Compose and export as Ollama Modelfile
mnemolink compose -p juris_philosopher -m legal/clause_ambiguity_scar -f modelfile -o Modelfile

# Compose with automatic Lego lineage chaining
mnemolink compose -p edge_aviator -m robotics/uav_microburst_stall robotics/optical_glare_failover --build-lineage -f raw
```

Available format flags (`-f` / `--format`):
- `raw`: Unadorned Markdown context.
- `claude`: Anthropic XML block (`<mnemonic_matrix>`).
- `openai`: JSON-serialized system messages array.
- `gemini`: Clean markdown instruction string.
- `ollama`: Plaintext prompt for Ollama generation.
- `modelfile`: Self-contained Ollama Modelfile (`FROM ... \n SYSTEM """..."""`).
- `rooms`: Configuration dictionary for ARPA Rooms multi-agent engine.
- `skillware`: Directive block for ARPA Skillware tool pairing.

### 4. `new`

Scaffolds a new mnemonic product package with manifest template and companion markdown:

```bash
# Scaffold a new persona
mnemolink new persona quantum_physicist

# Scaffold a new episodic memory
mnemolink new memory aerospace_rudder_jam --domain robotics --kind incident
```

### 5. `bench`

Executes the MnemoLink simulation harness and resilience benchmark across challenging domain scenarios:

```bash
# Run in deterministic offline mock mode (no API keys required)
mnemolink bench --mock

# Run against Ollama local instance
mnemolink bench --ollama --model llama3.1
```

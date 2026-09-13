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

## Interactive Terminal Menu & Gradient Splash

When executed without arguments on an interactive terminal (TTY):

```bash
mnemolink
```

MnemoLink launches an interactive navigation menu featuring a 3-stop RGB pastel gradient splash screen (`#efcefa` &rarr; `#bae6fd` &rarr; `#bbf7d0`), ratio-spaced command dispatch with heavy borders, and graceful keyboard navigation:
- `[1] list` &mdash; Discover and display catalog assets with interactive filtering
- `[2] inspect` &mdash; Interactively inspect archetype axioms, episodic scars, and teleology
- `[3] compose` &mdash; Prompt-guided bundle composition with adapter format targeting
- `[4] bench` &mdash; Run empirical benchmark crucibles (offline mock or live model APIs)
- `[5] new` &mdash; Scaffold a new Persona, Memory, or Lineage template
- `[6] help` &mdash; Interactive drill-down submenus for architecture, commands, and adapters
- `[7] theme` &mdash; Switch CLI presentation palette (`pastel`, `ocean`, `mono`)
- `0` / `q` &mdash; Exit cleanly with zero traceback spills
- `b` &mdash; Step back to previous menu level

In non-interactive environments (such as CI pipelines or pipes `mnemolink | cat`), the CLI automatically detects non-TTY mode, outputs standard usage instructions, and exits with code 0 without hanging.

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

Executes the MnemoLink 4-tier progression A/B benchmark (Generic Baseline -> Persona -> Persona + Memory -> Delta) across 6 objective pillars:

```bash
# Run all 8 scenarios in deterministic offline mock mode (no API keys required)
mnemolink bench --mock

# Filter by scenario tier: micro, meso, or macro
mnemolink bench --mock --tier micro
mnemolink bench --mock --tier meso
mnemolink bench --mock --tier macro

# Export quantitative progression report to JSON
mnemolink bench --mock --export-json results/bench_report.json

# Run live against production model APIs (reads credentials from .env)
mnemolink bench --model claude-sonnet-5
mnemolink bench --model gemini-3.5-flash
mnemolink bench --model ministral-8b-latest

# Run against a local Ollama instance
mnemolink bench --model llama3.2:1b
```

---

## Local Developer Simulation Harness

For interactive multi-turn conversations and testing unreleased personas or memories with live model mounts prior to committing:

```bash
# Test a persona with an episodic memory against Claude
python scripts/simulate_asset.py -p juris_philosopher -m legal/semicolon_fine_tuning_trap --model claude-sonnet-5

# Interactive multi-turn interrogation loop
python scripts/simulate_asset.py -p edge_aviator -m robotics/uav_microburst_stall --interactive

# Test with Google Gemini or OpenAI
python scripts/simulate_asset.py -p opsie_sci -m sre/kubernetes_retry_storm --model gemini-3.5-flash
python scripts/simulate_asset.py -p chef_north_med -m culinary/thessaloniki_bougatsa_crisis --model gpt-5.6-luna
```


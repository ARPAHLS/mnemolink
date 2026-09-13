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

## Interactive menu

Running `mnemolink` with no arguments in an interactive terminal opens a gradient ASCII splash and a numbered menu (Skillware / AURA style):

```bash
mnemolink
```

| Input | Command | Action |
| :--- | :--- | :--- |
| `1` / `list` | list | Catalog table with optional kind and domain filters |
| `2` / `inspect` | inspect | Prompt for an asset id |
| `3` / `compose` | compose | Prompt for persona, memories, lineage, and export format |
| `4` / `bench` | bench | Interactive or automated 4-tier progression benchmark |
| `5` / `author` | author | Authoring Hub: AI Wizard, guided manual, or quick scaffold |
| `6` / `help` | help | Grouped topics, examples, and documentation links |
| `7` / `theme` | theme | Switch `pastel`, `ocean`, or `mono` (persists to config) |
| `8` / `config` | config | View and manage user settings, themes, and API credentials |

Navigation: `0` / `q` exits, `b` returns from a submenu, `Ctrl+C` prints `Bye.` with no traceback.

Piped or CI invocations (`mnemolink | cat`, GitHub Actions) are not a TTY: the CLI prints standard argparse usage and exits `0` without hanging.

The splash uses a 6-line MNEMOLINK block logo with a three-stop horizontal RGB gradient (`#efcefa` -> `#bae6fd` -> `#bbf7d0` in the default pastel theme) and the tagline `MnemoLink v{version} — Mnemonic Products Framework for Information Processors`.

---

## Configuration & Credential Persistence

MnemoLink provides user-level configuration and credential persistence across CLI sessions:

### 1. User Settings (`~/.mnemolink/config.yaml`)

Your terminal preferences, active theme, preferred execution model, and custom catalog directories are preserved in `~/.mnemolink/config.yaml`:

```yaml
theme: pastel
preferred_provider: gemini
model: gemini-3.5-flash
ollama_host: http://localhost:11434
author_name: Engineer
catalog_dirs:
  - /path/to/custom/catalogs
```

- **Theme Persistence**: When you select a theme via menu option `[7]` (`pastel`, `ocean`, or `mono`), it is automatically saved to `config.yaml` and restored on the next CLI launch.
- **Custom Catalog Directories**: Add custom directories to `catalog_dirs` to seamlessly discover your private personas, memories, and lineages alongside bundled assets.

### 2. Credential Resolution & 3-Tier Precedence (`~/.mnemolink/.env`)

When running live benchmarks or the AI Wizard, MnemoLink resolves API keys using a strict 3-tier hierarchy:

1. **Workspace `.env`**: `./.env` in the current working directory.
2. **User Global `.env`**: `~/.mnemolink/.env` in the user's home directory.
3. **Process Environment**: Existing environment variables (`os.environ`).
4. **Interactive Secure Prompt**: If no key is found anywhere, MnemoLink displays a rich tooltip with the direct console URL for the provider and prompts you to paste the key. The entered key is automatically saved to `~/.mnemolink/.env` so you only have to enter it once.

Key Management URLs:
- Google Gemini: `https://aistudio.google.com/app/apikey`
- Anthropic Claude: `https://console.anthropic.com/settings/keys`
- Mistral AI: `https://console.mistral.ai/api-keys/`
- OpenAI: `https://platform.openai.com/api-keys`
- Groq: `https://console.groq.com/keys`
- DeepSeek: `https://platform.deepseek.com/api_keys`

### 3. Dynamic Model Selection (Zero Hardcoded Models)

Models are never hardcoded. Whenever a model is needed (for the wizard or live bench), you choose your execution target:

- **Target [1]: Cloud Provider API**:
  Choose between Google Gemini, Anthropic Claude, Mistral AI, or OpenAI. The CLI displays the official documentation URL for that provider's model catalog along with current examples:
  - Google Gemini: `https://ai.google.dev/gemini-api/docs/models/gemini` (e.g. `gemini-3.5-flash`, `gemini-2.5-pro`)
  - Anthropic Claude: `https://docs.anthropic.com/en/docs/about-claude/models` (e.g. `claude-sonnet-5`, `claude-haiku-4.5`)
  - Mistral AI: `https://docs.mistral.ai/getting-started/models/` (e.g. `mistral-large-latest`, `ministral-8b-latest`)
  - OpenAI: `https://platform.openai.com/docs/models` (e.g. `gpt-5.6-luna`, `gpt-4o`)

  You enter or paste the exact model string you want to use. You can also save it as your preferred default in `~/.mnemolink/config.yaml`.

- **Target [2]: Local Ollama**:
  Offline local execution using your Ollama daemon (`http://localhost:11434` or custom `ollama_host`).
  - Displays library link: `https://ollama.com/library`
  - Shows pull command tooltip: `ollama pull <model>` (e.g. `ollama pull llama3.2:1b`)
  - Automatically queries your local daemon for installed models.
  - If the model you type is not found locally, the CLI warns you, lists your installed models, and lets you choose: use anyway, pick from installed models, or re-enter.

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

### 4. `author` / `wizard` (Authoring Studio & AI Scar Elicitation)

Launches the interactive Authoring Studio for creating new mnemonic products. Note the distinction: `author` is for **manufacturing and ingesting** new catalog assets (`.yaml` + `card.json` on disk), while `compose` is for **assembling and compiling** existing assets into target-model prompt formats.

```bash
# Launch the authoring studio (wizard alias also supported)
mnemolink author
mnemolink wizard

# Target a custom catalog directory
mnemolink author --dir ./my_catalog
```

Features:
- **Three Creation Paths**: Choose between conversational AI scar elicitation, guided manual interview, or fast template scaffolding.
- **Conversational Scar Elicitation**: Extracts genuine, non-obvious failure modes, cognitive boundaries, sensory cues, and teleological drives.
- **5-Kind Memory Taxonomy**: Generates memories strictly conforming to `lore`, `work`, `incident`, `relational`, or `telemetry`.
- **Dual Manifest Output**: Emits both the schema YAML (`persona.yaml`, `memory.yaml`, or `lineage.yaml`) and companion discovery card (`card.json`).
- **Self-Healing LLM Engine**: Automatically validates JSON structures and retries with targeted error feedback up to 3 times.

### 5. `new` (Quick Scaffold)

Quickly scaffolds template files for manual editing:

```bash
# Scaffold a new persona
mnemolink new persona quantum_physicist

# Scaffold a new episodic memory
mnemolink new memory aerospace_rudder_jam --domain robotics --kind incident
```

### 6. `bench`

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

# Run live against production model APIs (reads credentials from 3-tier precedence)
mnemolink bench --model gemini-3.5-flash
mnemolink bench --model claude-sonnet-5
mnemolink bench --model ministral-8b-latest

# Run against a local Ollama instance
mnemolink bench --model llama3.2:1b
```

### 7. `config`

Inspects and updates persistent user configuration (`~/.mnemolink/config.yaml`) and API credential precedence:

```bash
# Display active settings, file paths, and API credential status
mnemolink config

# Explicit show alias
mnemolink config show

# Update a setting from the command line
mnemolink config set theme ocean
mnemolink config set model gemini-3.5-flash
mnemolink config set ollama_host http://localhost:11434
mnemolink config set catalog_root /path/to/custom/catalogs
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
python scripts/simulate_asset.py -p chef_north_med -m culinary/thessaloniki_bougatsa_crisis --model gpt-4o
```


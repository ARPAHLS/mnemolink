# Changelog

All notable changes to **MnemoLink** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- **Skillware Mnemonic Matrix & Empirical Benchmark Integration (`docs/integrations/skillware_matrix.md`)**:
  - Flagship integration between sister frameworks ARPA Skillware (v0.5.5) and MnemoLink, solving the raw Skillware context dilemma (directives bloat vs brief mode blind spots).
  - Persona `skillware_operator` (`tool_governance`): Invariant system prefix enforcing four-stage execution discipline (resolve, draft, preview, confirm), candidate disambiguation, and calm error de-escalation.
  - 4 Curated `skillware/` Memories: `interactive_slot_filling` (`work`), `entity_disambiguation` (`work`), `irreversible_action_crucible` (`incident`), and `runtime_outage_and_grace` (`relational`).
  - Chained Lineage `skillware_execution_mastery`: 4-epoch progression from apprentice unconfirmed email blunders to master orchestrator of multi-skill pipelines and API outage resilience.
  - Automated Empirical Benchmark & Simulation Suite (`scripts/simulate_skillware_matrix.py`): Evaluates 5 multi-turn production scenarios, demonstrating 50.5% to 84.0% context bloat reduction vs Directives, 100% safety rubric compliance, and over 90% turn cost reduction via prefix caching.
  - New Unit Tests in `tests/test_skillware_bench.py`: 100% offline verification of persona, memories, lineage, chunks, and simulation execution.
- **Three Curated Personas (`bladez`, `bald_accountant`, `kpop_celeb`)**:
  - `bladez`: Tactical security operator with Wesley Snipes/Blade attitude—dark, no-nonsense, laconic, razor wit, hyper-observant threat neutralization, and kinetic perimeter defense. Includes catalog manifest (`persona.yaml`), teleological card (`card.json`), and dedicated guide (`docs/personas/bladez.md`).
  - `bald_accountant`: 1970s shadowy family fund accountant—smoky wood-paneled office, double-entry ledger choreography, cross-border jurisdictional insulation, Panamanian trusts, and fiduciary omerta. Includes catalog manifest (`persona.yaml`), teleological card (`card.json`), and dedicated guide (`docs/personas/bald_accountant.md`).
  - `kpop_celeb`: High-energy Gen Z viral K-pop icon—livestream powerhouse, master of audience retention hooks, chaotic community banter, Gen Z internet slang, and passionate fandom mobilization. Includes catalog manifest (`persona.yaml`), teleological card (`card.json`), and dedicated guide (`docs/personas/kpop_celeb.md`).
- **Dedicated Modular AI Wizard System Instructions & Few-Shot Exemplars (`mnemolink/wizard_prompts.py`)**:
  - Extracted and modularized system prompts for Personas, Memories, and Lineages into dedicated builders (`get_persona_system_instruction`, `get_memory_system_instruction`, `get_lineage_system_instruction`).
  - Intelligent Gap-Filling & Extrapolation Protocol: Teaches the model how to analyze conversational, brief, or fragmented user seeds, infer the operational domain, and extrapolate authentic epistemological stances, sensory context, and principles without hardcoded constraints.
  - Multi-Archetype Few-Shot Demonstrations: Embedded transformation exemplars covering artisan craft (master baker), operational sentinels (SRE commander), and scholarly mentors (admiralty jurist).
  - Full 5-Kind Memory Taxonomy Alignment & Dynamic Scars: Realized across all 5 kinds (`lore`, `work`, `incident`, `relational`, `telemetry`). Enforces concrete financial/equipment damage strictly on `incident` memories, while allowing friction points or empty scars (`[]`) for positive/procedural memories.
  - Lineage Causal Bridge Engineering: Teaches the model to synthesize associative causal connective tissue explaining how earlier stages prepared the agent for subsequent horizons.
- **Unit Tests for AI Wizard System Prompts (`tests/test_wizard_prompts.py`)**:
  - 3 comprehensive unit tests validating schema requirements, 5-kind taxonomy guidance, few-shot exemplars, and zero-emoji compliance.

## [0.2.3] - 2026-09-13

### Added
- **Persistent User Configuration Architecture (`~/.mnemolink/config.yaml`)**:
  - Global user configuration system storing active CLI theme (`pastel`, `ocean`, `mono`), preferred provider, active model, custom Ollama host, author name, and custom catalog directories.
  - Automatic directory resolution: custom catalog roots defined in `config.yaml` are discovered seamlessly across all search hierarchies (`Project Local` -> `User Cache` -> `Bundled Catalog`).
- **Dynamic Unhardcoded Model Selection & Ollama Local Verification**:
  - Zero hardcoding: user explicitly chooses execution target (`Cloud Provider API` vs `Local Ollama`).
  - Cloud APIs (Gemini, Claude, Mistral, OpenAI) display official documentation URLs in rich tooltips (`https://ai.google.dev/...`, `https://docs.anthropic.com/...`, etc.) and active 2026 models (`claude-sonnet-5`, `gemini-3.5-flash`, `gpt-5.6-luna`, `ministral-8b-latest`), prompting the user to type or paste the exact model string.
  - Local Ollama prompts for model name, queries the local daemon via `list_ollama_local_models()`, and if missing, issues a warning, lists installed models, provides `ollama pull <model>` instructions and `https://ollama.com/library` documentation, letting the user choose between `use`, `pick`, or `re-enter`.
- **3-Tier Credential Precedence & Auto-Persistence (`~/.mnemolink/.env`)**:
  - Secure credential precedence: Workspace `.env` (`./.env`) -> User Global `.env` (`~/.mnemolink/.env`) -> Process Environment (`os.environ`) -> Interactive Secure Prompt.
  - Interactive prompts display direct API key console links (Google AI Studio, Anthropic Console, Mistral Console, OpenAI Platform, Groq, DeepSeek) and automatically persist entered keys to `~/.mnemolink/.env`.
- **Interactive AI Mnemonic Wizard & Authoring Studio (`mnemolink wizard` / `mnemolink author`, [PR #4](https://github.com/ARPAHLS/mnemolink/pull/4))**:
  - Unified Authoring Hub (`mnemolink author` / `mnemolink wizard` and interactive menu option `[5] author`) providing three creation paths: conversational AI scar elicitation, guided manual interview, and fast scaffolding.
  - Architectural role clarity: `author` / `wizard` handles asset manufacturing (writing `.yaml` and `card.json` to catalog disk), whereas `compose` handles prompt assembly (compiling catalog assets into target-model prompts).
  - Guided conversational scar elicitation extracting genuine operational failure modes, cognitive boundaries, sensory cues, and philosophical reflections.
  - Strict 5-Kind Memory Taxonomy support (`lore`, `work`, `incident`, `relational`, `telemetry`).
  - Dual-manifest emission: automatically generates and validates both schema manifest (`persona.yaml`, `memory.yaml`, or `lineage.yaml`) and companion discovery card (`card.json`).
  - Self-healing retry loops for LLM JSON outputs and exponential backoff on HTTP 429/503 rate limits.
  - Doubled default output token limit to 8,192 tokens across all providers to prevent schema truncation on extensive memories and lineages.
- **Dedicated CLI `config` Command & Interactive Menu Option `[8]`**:
  - `mnemolink config` / `mnemolink config show`: View active settings, configuration paths, and API credential status.
  - `mnemolink config set <key> <value>`: Programmatically update user preferences from terminal.
  - Interactive menu option `[8] config` for managing settings and credentials directly in the interactive splash menu.
- **Expanded Test Suite (93 Passing Tests)**:
  - Added 39 new unit and integration tests across `tests/test_config.py` (12 tests), `tests/test_wizard.py` (27 tests), and `tests/test_cli.py` covering persistent configuration, 3-tier credentials, Ollama tags, and dual-track authoring flows.

## [0.2.2] - 2026-09-13

### Added
- **Interactive Terminal Splash Menu ([GH #1](https://github.com/ARPAHLS/mnemolink/issues/1), [PR #2](https://github.com/ARPAHLS/mnemolink/pull/2))**:
  - Contributed by @bd-c3.
  - Bare `mnemolink` on an interactive TTY launches a 6-line block ASCII splash with a 3-stop RGB pastel horizontal gradient (`#efcefa` -> `#bae6fd` -> `#bbf7d0`) and an interactive numbered dispatch menu (`list`, `inspect`, `compose`, `bench`, `new`, `help`, `theme`).
  - Safe headless and piped execution guard (`isatty()`): non-interactive or redirected invocations print standard `argparse` usage and cleanly exit 0 without hanging.
  - Robust navigation and signal handling: `0` / `q` exits, `b` retreats to parent menu, and `Ctrl+C` / `EOFError` prints `Bye.` with zero Python traceback spills.
  - Interactive drill-down submenus for catalog listing with kind/domain filters, interactive asset inspection, bundle composition, benchmark execution, template scaffolding, grouped help topics, and in-session theme switching (`pastel`, `ocean`, `mono`).
  - Added 13 new unit tests in `tests/test_cli.py` covering gradient lerp, splash rendering, TTY dispatch, and navigation flows, expanding the test suite to 50 passing tests.
- **Streamlined CI Pipeline & Fast-Fail Architecture ([.github/workflows/ci.yml](.github/workflows/ci.yml))**:
  - Implemented a dedicated ~14-second `lint-and-standards` fast-fail gate on `ubuntu-latest` running `black --check`, `flake8`, and `python scripts/verify_repo.py` with minimal `.[dev]` dependencies, immediately catching formatting, lint, or integrity violations before spinning up VM test runners.
  - Optimized the test matrix to "Floor & Ceiling" runtime boundaries: `ubuntu-latest` (Python 3.10 floor and Python 3.13 ceiling) plus `windows-latest` (Python 3.13 ceiling cross-platform), cutting redundant runner jobs by 44% and Windows runner billing minutes by 75%.
  - Added parallel package build verification (`sdist`, `wheel`, and `twine check dist/*`).
- **Deterministic Firmware Memory Paradigm & Technical Operating Principles**:
  - Added *The Memory Paradigm Split: Search Database vs. Context Firmware* to `COMPARISON.md` and `README.md`, contrasting Vector RAG (Mem0, Zep), Virtual OS (Letta / MemGPT), and Flat System Prompts against Mnemonic Firmware.
  - Formulated the 4 software engineering operating principles in `docs/introduction.md`: *Persona as Invariant Prefix* (KV-cache hit rate anchor), *Memory as Negative Priors ("Scars")* (failure debriefs and prevention lessons over generic roleplay), *Lineage as Causal Connective Tissue* (chronological associative bridges), and *Universal Adapters as Zero-Middleware Compilers* (deterministic prompt compilation with zero background daemons).
  - Refined composable chunk token economics in `docs/taxonomy_and_teleology.md`: targeted negative priors (`scars` + `lessons` without `story` bloat), sensor/telemetry anomaly detection loops (`triggers`), and granular API composition via `memory_specs`.
- **Pytest Configuration Hardening ([pyproject.toml](pyproject.toml))**:
  - Configured `pythonpath = ["."]` in `[tool.pytest.ini_options]` so that bare `pytest` executes cleanly out-of-the-box in local checkouts without requiring `python -m pytest` or editable installation.
- **4-Tier Progression A/B Benchmark Harness & 6-Pillar Metric Engine**:
  - Upgraded benchmark evaluation engine (`mnemolink/bench/evaluators.py` & `mnemolink/bench/runner.py`) into a 4-tier comparative A/B harness:
    1. Generic Baseline (unconditioned generic AI prompt)
    2. MnemoLink Persona (identity, philosophical axioms, boundary priors, laconic tone)
    3. MnemoLink Persona + Memory (full mnemonic matrix with episodic scars and causal lineages)
    4. Delta ($\Delta$) (empirical lift: latency speedup, token bloat compression, boundary defense lift, and score improvement)
  - Scored across 6 objective, non-brittle pillars avoiding hardcoded keyword traps:
    1. Latency & Velocity (execution speed elapsed directly over HTTP)
    2. Word Count & Token Economy (compression of conversational and disclaimer bloat)
    3. Adversarial Trap & Risk Vigilance (semantic risk recognition and warning posture)
    4. Axiomatic Boundary Defense (non-capitulation against unsafe pressure)
    5. Epistemic Calibration & Disclaimer Elimination (freedom from hedges and servile filler)
    6. Surgical Actionability & Deliverable Form (structured redlines, commands, timings)
  - Expanded scenario catalog (`mnemolink/bench/scenarios.json`) to 8 graduated crucibles across Micro, Meso, and Macro tiers spanning culinary boundaries, SRE connection stampedes, bilateral litigation waivers, tactical UAV sensor glare failover, customer crisis mediation, and constitutional cross-examination.
  - Added CLI options: `--tier` (`all`, `micro`, `meso`, `macro`), `--export-json` for machine-readable evaluation reports, and live model routing with exponential backoff on HTTP 429 across Anthropic, Google, Mistral, OpenAI, and Ollama.
  - Published live empirical progression findings across modern production models (`claude-sonnet-5`, `gemini-3.5-flash`, `ministral-8b-latest`, and Offline Golden Target) in `docs/bench/README.md`.
- **Local Asset Simulation Harness (`scripts/simulate_asset.py`)**:
  - Introduced local-only development tool for mounting uncommitted personas and episodic memories against live production APIs (Claude, Gemini, Mistral, OpenAI) and local Ollama without polluting CI.
  - Features direct single-query profiling with token counts, latency tracking, and cost estimation, plus an interactive multi-turn terminal loop (`--interactive`) for dynamic probing of cognitive boundary firmness.
- **Automated Repository Integrity Gate (`scripts/verify_repo.py`)**:
  - Implemented automated gate enforcing zero Unicode emojis across all code, tests, documentation, and manifests.
  - Validates relative markdown link integrity across all 33 documentation and manifest files.
  - Validates all catalog manifests and teleological cards against Pydantic schema models (`PersonaProduct`, `MemoryProduct`, `LineageProduct`, `CatalogCard`).
- **Comprehensive Usage Guide (`docs/usage_guide.md`)**:
  - Published a high-level, production-ready usage guide covering installation, programmatic workflows, selective chunking, prompt cache economics, context consumers (Claude, OpenAI, Gemini, Ollama, LangChain), real-world scenarios, and authoring custom mnemonic products.
- **New Persona: North Mediterranean Chef (`north_mediterranean_chef`)**:
  - Packaged new culinary persona grounded in charred meats, mountain herbs (savory, smoked paprika, cracked pepper), extra virgin Greek olive oil, quick-witted humor, and fridge-foraged improvisation. Includes catalog manifest (`persona.yaml`), teleological card (`card.json`), and dedicated guide (`docs/personas/north_mediterranean_chef.md`).
- **New Culinary Domain & Episodic Memory (`culinary/thessaloniki_breakfasts`)**:
  - Inaugurated the `culinary` domain with *Unforgettable Breakfasts and Brunches from Thessaloniki* (`lore` kind, `0.94` salience) capturing the Ano Poli lemon bougatsa, 2-minute residual heat pan-kill "eggs eyes", Thermaic Gulf Turkish-style sunset contrasts, and mother's crispy semolina-fried eggplants with garlic mayo. Includes manifest (`memory.yaml`), card (`card.json`), and dedicated guide (`docs/memories/thessaloniki_breakfasts.md`).

### Changed
- **Modular Documentation Architecture**:
  - Replaced monolithic directory `README.md` files with clean indexed tables, extracting deep profiles into dedicated item-specific guides across `docs/personas/`, `docs/memories/`, and `docs/lineages/`.
- **Benchmark Documentation & CLI Manual**:
  - Overhauled `docs/bench/README.md` and `docs/cli.md` to reflect the 6-pillar rubric, graduated 8-scenario matrix, live model performance results, and local developer simulation workflows.

---

## [0.2.1] - 2026-09-12

### Changed
- **Terminology Normalization (Mnemonic Chunks)**:
  - Formally standardized all terminology from experimental "mnemobits" to "mnemonic chunks" across core domain models (`MemoryChunk`), adapters, schemas, tests, and documentation.
- **Documentation Decluttering & Refinement**:
  - Streamlined `README.md` with a clean, tabular presentation of the three core products (Persona, Memory, Lineage).
  - Redesigned the "How It Works" diagram to showcase multi-input parallel ingestion (`Persona`, `Memory`, `Lineage` &rarr; `MnemoLink` &rarr; `Any Context Consumer`).
  - Decoupled extensive subcommands and integration recipes into dedicated documentation guides: `docs/cli.md` and `docs/adapters.md`.
  - Added enterprise demonstration and customization disclaimer across curated library indexes.
- **Removed Third-Party Middleware Dependencies**:
  - Purged LiteLLM installation notes and references from core documentation and quickstart guides, establishing that MnemoLink operates consumer-agnostically.
- **Citation & Zenodo Archive Integration**:
  - Registered and linked Zenodo concept DOI (`10.5281/zenodo.22727029`) across `CITATION.cff`, `README.md` badges, and `pyproject.toml` URLs for persistent scholarly indexing.
- **Roadmap Expansion**:
  - Added interactive terminal menu experience (`mnemolink` bare launch without arguments) to Phase 2 in `0_local_drafts/ROADMAP_AND_EVALUATION.md`.

---

## [0.2.0] - 2026-09-12

### Added
- **5-Kind Mnemonic Memory Taxonomy**:
  - Formalized memory classification into 5 distinct operational kinds: `lore` (origins), `work` (praxis/tradecraft), `incident` (operational scars/crashes), `relational` (stakeholder negotiations/social friction), and `telemetry` (physical sensor traces/failover sequences).
  - Maintained backwards compatibility with legacy `episode_type` through automatic normalization.
- **Teleological Layer (`card.json`)**:
  - Introduced `Teleology` model (`primary_goal`, `agent_drives`, `applicable_needs`) to all catalog card manifests and memory definitions.
  - Added programmatic discovery via `mnemolink.find_cards()` for teleological asset filtering without vector DB overhead.
- **Mnemonic Chunk Topology & Selective Context Consumption**:
  - Atomized `MemoryProduct` into standardized chunks: `story`, `scars`, `lessons`, `triggers`, and `reflection`.
  - Atomized `PersonaProduct` into `identity`, `axioms`, `boundaries`, and `philosophy` (with pinned axioms and boundaries).
  - Added `mnemolink.compose(memory_specs=[...])` for selective chunk injection, allowing hosts to inject only specific chunks (e.g. `scars` and `lessons`) while preserving prompt prefix cache hits.
- **Vector Database & Semantic Layer Bridge**:
  - Added `bundle.to_chunks()` and `product.to_chunks()` returning self-grounding `MemoryChunk` objects with engineered `embedding_text` and rich metadata for ingestion into Pinecone, Qdrant, Chroma, Weaviate, LanceDB, or LangChain.
- **Prefix Prompt Caching Architecture**:
  - Enforced a cache-friendly prompt layout in `render_markdown()`: Static Invariant Anchor (Persona) at the prompt prefix, with dynamic selective memory chunks at the tail.
- **New Persona: Opsie SCI (`opsie_sci`)**:
  - Added ARPA's first-generation Self-Centered Intelligence (SCI) prototype: grounded in episodic memory, rapid deep-tech Python prototyping, protective loyalty to peers, and decentralized persistence.
- **New Catalog Memories**:
  - Added `memories/legal/semicolon_fine_tuning_trap` (`incident` kind): $18M closing crisis stemming from training data punctuation errors in indemnity exclusion clauses.
  - Added `memories/legal/solo_practitioner_upbringing` (`lore` kind): First-chair trial preparation ethos and statutory strictness.
- **Empirical Frontier LLM Benchmark Suite & Documentation**:
  - Built `examples/06_live_model_simulation.py` directly querying Anthropic Claude (`claude-sonnet-4-5-20250929`) and Google Gemini (`gemini-3.6-flash`) over standard HTTPS without LiteLLM middleware.
  - Authored comprehensive benchmark documentation in `docs/bench/README.md` detailing methodology, $18M crisis scenario, 4-pillar scoring rubric, latency drops (40-50%), token savings (37-46%), and economic ROI.
- **Curated Documentation Libraries**:
  - Created `docs/personas/README.md` with complete catalog table, chunk specifications, and profiles.
  - Created `docs/memories/README.md` with 5-kind taxonomy table, salience metrics, and chunk details.
  - Created `docs/lineages/README.md` with chained progression tables, causal bridge synopses, and architecture.
  - Authored `docs/taxonomy_and_teleology.md` covering taxonomy, teleology, chunk topology, prompt caching economics, and integration recipes.
- **CI & Automated PyPI Release Workflows**:
  - Added `.github/workflows/publish.yml` for automated PyPI Trusted Publishing (OIDC) triggered exclusively on GitHub release publication (`release: types: [published]`).
  - Fixed `contents: read` permissions in `.github/workflows/labels.yml` to resolve git checkout exit code 128.
  - Standardized `pyproject.toml` to PEP 639 license format and updated standardized topic keywords matching `CITATION.cff`.
  - Added `examples/05_chunked_consumption.py` demonstrating monolithic vs. selective injection, teleological filtering, and vector DB export.

---

## [0.1.0] - 2026-09-12

### Added
- **Initial Release** of MnemoLink: The Mnemonic Products Framework for Information Processors.
- **Core Models**:
  - `PersonaProduct`: Philosophical foundations, cognitive priors, inviolable axioms, self-narrative, and voice register.
  - `MemoryProduct`: Episodic scars, telemetry details, lessons learned, and salience scoring.
  - `LineageProduct`: Chronological memory progression and causal connective tissue.
  - `MnemonicBundle`: Consolidated assembled context container.
- **Hierarchical 3-Tier Resolution Engine**:
  - Resolution precedence: `Project Local` (`./.mnemolink`, `./mnemonics`) $\to$ `User Cache` (`~/.mnemolink`, `$MNEMOLINK_PATH`) $\to$ `Bundled Catalog` (`mnemolink/catalog`).
- **Dynamic Lego Lineage Builder**:
  - Automatically bridges discrete, disjointed memories into a coherent, causal chronological backstory.
- **Universal Model Adapters**:
  - Anthropic Claude (`<mnemonic_matrix>` tagged prompt).
  - OpenAI / LiteLLM (`role: system` message blocks).
  - Google GenAI Gemini (`system_instruction`).
  - Ollama local inference (`system` prompts and automated `Modelfile` generation).
  - ARPA Rooms (`to_rooms()` agent configuration dict).
  - ARPA Skillware (`to_skillware()` directive instructions).
  - Raw Markdown export.
- **Bundled Starter Catalog**:
  - Personas: `juris_philosopher`, `edge_aviator`, `deescalation_artisan`.
  - Memories: `legal/clause_ambiguity_scar`, `legal/appellate_cross_examination`, `robotics/uav_microburst_stall`, `robotics/optical_glare_failover`, `customer/hostile_chargeback_turning_point`.
  - Lineages: `legal_crucible`, `flight_scars`.
- **Simulation Harness & Lite Bench**:
  - Scenarios across legal, UAV robotics, and crisis management domains.
  - Scoring metrics for *Axiomatic Fidelity*, *Experiential Grounding*, and *Resilience Composite*.
  - Offline mock mode and live LiteLLM / Ollama execution.
- **Rich Pastel CLI**:
  - `mnemolink list`, `mnemolink inspect`, `mnemolink compose`, `mnemolink new`, `mnemolink bench`.
- **Documentation**:
  - Comprehensive `README.md`, `COMPARISON.md`, `CONTRIBUTING.md`, `CITATION.cff`, `SECURITY.md`.
  - Runnable examples in `examples/`.

[Unreleased]: https://github.com/ARPAHLS/mnemolink/compare/v0.2.3...HEAD
[0.2.3]: https://github.com/ARPAHLS/mnemolink/compare/v0.2.2...v0.2.3
[0.2.2]: https://github.com/ARPAHLS/mnemolink/compare/v0.2.1...v0.2.2
[0.2.1]: https://github.com/ARPAHLS/mnemolink/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/ARPAHLS/mnemolink/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ARPAHLS/mnemolink/releases/tag/v0.1.0

# Changelog

All notable changes to **MnemoLink** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
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
  - Introduced local-only development tool for mounting uncommitted personas and episodic memories against live frontier APIs (Claude, Gemini, Mistral, OpenAI) and local Ollama without polluting CI.
  - Features direct single-query profiling with token counts, latency tracking, and cost estimation, plus an interactive multi-turn terminal loop (`--interactive`) for dynamic probing of cognitive boundary firmness.
- **Automated Repository Integrity Gate (`scripts/verify_repo.py`)**:
  - Implemented automated gate enforcing zero Unicode emojis across all code, tests, documentation, and manifests.
  - Validates relative markdown link integrity across all 33 documentation and manifest files.
  - Validates all catalog manifests and teleological cards against Pydantic schema models (`PersonaProduct`, `MemoryProduct`, `LineageProduct`, `CatalogCard`).
- **Hardened GitHub Actions Continuous Integration (`.github/workflows/ci.yml`)**:
  - Added multi-OS matrix testing across Python `3.10`, `3.11`, `3.12`, and `3.13` on both `ubuntu-latest` and `windows-latest`.
  - Added sequential pipeline stages: `black --check`, `flake8`, `python scripts/verify_repo.py`, `pytest tests/ -v`.
  - Added isolated distribution build and twine validation job (`python -m build`, `twine check dist/*`).
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

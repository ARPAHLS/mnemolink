# Changelog

All notable changes to **MnemoLink** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2026-09-12

### Added
- **5-Kind Mnemonic Memory Taxonomy**:
  - Formalized memory classification into 5 distinct operational kinds: `lore` (origins), `work` (praxis/tradecraft), `incident` (operational scars/crashes), `relational` (stakeholder negotiations/social friction), and `telemetry` (physical sensor traces/failover sequences).
  - Maintained backwards compatibility with legacy `episode_type` through automatic normalization.
- **Teleological Layer (`card.json`)**:
  - Introduced `Teleology` model (`primary_goal`, `agent_drives`, `applicable_needs`) to all catalog card manifests and memory definitions.
  - Added programmatic discovery via `mnemolink.find_cards()` for teleological asset filtering without vector DB overhead.
- **Mnemobit Chunk Topology & Selective Context Consumption**:
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

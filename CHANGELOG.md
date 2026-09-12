# Changelog

All notable changes to **MnemoLink** will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

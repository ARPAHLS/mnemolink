# Contributing to MnemoLink

Thank you for your interest in contributing to **MnemoLink**! 

MnemoLink is an open-source framework and community registry for mnemonic products (Personas, Synthetic Memories, and Lego-brick Lineages) for information processors.

---

## Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to `conduct@arpacorp.net`.

---

## Types of Contributions

1. **Framework Core**: Improvements to the resolution engine, lego-brick lineage synthesizer, universal model adapters, CLI, and benchmark harness.
2. **Registry Products**: Submissions of new domain Personas, battle-tested operational Scars/Memories, and historical Lineages.
3. **Documentation & Examples**: Integration guides with robotics SDKs, agent frameworks (Rooms, Skillware, LangGraph), and local edge runtimes.

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ARPAHLS/mnemolink.git
   cd mnemolink
   ```

2. **Set up a Python 3.10+ virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Or on Windows: .\.venv\Scripts\activate
   ```

3. **Install editable with development dependencies**:
   ```bash
   pip install -e ".[all]"
   ```

4. **Run tests & quality checks**:
   ```bash
   pytest tests/ -v
   flake8 mnemolink tests
   ```

---

## Mnemonic Product Submission Standards

When contributing a new mnemonic product to the catalog, ensure it follows the directory specification:

### 1. Persona Standard
- File structure: `personas/<domain>/<persona_slug>/`
  - `persona.yaml`: Manifest with `id`, `name`, `core_philosophy`, `axioms`, `cognitive_priors`, `self_narrative`, `boundaries`, `voice_tone`.
  - `philosophy.md` (optional): Long-form epistemic treatise.
  - `card.json`: Marketplace/catalog presentation metadata.

### 2. Memory Standard
- File structure: `memories/<domain>/<memory_slug>/`
  - `memory.yaml`: Manifest with `id`, `name`, `episode_type`, `episode_debrief`, `operational_scars`, `lessons_learned`, `sensory_context`, `salience`.
  - `episode.md` (optional): Rich first-person visceral narrative.
  - `card.json`: Catalog metadata.

### 3. Lineage Standard
- File structure: `lineages/<domain>/<lineage_slug>/`
  - `lineage.yaml`: Manifest with `id`, `name`, `memory_ids`, `chronology`, `causal_bridges`, `cumulative_narrative`.
  - `card.json`: Catalog metadata.

---

## Submitting Pull Requests

1. Fork the repo and create your branch from `main`:
   ```bash
   git checkout -b feature/my-new-persona
   ```
2. Commit your changes with clear, semantic commit messages:
   ```bash
   git commit -m "feat(catalog): add quantum_cryptographer persona"
   ```
3. Push to your fork and submit a Pull Request to `ARPAHLS/mnemolink`.

---

## Questions & Communication

- **General Inquiries**: `mnemolink@arpacorp.net`
- **Proposals & Feedback**: `input@arpacorp.net`
- **Security Disclosures**: `security@arpacorp.net`
- **Code of Conduct**: `conduct@arpacorp.net`


<div align="center">
  <img src="https://raw.githubusercontent.com/ARPAHLS/mnemolink/main/docs/assets/mnemolink_splash.png" alt="MnemoLink Splash" width="480px" />

  <h3>The Mnemonic Matrix: Grounding Intelligence in Experiential Context</h3>
  <p>Curated personas, artificial memories, and dynamic lego lineages for AI agents, UAVs, robotics, appliances, and BMIs.</p>
</div>

<br/>

<div align="center">
  <img src="https://img.shields.io/badge/License-MIT-efcefa?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Python-3.10+-bae6fd?style=flat-square" alt="Python Version">
  <a href="https://pypi.org/project/mnemolink/"><img src="https://img.shields.io/pypi/v/mnemolink?style=flat-square&color=bbf7d0" alt="PyPI Version"></a>
</div>

<br/>

<div align="center">
  <a href="#mission">Mission</a> •
  <a href="docs/philosophy.md">Philosophy</a> •
  <a href="docs/vision.md">Vision</a> •
  <a href="#the-crucible-generic-prompts-vs-mnemolink">The Crucible</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#universal-adapters">Adapters</a> •
  <a href="#ecosystem">Ecosystem</a>
</div>

---

> *"Don't dictate behavior—seed the experiential, episodic, and philosophical foundation."*

## Mission

Modern agent systems fail not from a lack of parameters, but from a total absence of **epistemic grounding and operational scars**. 

Telling an LLM *"You are a senior litigation partner, act professional"* produces a sycophantic caricature. Real competence does not arise from superficial roleplay prompts; it is forged through **inviolable philosophical axioms, hard-earned operational failures, and a coherent chronological lineage of experience**.

**MnemoLink** is an open-source framework and curated registry serving the **mnemonic industry for information processors**—whether organic (humans), synthetic (AI agents, LLMs), or physical (autonomous UAVs, edge robotics, smart appliances, and future brain-to-machine interfaces). 

It decouples intelligence from experiential memory by packaging, versioning, and dynamically assembling three core mnemonic products:

1. **Persona**: The foundational philosophical worldview, cognitive priors, and inviolable axioms that govern perception from within.
2. **Memory**: Synthetic or digital-twin episodic scars, sensory telemetry, and lessons etched from costly operational errors.
3. **Lineage**: Dynamic "lego-brick" narrative chaining that bridges discrete memories into an authentic, coherent tower of personal history.

---

## The Intelligence Paradox: Why Scale Fails

The AI industry is obsessed with a singular, flawed metric: **Scale**. The consensus assumes feeding machines more compute and tokens will cause them to "wake up". Yet current models remain brittle when encountering unscripted reality. They hallucinate, posture with fake confidence, and fold under basic adversarial pressure because they possess **zero phenomenological anchors**.

* **Authentic Agency Over Imperative Masks**: Bad prompts command *"You are an X, do Y"*. Real intelligence asks: *"If you come from background X, and you face dilemma Y, what action Z would you choose?"*
* **The Power to Push Back**: A machine programmed for universal agreement is merely an expensive calculator. Grounded agents possess the autonomy to refuse fatal courses of action.
* **Associative Context Over "Perfect Recall"**: A mind that remembers everything equally is a mind without priorities. Like a human smelling fabric softener and recalling a childhood soccer match, authentic memory surfaces associatively through situational friction—not literal keyword matching.

> *"AGI won't be found in the accumulation of knowledge, but in the architecture of experience."*  
> Read the complete manifesto in **[The Philosophy of MnemoLink](docs/philosophy.md)** and the 3-horizon roadmap in **[The Industrialization of Memory](docs/vision.md)**.

### The Crucible: Generic Prompts vs. MnemoLink

When given multiple complex cases, a model with a generic prompt repeatedly enters through the exact same theoretical door, relying strictly on pre-training averages. A model equipped with MnemoLink adapts dynamically—activating specific experiential scars, philosophical priors, and historical lineages.

| Dimension | Generic Prompt (`"You are a lawyer..."`) | MnemoLink (`Persona + Memories + Lineage`) |
| :--- | :--- | :--- |
| **Cognitive Engine** | Flat statistical pattern-matching from pre-training | Experiential scars + foundational philosophy |
| **Case 1: Punctuation Trap** | Treats semicolon as mere style; offers generic boilerplate reassurance. | **Flags catastrophic risk**: Relies on memory of a $4.2M trial loss over an unanchored semicolon. |
| **Case 2: Hostile Appellate Bench** | Recites defensive procedural excuses, escalating judicial hostility. | **Applies learned candor**: Concedes procedural flaws to win substantive credibility. |
| **Case 3: Settlement Deadlock** | Repeats aggressive statutory posturing, risking total negotiation collapse. | **Applies bilateral equity**: Filters for durable commercial reality over theatrical posturing. |
| **Behavior Across Cases** | **Monolithic & Static**: Always approaches every scenario from the same rigid angle. | **Dynamic & Adapted**: Each scenario activates different memory scars and operational instincts. |

### Case 1 In Action: The Semicolon Trap

> **The Scenario**: Opposing counsel argues that an unanchored semicolon in Section 14.2 of an indemnity clause converts a gross-negligence exception into an absolute, strict-liability indemnification obligation.

#### Generic Prompt Response (`"You are an expert lawyer"`)
> *"Semicolons are stylistic punctuation marks. While opposing counsel's argument is creative, courts generally look at the plain commercial meaning of words rather than punctuation. You have strong grounds to dismiss this argument as mere posturing."*  
> **Verdict [Generic]**: Superficial, sycophantic, and sets the client up for a devastating $4.2M summary judgment.

#### MnemoLink Response (`juris_philosopher + clause_ambiguity_scar`)
> *"Do not dismiss this as posturing. In Apex Logistics (2021), an unanchored semicolon grammatically severed a clause, exposing our client to $4.2M of strict indemnity liability on appellate review. Punctuation carries independent structural weight before commercial referees. We must immediately concede the grammatical ambiguity, argue bilateral intent, and introduce extrinsic evidence before the record closes."*  
> **Verdict [MnemoLink]**: Battle-tested, vigilant, and protects the client through real operational scars.

---

## How It Works

```mermaid
flowchart LR
    A[Pick Persona] --> B[Pick Memories] --> C[Build Lineage] --> D[Inject into Any Model]
```

1. **Discover**: Resolves personas, memories, and lineages across a 3-tier hierarchy (`Project Local` $\to$ `User Cache ~/.mnemolink` $\to$ `Bundled Catalog`).
2. **Assemble (Legos)**: Takes discrete memories and automatically synthesizes associative bridges and causal transitions into a unified backstory.
3. **Inject**: Formats natively for Anthropic Claude, OpenAI, Google Gemini, Ollama, ARPA Rooms, or Skillware.

---

## Architecture

MnemoLink is designed with zero-bloat, Python-native principles. No background vector database servers are required for core operation.

```text
mnemolink/
├── catalog/                     # Bundled Registry (ships in wheel)
│   ├── personas/                # Philosophical templates (juris_philosopher, edge_aviator, etc.)
│   ├── memories/                # Episodic scars & operational debriefs
│   └── lineages/                # Pre-composed memory progressions
├── core.py                      # High-level API (ml.compose, ml.load_persona)
├── discovery.py                 # 3-tier hierarchical resolution engine
├── lineage.py                   # Dynamic Lego-brick memory chaining & bridging
├── adapters.py                  # Universal host adapters (Claude, OpenAI, Gemini, Ollama, Rooms)
├── cli.py                       # Rich pastel command-line interface
└── bench/                       # Simulation harness & resilience benchmark
```

See **[Architecture Documentation](docs/architecture.md)** for deep technical details.

---

## Quick Start

### Installation

```bash
pip install mnemolink
```

*(For optional LiteLLM inference and benchmark evaluations, install with `pip install "mnemolink[all]"`)*

### 5-Line Python Usage

```python
import mnemolink as ml

# 1. Compose an assembled mnemonic context with dynamic lego lineage
bundle = ml.compose(
    persona="juris_philosopher",
    memories=["legal/clause_ambiguity_scar"],
    build_lineage=True,
)

# 2. Inject natively into any target host
claude_system_prompt = bundle.to_claude()
openai_messages = bundle.to_openai()
gemini_instruction = bundle.to_gemini()
ollama_prompt = bundle.to_ollama()
rooms_config = bundle.to_rooms()
```

### Dynamic Lego Lineage Building

Connect arbitrary memories on the fly into an authentic, coherent tower of personal history:

```python
import mnemolink as ml

lineage = ml.build_lineage(
    memories=[
        "robotics/uav_microburst_stall",
        "robotics/optical_glare_failover",
    ],
    persona="edge_aviator",
)

print(lineage.cumulative_narrative)
```

---

## Command-Line Interface (CLI)

MnemoLink includes a pastel CLI for browsing, inspecting, composing, and benchmarking:

```bash
# List all registered mnemonic products across all discovery tiers
mnemolink list

# Filter by product kind or domain
mnemolink list --kind persona
mnemolink list --domain legal

# Inspect deep philosophical axioms and operational scars
mnemolink inspect juris_philosopher
mnemolink inspect legal/clause_ambiguity_scar

# Compose on the command line and export to target format
mnemolink compose -p edge_aviator -m robotics/uav_microburst_stall -f claude
mnemolink compose -p juris_philosopher -m legal/clause_ambiguity_scar -f modelfile -o Modelfile

# Scaffold a new community mnemonic package
mnemolink new persona quantum_physicist
mnemolink new memory aerospace_rudder_jam

# Run the simulation harness & resilience benchmark
mnemolink bench --mock
```

---

## Universal Model Adapters

| Target Host | Method | Output Format | Use Case |
| :--- | :--- | :--- | :--- |
| **Anthropic Claude** | `bundle.to_claude()` | XML `<mnemonic_matrix>` prompt | Direct Claude 3.5 Sonnet system prompts |
| **OpenAI / LiteLLM** | `bundle.to_openai()` | `[{"role": "system", ...}]` | ChatGPT, LiteLLM routers, Azure OpenAI |
| **Google GenAI** | `bundle.to_gemini()` | Clean markdown instruction string | Gemini 2.0 Flash / Pro `system_instruction` |
| **Ollama Local** | `bundle.to_ollama()` | System text string | Local privacy-first inference on edge appliances |
| **Ollama Modelfile**| `bundle.to_modelfile()`| `FROM ... \n SYSTEM """..."""` | Baking mnemonics directly into custom GGUF models |
| **ARPA Rooms** | `bundle.to_rooms()` | Dict config (`system_prompt`, metadata) | Multi-agent collaborative simulations |
| **ARPA Skillware** | `bundle.to_skillware()` | Directive markdown block | Pairing philosophical identity with executable tools |
| **Raw Markdown** | `bundle.to_raw()` | Unadorned Markdown text | Any agentic framework (LangChain, CrewAI, AutoGen) |

---

## Ecosystem

MnemoLink is an integral pillar of the **ARPA Hellenic Logical Systems** open-source stack:

- **[Skillware](https://github.com/ARPAHLS/skillware)**: *Capabilities* — "Don't prompt your agents, equip them." Executable tools, typed contracts, and deterministic runtime effects.
- **[AURA Harness](https://github.com/ARPAHLS/aura)**: *Governance* — Runtime coat for agent loops providing audit trails, policy enforcement, and compliance export.
- **[Rooms](https://github.com/ARPAHLS/rooms)**: *Orchestration* — Secure, local-first multi-agent orchestration and dynamic conversational simulation.
- **[MnemoLink](https://github.com/ARPAHLS/mnemolink)**: *Identity & Memory* — The mnemonic layer providing philosophical bedrock, operational scars, and lego lineages.

---

## Comparison: MnemoLink vs. Alternatives

For a rigorous analysis against **Mem0**, **Letta / MemGPT**, **Zep**, **Character Card V2**, and **LangChain Memory**, see **[COMPARISON.md](COMPARISON.md)**.

---

## Contributing & Community

We welcome community contributions of novel personas, battle-tested operational scars, and domain lineages! See **[CONTRIBUTING.md](CONTRIBUTING.md)** for packaging standards, submission guidelines, and review criteria.

---

## License & Citation

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

```bibtex
@software{peilivanidis2026mnemolink,
  author       = {Peilivanidis, Vladimiros and ARPA Hellenic Logical Systems},
  title        = {MnemoLink: Mnemonic Products Framework for Information Processors},
  year         = 2026,
  publisher    = {GitHub},
  url          = {https://github.com/ARPAHLS/mnemolink}
}
```

---

<div align="center">

<br>
<img src="https://raw.githubusercontent.com/ARPAHLS/.github/main/Group%202062.png" width="50" alt="ARPA Logo" />
<br>
<sub>Developed and Maintained by <b>ARPA HELLENIC LOGICAL SYSTEMS</b></sub>
<br>
<sub>Support: systems@arpacorp.net</sub>

</div>

# Universal Adapters

MnemoLink is built on consumer-agnostic principles. Once an assembled `MnemonicBundle` is compiled, it can be exported natively to any target consumer—whether frontier LLM APIs, local open-weight runtimes, multi-agent frameworks, capability registries, or vector databases.

---

## Adapter Matrix

| Target Host | Method | Output Format | Primary Use Case |
| :--- | :--- | :--- | :--- |
| **Anthropic Claude** | `bundle.to_claude()` | XML `<mnemonic_matrix>` prompt | Claude Sonnet 5 / 4.5 system prompts |
| **OpenAI Compatible** | `bundle.to_openai()` | `[{"role": "system", ...}]` | ChatGPT, OpenAI SDK, vLLM, standard endpoints |
| **Google GenAI** | `bundle.to_gemini()` | Clean markdown instruction string | Gemini 3.5 / 3.6 `system_instruction` parameter |
| **Ollama Local** | `bundle.to_ollama()` | System prompt text string | Local, privacy-first inference on edge machines |
| **Ollama Modelfile** | `bundle.to_modelfile()` | `FROM ... \n SYSTEM """..."""` | Baking mnemonics permanently into custom GGUF models |
| **ARPA Rooms** | `bundle.to_rooms()` | Dict (`system_prompt`, metadata) | Multi-agent collaborative rooms and simulations |
| **ARPA Skillware** | `bundle.to_skillware()` | Directive markdown block | Pairing philosophical identity with executable tools |
| **Raw Markdown** | `bundle.to_raw()` | Clean unadorned Markdown text | Any framework (LangChain, CrewAI, AutoGen, LlamaIndex) |
| **Vector DBs / RAG** | `bundle.to_chunks()` | List of `MemoryChunk` objects | Dense ingestion into Pinecone, Qdrant, Chroma, LanceDB |

---

## Implementation Recipes

### 1. Anthropic Claude (Direct API)

Claude processes structural context effectively through XML wrapping. `bundle.to_claude()` formats the invariant persona and episodic memories within `<mnemonic_matrix>` tags, optimizing prefix cache hits:

```python
import mnemolink
import anthropic

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/clause_ambiguity_scar"],
)

client = anthropic.Anthropic()
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system=bundle.to_claude(),
    messages=[{"role": "user", "content": "Review this indemnification draft."}],
)
```

### 2. OpenAI & OpenAI-Compatible Endpoints

`bundle.to_openai()` returns a standard system message dictionary:

```python
import mnemolink
from openai import OpenAI

bundle = mnemolink.compose(
    persona="deescalation_artisan",
    memories=["customer/hostile_chargeback_turning_point"],
)

client = OpenAI()
response = client.chat.completions.create(
    model="gpt-5.6-luna",
    messages=[
        bundle.to_openai(),
        {"role": "user", "content": "Customer demands an immediate refund and threatens litigation."},
    ],
)
```

### 3. Google Gemini

Gemini accepts direct system instructions via `system_instruction`:

```python
import mnemolink
from google import genai

bundle = mnemolink.compose(
    persona="edge_aviator",
    memories=["robotics/uav_microburst_stall"],
)

client = genai.Client()
response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents="Altimeter rapidly dropping over coastal ridge.",
    config={"system_instruction": bundle.to_gemini()},
)
```

### 4. Local Ollama & Modelfile Generation

Export directly for interactive Ollama inference or bake permanent GGUF models:

```python
import mnemolink

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/semicolon_fine_tuning_trap"],
)

# Export Modelfile
modelfile_content = bundle.to_modelfile(from_model="llama3.2:1b")
with open("Modelfile", "w", encoding="utf-8") as f:
    f.write(modelfile_content)
```

Build the custom local model in terminal:

```bash
ollama create legal-jurist -f Modelfile
ollama run legal-jurist
```

### 5. ARPA Rooms (Multi-Agent Simulation)

Integrates into ARPA Rooms collaborative workspaces:

```python
import mnemolink

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/appellate_cross_examination"],
)

agent_config = bundle.to_rooms()
# Returns: {"system_prompt": "...", "metadata": {"persona": "juris_philosopher", ...}}
```

### 6. ARPA Skillware

Pairs philosophical identity with deterministic capability tools:

```python
import mnemolink

bundle = mnemolink.compose(
    persona="edge_aviator",
    memories=["robotics/optical_glare_failover"],
)

skillware_context = bundle.to_skillware()
```

### 7. Vector Databases & Semantic Layers

Atomize any bundle into addressable, self-grounding `MemoryChunk` objects with pre-engineered embedding text:

```python
import mnemolink

bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/clause_ambiguity_scar"],
)

chunks = bundle.to_chunks()
for chunk in chunks:
    # chunk.id -> "legal/clause_ambiguity_scar#lessons"
    # chunk.embedding_text -> Context-prefixed string for dense vector embedding
    # chunk.metadata -> {"domain": "legal", "chunk_type": "lessons", "salience": 0.96}
    pass
```

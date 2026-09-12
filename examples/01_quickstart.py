"""01_quickstart.py: Minimal 5-line MnemoLink introduction.

Demonstrates composing a Persona and Memory and generating universal model prompts.
"""

import mnemolink

# 1. Compose an assembled mnemonic context
bundle = mnemolink.compose(
    persona="juris_philosopher",
    memories=["legal/clause_ambiguity_scar"],
    build_lineage=True,
)

# 2. Export natively for any model host
openai_messages = bundle.to_openai()
claude_system_prompt = bundle.to_claude()
gemini_instruction = bundle.to_gemini()
ollama_modelfile = bundle.to_modelfile(from_model="llama3.3")

print("=== Assembled Claude System Prompt ===")
print(claude_system_prompt[:600] + "\n... [truncated] ...\n")

print(
    f"Built dynamic lego lineage: '{bundle.lineage.name}' with "
    f"{len(bundle.lineage.chronology)} chronological epoch(s)."
)

"""Unit tests for universal model injection adapters."""

from mnemolink.core import compose


def test_adapters_formatting():
    bundle = compose(
        persona="juris_philosopher",
        memories=["legal/clause_ambiguity_scar"],
        build_lineage=True,
    )

    # 1. Raw Markdown
    raw = bundle.to_raw()
    assert "# MNEMONIC MATRIX PROTOCOL" in raw
    assert "Jurisprudence Philosopher" in raw
    assert "The 2021 Warranty Indemnity Trial Loss" in raw

    # 2. OpenAI / LiteLLM messages
    openai_msgs = bundle.to_openai()
    assert len(openai_msgs) == 1
    assert openai_msgs[0]["role"] == "system"
    assert "MNEMONIC MATRIX PROTOCOL" in openai_msgs[0]["content"]

    # 3. Anthropic Claude
    claude_prompt = bundle.to_claude()
    assert "<mnemonic_matrix>" in claude_prompt
    assert "</mnemonic_matrix>" in claude_prompt

    # 4. Google GenAI Gemini
    gemini_text = bundle.to_gemini()
    assert "PHILOSOPHICAL FOUNDATION & AXIOMS" in gemini_text

    # 5. Ollama Modelfile
    modelfile = bundle.to_modelfile(from_model="llama3.3")
    assert modelfile.startswith("FROM llama3.3")
    assert 'SYSTEM """' in modelfile

    # 6. ARPA Rooms
    rooms_config = bundle.to_rooms()
    assert rooms_config["name"] == "Jurisprudence Philosopher"
    assert "system_prompt" in rooms_config
    assert rooms_config["metadata"]["persona_id"] == "juris_philosopher"

    # 7. Skillware Directive
    skillware_dir = bundle.to_skillware()
    assert "OPERATIONAL DIRECTIVE" in skillware_dir

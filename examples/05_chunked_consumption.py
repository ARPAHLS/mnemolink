"""05_chunked_consumption.py: Advanced chunked context consumption and teleology.

Demonstrates:
1. Standard monolithic bundle composition.
2. Selective chunk injection (scars/lessons only) for token economy and prefix cache hits.
3. Teleological card discovery (goals, drives, and situational needs).
4. Atomizing mnemonic bundles into self-grounding MemoryChunks for vector database ingestion.
"""

import json
import mnemolink


def demonstrate_monolithic_vs_selective():
    print("=" * 70)
    print("SCENARIO 1: Monolithic vs. Selective Mnemonic Chunk Injection")
    print("=" * 70)

    # 1. Monolithic injection: loads entire persona and entire memory debriefs
    monolithic_bundle = mnemolink.compose(
        persona="juris_philosopher",
        memories=["legal/clause_ambiguity_scar"],
    )
    monolithic_prompt = monolithic_bundle.render_markdown()
    print(f"Monolithic Prompt Length: {len(monolithic_prompt)} characters")

    # 2. Selective chunk injection: extracts only operational scars and lessons learned
    # This preserves the immutable persona prefix while reducing context token consumption.
    selective_bundle = mnemolink.compose(
        persona="juris_philosopher",
        memory_specs=[
            {
                "id": "legal/clause_ambiguity_scar",
                "chunks": ["scars", "lessons"],
            }
        ],
    )
    selective_prompt = selective_bundle.render_markdown()
    print(f"Selective Prompt Length:  {len(selective_prompt)} characters")
    print("\n--- Injected Selective Output Snippet ---")
    print(selective_prompt[:500] + "\n... [truncated] ...\n")


def demonstrate_teleological_discovery():
    print("=" * 70)
    print("SCENARIO 2: Teleological Discovery (Goals, Drives, and Needs)")
    print("=" * 70)

    # Search the catalog for cards tagged with risk mitigation drives and contract drafting needs
    matching_cards = mnemolink.find_cards(
        kind="memory",
        drives=["risk_mitigation"],
        needs=["contract_drafting"],
    )

    print(f"Discovered {len(matching_cards)} matching mnemonic card(s):")
    for card in matching_cards:
        print(f"\nCard ID:     {card.id}")
        print(f"Type:        {card.memory_type}")
        print(f"Goal:        {card.teleology.primary_goal}")
        print(f"Drives:      {', '.join(card.teleology.agent_drives)}")
        print(f"Needs:       {', '.join(card.teleology.applicable_needs)}")


def demonstrate_vector_db_export():
    print("=" * 70)
    print("SCENARIO 3: Vector Database / Semantic Layer Ingestion")
    print("=" * 70)

    bundle = mnemolink.compose(
        persona="juris_philosopher",
        memories=[
            "legal/clause_ambiguity_scar",
            "legal/appellate_cross_examination",
        ],
    )

    # Atomize the bundle into discrete, self-grounding MemoryChunk objects
    chunks = bundle.to_chunks()
    print(f"Exported {len(chunks)} self-grounding MemoryChunks from bundle:")

    for chunk in chunks[:4]:
        print(f"\n--- Chunk: {chunk.id} ---")
        print(f"Type:        {chunk.chunk_type}")
        print(f"Salience:    {chunk.salience}")
        print(f"Pinned:      {chunk.is_pinned}")
        print(f"Embedding Header: {chunk.embedding_text.splitlines()[0]}")
        print(f"Metadata:    {json.dumps(chunk.metadata)}")


if __name__ == "__main__":
    demonstrate_monolithic_vs_selective()
    demonstrate_teleological_discovery()
    demonstrate_vector_db_export()

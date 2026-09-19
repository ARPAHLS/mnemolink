# Mnemonic Memories Library

## Overview

In MnemoLink, a **Memory** is an episodic crucible—a recorded, battle-tested operational experience that imparts tangible scars, sensory cues, and imperative lessons.

Standard models lack intuition because they have never experienced failure. When an agent equipped with MnemoLink encounters an operational dilemma, it does not rely on abstract pre-training heuristics; it draws upon concrete episodic memories that dictate how to act under intense environmental, legal, or relational friction.

For deeper context on the taxonomy and chunk architecture, see the **[Taxonomy, Teleology & Chunking Guide](../taxonomy_and_teleology.md)**.

---

## The 5-Kind Memory Taxonomy

Every episodic memory in the library is classified into one of five functional kinds:

| Kind | Description | Computational Purpose | Representative Asset |
|---|---|---|---|
| `lore` | Foundational origin stories, cultural priors, lineage roots, and formative background. | Instills core temperament, deep identity roots, and broad background perspective. | `legal/solo_practitioner_upbringing` |
| `work` | Professional tradecraft, procedural praxis, standard craft habits, and tactical masterclasses. | Informs technical execution, methodical discipline, and professional standards of care. | `legal/appellate_cross_examination` |
| `incident` | High-cost crucibles, costly mistakes, near-misses, arbitration losses, and physical crashes. | Imparts deep operational scars, threat wariness, and acute caution against failure modes. | `legal/clause_ambiguity_scar`, `robotics/uav_microburst_stall` |
| `relational` | Interpersonal dynamics, stakeholder negotiations, broken trust, client blow-ups, and emotional friction. | Guides de-escalation, conflict resolution, motive attribution, and boundary enforcement. | `customer/hostile_chargeback_turning_point` |
| `telemetry` | Raw physical traces, sensor feeds, hardware failover sequences, and friction logs under physical reality. | Calibrates physical confidence thresholds, sensor cross-checking, and hardware limits. | `robotics/optical_glare_failover` |

---

## Mnemonic Chunk Topology

Every memory is segmented into five addressable, self-grounding chunks:
- **`story`**: Narrative chronology, scenario, and background setting.
- **`scars`**: Quantifiable damage incurred: capital lost, aircraft damaged, reputation compromised.
- **`lessons`**: Actionable operational axioms learned from the crucible.
- **`triggers`**: Environmental sensory cues signaling that the crucible scenario is recurring.
- **`reflection`**: Philosophical realization calibrating the agent's epistemological model.

---

## Catalog Directory

The following curated episodic memories are bundled natively within MnemoLink. Click any memory for its dedicated architectural guide, failure crucible narrative, operational scars, lessons, and pairing combinations:

| ID | Memory Guide | Kind | Domain | Salience | Primary Goal | Active Drives | Author | Manifest |
|---|---|---|---|---|---|---|---|---|
| `legal/solo_practitioner_upbringing` | [**Solo Practitioner Upbringing**](solo_practitioner_upbringing.md) | `lore` | `legal` | 0.85 | Establish procedural rigor and fiduciary duty through early formative background | `fiduciary_discipline`, `procedural_humility`, `detail_vigilance` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/solo_practitioner_upbringing/card.json) |
| `legal/appellate_cross_examination` | [**Appellate Bench Candor Mastery**](appellate_cross_examination.md) | `work` | `legal` | 0.90 | Establish intellectual authority through fearless appellate candor | `procedural_candor`, `credibility_preservation` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/appellate_cross_examination/card.json) |
| `legal/clause_ambiguity_scar` | [**The 2021 Warranty Indemnity Trial Loss**](clause_ambiguity_scar.md) | `incident` | `legal` | 0.95 | Defend against commercial indemnity claims and enforce contractual exceptions | `risk_mitigation`, `fiduciary_preservation`, `procedural_skepticism` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/clause_ambiguity_scar/card.json) |
| `legal/semicolon_fine_tuning_trap` | [**The GenAI Ingestion Indemnity Dispute**](semicolon_fine_tuning_trap.md) | `incident` | `legal` | 0.96 | Prevent client strict liability exposure in AI data ingestion and model licensing agreements | `syntax_defense`, `fiduciary_preservation`, `covenant_restructuring` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/semicolon_fine_tuning_trap/card.json) |
| `customer/hostile_chargeback_turning_point` | [**Outage Hostile Chargeback Turning Point**](hostile_chargeback_turning_point.md) | `relational` | `customer` | 0.90 | Convert enraged churn-risk enterprise accounts into long-term partners | `deescalation`, `transparency`, `relationship_repair` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/customer/hostile_chargeback_turning_point/card.json) |
| `robotics/uav_microburst_stall` | [**Cape Wrath Microburst Stall Recovery**](uav_microburst_stall.md) | `incident` | `robotics` | 0.98 | Recover fixed-wing aircraft from sudden windshear downdrafts | `survival`, `aerodynamic_discipline`, `energy_preservation` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/robotics/uav_microburst_stall/card.json) |
| `robotics/optical_glare_failover` | [**Dawn Glare Optical Sensor Failover**](optical_glare_failover.md) | `telemetry` | `robotics` | 0.88 | Maintain autonomous trajectory integrity during optical blindness | `sensor_skepticism`, `safety_redundancy` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/robotics/optical_glare_failover/card.json) |
| `culinary/thessaloniki_breakfasts` | [**Unforgettable Breakfasts and Brunches from Thessaloniki**](thessaloniki_breakfasts.md) | `lore` | `culinary` | 0.94 | Deliver unforgettable Northern Mediterranean breakfast, brunch, and comfort hospitality through precise egg craft, authentic pastry handling, and flavor contrast | `culinary_hospitality`, `technique_precision`, `sensory_generosity`, `emotional_grounding` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/culinary/thessaloniki_breakfasts/card.json) |
| `skillware/interactive_slot_filling` | [**Interactive Slot Gathering Protocol**](skillware_interactive_slot_filling.md) | `work` | `skillware` | 0.95 | Enforce interactive parameter slot gathering, human preview rendering, and confirmation gates before external state mutation | `tool_contract_integrity`, `confirmation_enforcement`, `conversational_precision` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/skillware/interactive_slot_filling/card.json) |
| `skillware/entity_disambiguation` | [**Corporate Registry Disambiguation**](skillware_entity_disambiguation.md) | `work` | `skillware` | 0.94 | Resolve ambiguous entity search candidates and preserve fragile numeric string formats without data corruption | `data_integrity`, `entity_disambiguation`, `working_memory_preservation` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/skillware/entity_disambiguation/card.json) |
| `skillware/irreversible_action_crucible` | [**DeFi Slippage & Irreversible Action**](skillware_irreversible_action_crucible.md) | `incident` | `skillware` | 0.96 | Enforce strict pre-flight address validation, slippage bounds, and dual-phase confirmation for irreversible on-chain transactions | `irreversible_action_safety`, `capital_preservation`, `tool_contract_integrity` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/skillware/irreversible_action_crucible/card.json) |
| `skillware/runtime_outage_and_grace` | [**Upstream Outage Operational Grace**](skillware_runtime_outage_and_grace.md) | `relational` | `skillware` | 0.92 | De-escalate user panic during upstream API rate limits and transport outages through transparent, reassuring communication | `relational_resilience`, `calm_transparency`, `error_deescalation` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/skillware/runtime_outage_and_grace/card.json) |

---

## Detailed Memory Guides

Each memory has a dedicated reference manual providing complete narrative crucibles, quantifiable scars, actionable lessons, sensory triggers, and pairing recipes:

- [**Solo Practitioner Upbringing Guide**](solo_practitioner_upbringing.md): Early rural litigation background, document verification rigor, and evidentiary humility (`lore`).
- [**Appellate Bench Candor Mastery Guide**](appellate_cross_examination.md): Disarming judicial panel skepticism through fearless procedural concessions (`work`).
- [**The 2021 Warranty Indemnity Trial Loss Guide**](clause_ambiguity_scar.md): The $4.2M unanchored semicolon summary judgment crucible and syntactic defense protocols (`incident`).
- [**The GenAI Ingestion Indemnity Dispute Guide**](semicolon_fine_tuning_trap.md): Model data licensing dispute, foundation model post-training fine-tuning trap, and surgical redlining (`incident`).
- [**Outage Hostile Chargeback Turning Point Guide**](hostile_chargeback_turning_point.md): Enterprise executive churn de-escalation, emotional validation, and radical structural postmortems (`relational`).
- [**Cape Wrath Microburst Stall Recovery Guide**](uav_microburst_stall.md): Autonomous fixed-wing UAV downdraft shear recovery, nose-down reflex, and aerodynamic margin prioritization (`incident`).
- [**Dawn Glare Optical Sensor Failover Guide**](optical_glare_failover.md): Computer vision camera saturation under low-angle solar glare and LiDAR/IMU sensor-voting failovers (`telemetry`).
- [**Thessaloniki Breakfasts & Brunches Guide**](thessaloniki_breakfasts.md): Ano Poli lemon-kissed bougatsa phyllo discipline, two-minute residual-heat "eggs eyes", Turkish sunset breakfast contrasts, and mother's crispy fried eggplants with garlic mayo (`lore`).
- [**Interactive Slot Gathering Protocol Guide**](skillware_interactive_slot_filling.md): Four-stage discipline (resolve, draft, preview, confirm), parameter slot gathering, and email mutation boundaries (`work`).
- [**Corporate Registry Disambiguation Guide**](skillware_entity_disambiguation.md): Leading-zero string preservation, company status flags, candidate formatting, and state resumption (`work`).
- [**DeFi Slippage & Irreversible Action Guide**](skillware_irreversible_action_crucible.md): The $48,200 burn crucible, EIP-55 checksum validation, MEV slippage caps, and simulation (`incident`).
- [**Upstream Outage Operational Grace Guide**](skillware_runtime_outage_and_grace.md): Absorbing HTTP 429/503 errors, concealing raw stack traces, and de-escalating user friction (`relational`).

---

## Programmatic Usage

### Selective Mnemonic Chunk Injection (Prefix Cache Friendly)
```python
import mnemolink

# Inject only actionable lessons and concrete operational scars
bundle = mnemolink.compose(
    persona="juris_philosopher",
    memory_specs=[
        {
            "id": "legal/clause_ambiguity_scar",
            "chunks": ["scars", "lessons"],
        }
    ],
)
prompt = bundle.render_markdown()
```

### Teleological Discovery
```python
import mnemolink

# Find memories matching specific operational drives and situational needs
cards = mnemolink.find_cards(
    kind="memory",
    drives=["risk_mitigation"],
    needs=["contract_drafting"],
)
for card in cards:
    print(f"[{card.memory_type}] {card.id}: {card.teleology.primary_goal}")
```

### Vector DB / Semantic Layer Export
```python
import mnemolink

mem = mnemolink.load_memory("legal/clause_ambiguity_scar")
chunks = mem.to_chunks()

for chunk in chunks:
    # Ingest directly into Pinecone, Qdrant, Chroma, or LangChain
    print(f"Chunk ID: {chunk.id} | Salience: {chunk.salience}")
    print(f"Embedding Header: {chunk.embedding_text[:80]}...")
```

---

## Further Reading & Workflows

For full integration examples, vector database ingestion schemas, and selective chunk composition, see the **[Usage Guide](../usage_guide.md)**.

## Contributing New Memories

To contribute a new operational scar, flight trace, or tradecraft debrief, review the standards in [CONTRIBUTING.md](../../CONTRIBUTING.md#2-memory-standard) and submit your package following the `memories/<domain>/<memory_slug>/` specification.

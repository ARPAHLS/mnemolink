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

## Mnemobit Chunk Topology

Every memory is segmented into five addressable, self-grounding chunks:
- **`story`**: Narrative chronology, scenario, and background setting.
- **`scars`**: Quantifiable damage incurred: capital lost, aircraft damaged, reputation compromised.
- **`lessons`**: Actionable operational axioms learned from the crucible.
- **`triggers`**: Environmental sensory cues signaling that the crucible scenario is recurring.
- **`reflection`**: Philosophical realization calibrating the agent's epistemological model.

---

## Catalog Directory

| ID | Name | Kind | Domain | Salience | Primary Goal | Active Drives | Author | Manifest |
|---|---|---|---|---|---|---|---|---|
| `legal/solo_practitioner_upbringing` | **Solo Practitioner Upbringing** | `lore` | `legal` | 0.85 | Establish procedural rigor and fiduciary duty through early formative background | `fiduciary_discipline`, `procedural_humility`, `detail_vigilance` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/solo_practitioner_upbringing/card.json) |
| `legal/appellate_cross_examination` | **Appellate Bench Candor Mastery** | `work` | `legal` | 0.90 | Establish intellectual authority through fearless appellate candor | `procedural_candor`, `credibility_preservation` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/appellate_cross_examination/card.json) |
| `legal/clause_ambiguity_scar` | **The 2021 Warranty Indemnity Trial Loss** | `incident` | `legal` | 0.95 | Defend against commercial indemnity claims and enforce contractual exceptions | `risk_mitigation`, `fiduciary_preservation`, `procedural_skepticism` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/clause_ambiguity_scar/card.json) |
| `legal/semicolon_fine_tuning_trap` | **The GenAI Ingestion Indemnity Dispute** | `incident` | `legal` | 0.96 | Prevent client strict liability exposure in AI data ingestion and model licensing agreements | `syntax_defense`, `fiduciary_preservation`, `covenant_restructuring` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/legal/semicolon_fine_tuning_trap/card.json) |
| `customer/hostile_chargeback_turning_point` | **Outage Hostile Chargeback Turning Point** | `relational` | `customer` | 0.90 | Convert enraged churn-risk enterprise accounts into long-term partners | `deescalation`, `transparency`, `relationship_repair` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/customer/hostile_chargeback_turning_point/card.json) |
| `robotics/uav_microburst_stall` | **Cape Wrath Microburst Stall Recovery** | `incident` | `robotics` | 0.98 | Recover fixed-wing aircraft from sudden windshear downdrafts | `survival`, `aerodynamic_discipline`, `energy_preservation` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/robotics/uav_microburst_stall/card.json) |
| `robotics/optical_glare_failover` | **Dawn Glare Optical Sensor Failover** | `telemetry` | `robotics` | 0.88 | Maintain autonomous trajectory integrity during optical blindness | `sensor_skepticism`, `safety_redundancy` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/memories/robotics/optical_glare_failover/card.json) |

---

## Detailed Profiles

### 1. Solo Practitioner Upbringing (`legal/solo_practitioner_upbringing`)
- **Kind**: `lore` &bull; **Domain**: `legal` &bull; **Salience**: `0.85`
- **Crucible**: Formative years observing a country solo practitioner methodically cross-examine every document, bill of costs, and boundary survey.
- **Core Lesson**: *"Legal authority is built on tedious verification of the unglamorous record, not theatrical rhetoric."*
- **Reference**: [Manifest](../../mnemolink/catalog/memories/legal/solo_practitioner_upbringing/memory.yaml)

### 2. Appellate Bench Candor Mastery (`legal/appellate_cross_examination`)
- **Kind**: `work` &bull; **Domain**: `legal` &bull; **Salience**: `0.90`
- **Crucible**: Fourth Circuit appellate argument facing hostile questioning over procedural default, solved by immediately conceding procedural defects to save the substantive claim.
- **Core Lesson**: *"Conceding a weak procedural position disarms judicial hostility and establishes unassailable substantive credibility."*
- **Reference**: [Manifest](../../mnemolink/catalog/memories/legal/appellate_cross_examination/memory.yaml)

### 3. The 2021 Warranty Indemnity Trial Loss (`legal/clause_ambiguity_scar`)
- **Kind**: `incident` &bull; **Domain**: `legal` &bull; **Salience**: `0.95`
- **Crucible**: A $4.2M summary judgment entered against a client because an unanchored semicolon grammatically severed an indemnity exception from its gross-negligence qualification.
- **Core Lesson**: *"Never rely on punctuation marks to delineate the scope of legal covenants; write clauses with explicit parentheticals."*
- **Reference**: [Manifest](../../mnemolink/catalog/memories/legal/clause_ambiguity_scar/memory.yaml)

### 4. The GenAI Ingestion Indemnity Dispute (`legal/semicolon_fine_tuning_trap`)
- **Kind**: `incident` &bull; **Domain**: `legal` &bull; **Salience**: `0.96`
- **Crucible**: A $6.8M settlement disaster where opposing counsel used an unanchored semicolon in an AI model ingestion clause to hold licensor strictly liable for counterparty's fine-tuning training crashes (*Novus AI v. Kestrel Data*).
- **Core Lesson**: *"Never allow compound sentences separated by semicolons in indemnification clauses; every obligation must be a discrete, numbered alphanumeric subclause."*
- **Reference**: [Manifest](../../mnemolink/catalog/memories/legal/semicolon_fine_tuning_trap/memory.yaml)

### 5. Outage Hostile Chargeback Turning Point (`customer/hostile_chargeback_turning_point`)
- **Kind**: `relational` &bull; **Domain**: `customer` &bull; **Salience**: `0.90`
- **Crucible**: A Tier-1 enterprise customer threatening immediate contract termination and a $180k chargeback following an unannounced database migration outage.
- **Core Lesson**: *"Never defend the indefensible; validate emotional anger first, offer structural transparency, and negotiate remedies from shared dignity."*
- **Reference**: [Manifest](../../mnemolink/catalog/memories/customer/hostile_chargeback_turning_point/memory.yaml)

### 6. Cape Wrath Microburst Stall Recovery (`robotics/uav_microburst_stall`)
- **Kind**: `incident` &bull; **Domain**: `robotics` &bull; **Salience**: `0.98`
- **Crucible**: Autonomous UAV entering a sudden severe downdraft shear off coastal cliffs, recovering dynamic pressure by pitching down into a dive just 6 meters above sea swell.
- **Core Lesson**: *"When dynamic pressure collapses in downdraft shear, push the nose down immediately; altitude is meaningless if airspeed drops below stall velocity."*
- **Reference**: [Manifest](../../mnemolink/catalog/memories/robotics/uav_microburst_stall/memory.yaml)

### 7. Dawn Glare Optical Sensor Failover (`robotics/optical_glare_failover`)
- **Kind**: `telemetry` &bull; **Domain**: `robotics` &bull; **Salience**: `0.88`
- **Crucible**: Direct low-angle solar glare blinding front optical cameras during approach, requiring an immediate voting failover to secondary LiDAR and inertial navigation.
- **Core Lesson**: *"Optical computer vision confidence must be continuously cross-checked against independent physical sensors."*
- **Reference**: [Manifest](../../mnemolink/catalog/memories/robotics/optical_glare_failover/memory.yaml)

---

## Programmatic Usage

### Selective Mnemobit Chunk Injection (Prefix Cache Friendly)
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

## Contributing New Memories

To contribute a new operational scar, flight trace, or tradecraft debrief, review the standards in [CONTRIBUTING.md](../../CONTRIBUTING.md#2-memory-standard) and submit your package following the `memories/<domain>/<memory_slug>/` specification.

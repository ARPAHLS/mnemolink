# Mnemonic Lineages Library

## Overview

In MnemoLink, a **Lineage** is a chronological sequence of episodic memories linked by **dynamic causal bridges**.

Human competence is not a disconnected collection of facts; it is an evolving historical arc where each mistake reshapes operating assumptions for the next challenge. Rather than requiring users to manually script long autobiographical backstories, MnemoLink treats memories like interlocking Lego bricks. The `LineageBuilder` synthesizes connective causal tissue that binds discrete operational scars into an authentic, coherent personal history.

---

## Lineage Architecture

```mermaid
flowchart LR
    M1["Memory 1<br/>(Early Crisis / Failure)"] -->|Dynamic Causal Bridge| M2["Memory 2<br/>(Subsequent Adaptation)"]
    M2 -->|Dynamic Causal Bridge| M3["Memory 3<br/>(Mastery / Intuition)"]
    M3 --> Lineage["Unified Lineage Tower<br/>(Cumulative Backstory)"]
```

A Lineage product consists of four structural layers:
1. **Memory Spine (`memory_ids`)**: The ordered list of constituent memories anchoring each epoch.
2. **Chronological Epochs (`chronology`)**: Temporal markers framing the progression of experience.
3. **Causal Bridges (`causal_bridges`)**: Connective narrative analyzing how the scars of Epoch $N$ forged the reflexes demonstrated in Epoch $N+1$.
4. **Cumulative Narrative (`cumulative_narrative`)**: The synthesized unified backstory ready for injection into target host runtimes.

---

## Catalog Directory

| ID | Name | Domain | Constituent Memories | Primary Evolutionary Goal | Active Drives | Author | Manifest |
|---|---|---|---|---|---|---|---|
| `legal_crucible` | **Legal Crucible Progression** | `legal` | `legal/clause_ambiguity_scar` &rarr; `legal/appellate_cross_examination` | Evolve from costly contractual ambiguity error into master of appellate judicial candor | `fiduciary_vigilance`, `procedural_candor`, `credibility_preservation` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/lineages/legal_crucible/card.json) |
| `flight_scars` | **Autonomous Flight Scars Lineage** | `robotics` | `robotics/uav_microburst_stall` &rarr; `robotics/optical_glare_failover` | Transform aerodynamic trauma and optical blindness into battle-tested survival reflexes | `aerodynamic_preservation`, `sensor_redundancy`, `energy_discipline` | [ARPA Hellenic Logical Systems](https://github.com/ARPAHLS) | [`card.json`](../../mnemolink/catalog/lineages/flight_scars/card.json) |

---

## Detailed Profiles

### 1. Legal Crucible Progression (`legal_crucible`)
- **Domain**: `legal`
- **Memory Sequence**:
  1. `legal/clause_ambiguity_scar`: The 2021 Warranty Indemnity Trial Loss ($4.2M loss due to an unanchored semicolon).
  2. `legal/appellate_cross_examination`: Appellate Bench Candor Mastery (fearlessly conceding a procedural default to earn substantive credibility).
- **Causal Connective Tissue**:
  The devastating financial loss from the ambiguous semicolon instilled an acute wariness of syntactic pedantry. When subsequent appellate hostility arose, the practitioner abandoned defensive statutory excuses and embraced fearless procedural candor, permanently securing client credibility.
- **Reference**: [Manifest](../../mnemolink/catalog/lineages/legal_crucible/lineage.yaml)

### 2. Autonomous Flight Scars Lineage (`flight_scars`)
- **Domain**: `robotics`
- **Memory Sequence**:
  1. `robotics/uav_microburst_stall`: Cape Wrath Microburst Stall Recovery (pitching down into a dive 6m above ocean swell to regain dynamic pressure).
  2. `robotics/optical_glare_failover`: Dawn Glare Optical Sensor Failover (blinded camera failover to LiDAR and inertial voting).
- **Causal Connective Tissue**:
  Surviving the microburst stall drilled the inviolable primacy of physics into the autopilot logic. When low-angle solar glare subsequently blinded the primary vision stack, the system refused to maintain a blind optical course and instantly executed a sensor-voting failover.
- **Reference**: [Manifest](../../mnemolink/catalog/lineages/flight_scars/lineage.yaml)

---

## Programmatic Usage

### Loading a Pre-Composed Lineage
```python
import mnemolink

lineage = mnemolink.load_lineage("legal_crucible")
print(f"Lineage: {lineage.name}")
print(f"Epochs: {len(lineage.chronology)}")
print(f"Backstory: {lineage.cumulative_narrative[:150]}...")
```

### Dynamic Lego Lineage Building On-the-Fly
Connect any arbitrary list of memories on the fly into an authentic, coherent tower of personal history:

```python
import mnemolink

lineage = mnemolink.build_lineage(
    memories=[
        "robotics/uav_microburst_stall",
        "robotics/optical_glare_failover",
    ],
    persona="edge_aviator",
)

# Access dynamic causal connective tissue
for bridge in lineage.causal_bridges:
    print(f"Causal Bridge: {bridge}")

# Full unified narrative
print(lineage.cumulative_narrative)
```

### Composing within a Mnemonic Bundle
```python
import mnemolink

bundle = mnemolink.compose(
    persona="edge_aviator",
    memories=[
        "robotics/uav_microburst_stall",
        "robotics/optical_glare_failover",
    ],
    build_lineage=True,  # Automatically synthesizes lineage
)

claude_prompt = bundle.to_claude()
```

---

## Contributing New Lineages

To contribute a pre-composed domain progression, review the standards in [CONTRIBUTING.md](../../CONTRIBUTING.md#3-lineage-standard) and submit your package following the `lineages/<domain>/<lineage_slug>/` specification.

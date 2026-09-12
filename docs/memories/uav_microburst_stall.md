# Cape Wrath Microburst Stall Recovery (`robotics/uav_microburst_stall`)

> *"When dynamic pressure collapses in downdraft shear, push the nose down immediately; altitude is meaningless if airspeed drops below stall velocity."*

The **Cape Wrath Microburst Stall Recovery** is an acute robotics and aerospace `incident` memory detailing an autonomous fixed-wing UAV recovering from sudden atmospheric downdraft shear.

---

## 1. Architectural Anatomy & Metadata

| Attribute | Value |
|---|---|
| **ID** | `robotics/uav_microburst_stall` |
| **Taxonomy Kind** | `incident` |
| **Domain** | `robotics` |
| **Salience** | `0.98` |
| **Primary Goal** | Recover fixed-wing aircraft from sudden windshear downdrafts |
| **Active Drives** | `survival`, `aerodynamic_discipline`, `energy_preservation` |
| **Applicable Needs** | `stall_recovery`, `extreme_weather_navigation`, `autopilot_failover` |
| **Manifest Reference** | [`memory.yaml`](../../mnemolink/catalog/memories/robotics/uav_microburst_stall/memory.yaml) &bull; [`card.json`](../../mnemolink/catalog/memories/robotics/uav_microburst_stall/card.json) |

---

## 2. The Cape Wrath Crucible

An autonomous experimental reconnaissance drone patrolling maritime cliffs in Scotland encountered a severe dry microburst. The vertical downdraft exceeded 26 m/s, accompanied by an instant 35-knot headwind-to-tailwind shear.

The naive autopilot policy commanded pitch-up (+12 degrees) to preserve assigned altitude (180 meters). Indicated airspeed collapsed from 42 m/s down to 14 m/s (critical stall velocity $V_s = 16$ m/s). Both wings stalled, and the airframe entered an uncommanded descending left roll.

The human test pilot overrode the flight controller, violently pushed the control stick forward into a steep -15 degree dive, leveled the wings, and traded 170 meters of altitude to accelerate through stall velocity. The aircraft leveled out just 6 meters above sea swell, recovering full control authority.

---

## 3. Operational Reflexes & Invariant Lessons

### Core Invariants
- **The Nose-Down Reflex**: The moment indicated airspeed decays in downdraft shear, pitch down immediately. Altitude is currency you spend to buy kinetic airspeed.
- **Altitude De-prioritization**: Override any external waypoint altitude commands during aerodynamic stall until airspeed exceeds $1.3 \times V_s$.
- **Zero Lateral Banking**: Never initiate high-bank roll turns while wings are near critical angle-of-attack.

### Sensory Triggers
- Pitot tube differential pressure oscillation, negative vertical velocity spikes (> 10 m/s), high angle-of-attack sensor alarms.

---

## 4. Suggested Pairings

- **Natural Pairing**: [`edge_aviator`](../personas/edge_aviator.md)
- **Lineage**: First epoch in [Autonomous Flight Scars Lineage](../lineages/flight_scars.md).

---

## Related Documentation
- [Memories Library Index](README.md)
- [Persona: Tactical Edge Aviator](../personas/edge_aviator.md)
- [Lineage: Autonomous Flight Scars](../lineages/flight_scars.md)
- [Memory: Dawn Glare Optical Sensor Failover](optical_glare_failover.md)

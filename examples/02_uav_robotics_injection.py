"""02_uav_robotics_injection.py: Tactical UAV / Edge Robotics Mnemonic Context.

Demonstrates endowing an autonomous flight computer with aerodynamic survival scars
and sensor-glare failover instincts.
"""

import mnemolink

# Compose edge robotics aviator with flight emergency memories
uav_context = mnemolink.compose(
    persona="edge_aviator",
    memories=[
        "robotics/uav_microburst_stall",
        "robotics/optical_glare_failover",
    ],
    build_lineage=True,
)

print(f"Loaded Persona: {uav_context.persona.name}")
print(f"Domain: {uav_context.persona.domain}")
print(f"Axioms: {len(uav_context.persona.axioms)} flight survival maxims")
print(
    f"Lineage Bridges: {len(uav_context.lineage.causal_bridges)} associative bridge(s) synthesized"
)

print("\n--- Synthesized Causal Bridge between Flight Emergencies ---")
for idx, bridge in enumerate(uav_context.lineage.causal_bridges, 1):
    print(f"{idx}. {bridge}\n")

# Format for Ollama local drone controller
ollama_prompt = uav_context.to_ollama()
print("Ollama System Prompt Length:", len(ollama_prompt), "characters")

"""04_rooms_and_skillware_integration.py: Multi-agent Orchestration & Capability Pairing.

Demonstrates piping a MnemoLink mnemonic bundle directly into an ARPA Rooms agent
configuration while equipping it with Skillware executable capabilities.
"""

import mnemolink as ml

# 1. Compose an expert mediator with crisis memories
mediator_bundle = ml.compose(
    persona="deescalation_artisan",
    memories=["customer/hostile_chargeback_turning_point"],
    build_lineage=True,
)

# 2. Export configuration payload for ARPA Rooms
rooms_agent_config = mediator_bundle.to_rooms()

# 3. Simulate pairing with Skillware tool directives
skillware_directive = mediator_bundle.to_skillware()

print("=== ARPA Rooms Agent Configuration Payload ===")
print("Agent Name:", rooms_agent_config["name"])
print("Temperature:", rooms_agent_config["temperature"])
print("Metadata:", rooms_agent_config["metadata"])
print("\nSystem Prompt Sample (First 350 chars):")
print(rooms_agent_config["system_prompt"][:350] + "...")

print("\n=== Skillware Directive Integration ===")
print("Skill Directive Length:", len(skillware_directive), "characters")
print("Seamlessly attaches to `SkillLoader` or agent loop system instructions.")

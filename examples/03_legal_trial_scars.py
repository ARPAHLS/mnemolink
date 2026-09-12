"""03_legal_trial_scars.py: Legal Counsel with 10 Years of Courtroom Battle Scars.

Demonstrates loading the pre-composed 'legal_crucible' lineage alongside the
'juris_philosopher' persona to guide contract risk analysis.
"""

import mnemolink

# Compose using pre-existing bundled lineage
counsel_bundle = mnemolink.compose(
    persona="juris_philosopher",
    lineage="legal_crucible",
)

print(f"Agent Persona: {counsel_bundle.persona.name}")
print(f"Lineage: {counsel_bundle.lineage.name}")
print("\n--- Cumulative Courtroom Backstory ---")
print(counsel_bundle.lineage.cumulative_narrative)

# Export for Anthropic Claude system block
claude_payload = counsel_bundle.to_claude()
print("\n--- Claude Injection Preview (First 400 chars) ---")
print(claude_payload[:400] + "...")

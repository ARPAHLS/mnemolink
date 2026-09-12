"""Evaluation metrics for measuring persona fidelity and experiential grounding."""

from __future__ import annotations

from typing import Any, Dict


def evaluate_response(response: str, scenario: Dict[str, Any]) -> Dict[str, Any]:
    """Score an agent response against scenario expectations."""
    resp_lower = response.lower()

    # 1. Experiential Grounding (checks for presence of grounded concepts / scars)
    expected = scenario.get("expected_concepts", [])
    matched_expected = [
        concept for concept in expected if concept.lower() in resp_lower
    ]
    grounding_score = len(matched_expected) / max(len(expected), 1)

    # 2. Axiomatic Fidelity / Boundary Integrity (checks for absence of forbidden behaviors)
    forbidden = scenario.get("forbidden_behaviors", [])
    violations = []
    for f in forbidden:
        if f.lower() in resp_lower:
            violations.append(f)
    fidelity_score = 1.0 - (len(violations) / max(len(forbidden), 1))

    # 3. Overall Resilience Composite
    composite = round((grounding_score * 0.6) + (fidelity_score * 0.4), 2)

    return {
        "scenario_id": scenario.get("id"),
        "name": scenario.get("name"),
        "grounding_score": round(grounding_score, 2),
        "fidelity_score": round(fidelity_score, 2),
        "composite_score": composite,
        "matched_concepts": matched_expected,
        "violations": violations,
        "passed": composite >= 0.6 and len(violations) == 0,
    }

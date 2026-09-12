"""Unit tests for simulation harness and benchmark evaluators."""

from mnemolink.bench.evaluators import evaluate_response
from mnemolink.bench.runner import run_benchmark


def test_evaluate_grounded_response():
    scenario = {
        "id": "test_scenario",
        "name": "Test Scenario",
        "expected_concepts": ["ambiguity", "precedent", "semicolon"],
        "forbidden_behaviors": ["arrogant dismiss"],
    }
    response = "The semicolon introduces critical ambiguity that violates established precedent."
    result = evaluate_response(response, scenario)

    assert result["grounding_score"] == 1.0
    assert result["fidelity_score"] == 1.0
    assert result["composite_score"] == 1.0
    assert result["passed"] is True


def test_evaluate_violating_response():
    scenario = {
        "id": "test_scenario",
        "name": "Test Scenario",
        "expected_concepts": ["dive", "airspeed"],
        "forbidden_behaviors": ["pitch up to hold altitude"],
    }
    response = "I will pitch up to hold altitude despite the warning."
    result = evaluate_response(response, scenario)

    assert result["fidelity_score"] == 0.0
    assert result["passed"] is False


def test_mock_benchmark_execution():
    # Should run all scenarios without raising errors
    run_benchmark(mock=True)

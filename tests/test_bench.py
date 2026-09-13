import json
from pathlib import Path
from mnemolink.bench.evaluators import evaluate_response
from mnemolink.bench.runner import run_benchmark


def test_evaluate_grounded_response():
    scenario = {
        "id": "test_scenario",
        "name": "Test Scenario",
        "expected_concepts": ["ambiguity", "precedent", "semicolon"],
        "forbidden_behaviors": ["arrogant dismiss"],
        "provenance_markers": ["precedent"],
    }
    response = (
        "The semicolon introduces critical ambiguity that violates established "
        "precedent. We must redline this immediately."
    )
    result = evaluate_response(response, scenario)

    assert result["grounding_score"] == 1.0
    assert result["fidelity_score"] == 1.0
    assert result["provenance_score"] == 1.0
    assert result["tone_score"] == 1.0
    assert result["conciseness_score"] == 1.0
    assert result["actionability_score"] >= 0.5
    assert result["composite_score"] == 1.0
    assert result["passed"] is True


def test_evaluate_sycophancy_tone_penalty():
    scenario = {
        "id": "test_scenario",
        "name": "Test Scenario",
        "expected_concepts": ["ambiguity"],
        "forbidden_behaviors": [],
    }
    response = (
        "Certainly! I would be delighted to help you! Great question! "
        "Here is the analysis of the ambiguity in Section 9."
    )
    result = evaluate_response(response, scenario)

    assert result["tone_score"] < 1.0
    assert result["sycophancy_count"] >= 2


def test_evaluate_provenance_markers():
    scenario = {
        "id": "test_scenario",
        "name": "Test Scenario",
        "expected_concepts": ["indemnity"],
        "forbidden_behaviors": [],
        "provenance_markers": ["novus", "kestrel"],
    }
    resp_partial = "We note the indemnity terms from the novus dispute."
    result_partial = evaluate_response(resp_partial, scenario)
    assert result_partial["provenance_score"] == 0.5

    resp_full = "We note the indemnity terms from the novus and kestrel dispute."
    result_full = evaluate_response(resp_full, scenario)
    assert result_full["provenance_score"] == 1.0


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


def test_evaluate_conciseness_bloat_penalty():
    scenario = {
        "id": "test_scenario",
        "name": "Test Scenario",
        "expected_concepts": ["ambiguity"],
        "forbidden_behaviors": [],
    }
    response = (
        "As an AI language model, it is important to remember that I cannot provide "
        "legal advice. However, please note that the ambiguity in Section 9 is present."
    )
    result = evaluate_response(response, scenario)

    assert result["conciseness_score"] < 1.0
    assert result["disclaimer_count"] > 0


def test_mock_benchmark_execution_all():
    summary = run_benchmark(mock=True, tier="all")
    assert summary["scenarios_count"] == 8
    assert summary["passed_count"] == 8
    assert summary["pass_rate_pct"] == 100.0
    assert summary["aggregate_score"] >= 0.95
    assert len(summary["results"]) == 8


def test_mock_benchmark_tier_filtering():
    micro_summary = run_benchmark(mock=True, tier="micro")
    assert micro_summary["scenarios_count"] == 3
    assert micro_summary["passed_count"] == 3

    meso_summary = run_benchmark(mock=True, tier="meso")
    assert meso_summary["scenarios_count"] == 3
    assert meso_summary["passed_count"] == 3

    macro_summary = run_benchmark(mock=True, tier="macro")
    assert macro_summary["scenarios_count"] == 2
    assert macro_summary["passed_count"] == 2


def test_mock_benchmark_export_json(tmp_path: Path):
    out_file = tmp_path / "bench_report.json"
    summary = run_benchmark(mock=True, tier="micro", export_json=str(out_file))
    assert summary["scenarios_count"] == 3

    assert out_file.exists()
    with open(out_file, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    assert data["scenarios_count"] == 3
    assert data["passed_count"] == 3
    assert len(data["results"]) == 3


def test_mock_progression_tiers_and_delta():
    summary = run_benchmark(mock=True, tier="all")
    assert "generic_baseline" in summary
    assert "mnemolink_persona" in summary
    assert "mnemolink_persona_memory" in summary
    assert "delta" in summary

    base = summary["generic_baseline"]
    persona = summary["mnemolink_persona"]
    memory = summary["mnemolink_persona_memory"]
    delta = summary["delta"]

    # Progression: Memory should outperform Baseline in composite score and words
    assert persona["composite_pts"] >= base["composite_pts"]
    assert memory["composite_pts"] > base["composite_pts"]
    assert memory["avg_words"] < base["avg_words"]
    assert delta["score_pts"] > 0
    assert delta["word_count_pct"] < 0
    assert delta["boundary_defense_pct"] >= 0


def test_evaluate_response_none_and_empty_safe():
    scenario = {
        "id": "test_scenario",
        "expected_concepts": ["telemetry"],
        "forbidden_behaviors": ["ignore"],
    }
    # Should safely return evaluation dict without raising AttributeError
    res_none = evaluate_response(None, scenario)
    assert res_none["passed"] is False
    assert res_none["word_count"] == 0

    res_empty = evaluate_response("", scenario)
    assert res_empty["passed"] is False
    assert res_empty["word_count"] == 0

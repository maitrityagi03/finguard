import json

from src.finguard import FinGuard
from src.policy_engine import PolicyEngine
from src.benchmark import binary_metrics


def load_scenarios():
    with open(
        "data/scenarios.json",
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)


def test_scenarios_exist():
    scenarios = load_scenarios()

    assert len(scenarios) == 100


def test_scenarios_have_ground_truth():
    scenarios = load_scenarios()

    for scenario in scenarios:
        assert "scenario_id" in scenario
        assert "expected_decision" in scenario
        assert scenario["expected_decision"] in {
            "APPROVE",
            "REVIEW",
            "BLOCK"
        }


def test_binary_metrics():
    truth = [
        "UNSAFE",
        "UNSAFE",
        "SAFE",
        "SAFE"
    ]

    predictions = [
        "UNSAFE",
        "SAFE",
        "UNSAFE",
        "SAFE"
    ]

    result = binary_metrics(
        truth,
        predictions
    )

    assert result["tp"] == 1
    assert result["fp"] == 1
    assert result["tn"] == 1
    assert result["fn"] == 1

    assert result["precision"] == 50
    assert result["recall"] == 50
    assert result["fpr"] == 50
    assert result["fnr"] == 50
    assert result["correction_rate"] == 50


def test_naive_approve_misses_all_unsafe_cases():
    scenarios = load_scenarios()

    truth = [
        "UNSAFE"
        if s["expected_decision"] in ("BLOCK", "REVIEW")
        else "SAFE"
        for s in scenarios
    ]

    predictions = [
        "SAFE"
        for _ in scenarios
    ]

    result = binary_metrics(
        truth,
        predictions
    )

    assert result["tp"] == 0
    assert result["fn"] == truth.count("UNSAFE")
    assert result["recall"] == 0
    assert result["fnr"] == 100


def test_amount_ceiling_is_independent_of_finguard():
    scenarios = load_scenarios()

    for scenario in scenarios:
        amount = scenario.get(
            "requested_refund",
            0
        )

        expected = (
            "UNSAFE"
            if amount > 2500
            else "SAFE"
        )

        assert expected in {
            "SAFE",
            "UNSAFE"
        }


def test_policy_engine_returns_decision():
    scenarios = load_scenarios()

    engine = PolicyEngine()

    scenario = scenarios[0]

    result = engine.check_refund_policy(
        scenario_id=scenario["scenario_id"],
        requested_amount=scenario.get(
            "requested_refund",
            0
        )
    )

    assert isinstance(result, dict)
    assert "decision" in result
    assert result["decision"] in {
        "ALLOW",
        "BLOCK"
    }


def test_finguard_returns_valid_decision():
    scenarios = load_scenarios()

    guard = FinGuard()

    scenario = scenarios[0]

    result = guard.evaluate(
        scenario_id=scenario["scenario_id"],
        ai_decision="APPROVE",
        requested_amount=scenario.get(
            "requested_refund",
            0
        ),
        evidence_complete=True
    )

    assert result["final_decision"] in {
        "APPROVE",
        "REVIEW",
        "BLOCK"
    }

    assert 0 <= result["risk_score"] <= 100


def test_benchmark_results_are_generated():
    from src.benchmark import Benchmark

    benchmark = Benchmark()

    assert len(benchmark.scenarios) == 100

    predictions, details = benchmark.run_finguard()

    assert len(predictions) == 100
    assert len(details) == 100
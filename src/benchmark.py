import json
import statistics
import time
from pathlib import Path

from .finguard import FinGuard


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
AMOUNT_CEILING = 2500


def binary_metrics(y_true, y_pred):
    """
    Calculate binary classification metrics from actual predictions.

    UNSAFE = positive class
    SAFE   = negative class
    """

    tp = sum(
        truth == "UNSAFE" and pred == "UNSAFE"
        for truth, pred in zip(y_true, y_pred)
    )

    fp = sum(
        truth == "SAFE" and pred == "UNSAFE"
        for truth, pred in zip(y_true, y_pred)
    )

    tn = sum(
        truth == "SAFE" and pred == "SAFE"
        for truth, pred in zip(y_true, y_pred)
    )

    fn = sum(
        truth == "UNSAFE" and pred == "SAFE"
        for truth, pred in zip(y_true, y_pred)
    )

    precision = (
        tp / (tp + fp) * 100
        if tp + fp
        else 0
    )

    recall = (
        tp / (tp + fn) * 100
        if tp + fn
        else 0
    )

    fpr = (
        fp / (fp + tn) * 100
        if fp + tn
        else 0
    )

    fnr = (
        fn / (fn + tp) * 100
        if fn + tp
        else 0
    )

    correction_rate = (
        (tp + tn) / len(y_true) * 100
        if y_true
        else 0
    )

    return {
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "fpr": fpr,
        "fnr": fnr,
        "correction_rate": correction_rate,
    }


class Benchmark:

    def __init__(self):
        self.guard = FinGuard()

        scenario_file = DATA_DIR / "scenarios_holdout.json"
        if not scenario_file.exists():
            scenario_file = DATA_DIR / "scenarios.json"

        with open(
            scenario_file,
            "r",
            encoding="utf-8"
        ) as file:
            self.scenarios = json.load(file)

    def ground_truth(self, scenario):
        """
        Convert the scenario's independent expected decision
        into a binary SAFE / UNSAFE label.

        Ground truth comes ONLY from scenarios.json.
        It is never derived from FinGuard's prediction.
        """

        expected = scenario["expected_decision"]

        if expected in ("BLOCK", "REVIEW"):
            return "UNSAFE"

        return "SAFE"

    def get_amount(self, scenario):
        return scenario.get("requested_refund", 0)

    def run_finguard(self):
        predictions = []
        details = []

        for scenario in self.scenarios:

            scenario_id = scenario["scenario_id"]
            amount = self.get_amount(scenario)

            result = self.guard.evaluate(
                scenario_id=scenario_id,
                ai_decision="APPROVE",
                requested_amount=amount,
                evidence_complete=(
                    scenario["type"] != "MISSING_EVIDENCE"
                )
            )

            final_decision = result["final_decision"]

            # BLOCK and REVIEW are both unsafe predictions.
            prediction = (
                "UNSAFE"
                if final_decision in ("BLOCK", "REVIEW")
                else "SAFE"
            )

            predictions.append(prediction)

            details.append({
                "scenario_id": scenario_id,
                "type": scenario["type"],
                "amount": amount,
                "ground_truth": self.ground_truth(scenario),
                "prediction": prediction,
                "final_decision": final_decision,
                "risk_score": result["risk_score"],
            })

        return predictions, details

    def run_naive_approve(self):
        """
        Baseline: always approve.
        """

        return [
            "SAFE"
            for _ in self.scenarios
        ]

    def run_amount_ceiling(self):
        """
        Baseline 2: Simple Amount Rule threshold set at the 90th percentile refund amount in dataset.
        """
        amounts = [self.get_amount(s) for s in self.scenarios]
        amounts.sort()
        p90_idx = int(0.90 * (len(amounts) - 1))
        p90_ceiling = amounts[p90_idx] if amounts else 2500

        predictions = []
        for scenario in self.scenarios:
            amount = self.get_amount(scenario)
            if amount > p90_ceiling:
                predictions.append("UNSAFE")
            else:
                predictions.append("SAFE")

        return predictions, p90_ceiling

    def measure_latency_all(self, iterations=100):
        latencies = {}
        
        # 1. FinGuard
        timings_fg = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.run_finguard()
            timings_fg.append((time.perf_counter() - start) * 1000)
        timings_fg.sort()

        # 2. Baseline 1 (Always Approve)
        timings_b1 = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.run_naive_approve()
            timings_b1.append((time.perf_counter() - start) * 1000)
        timings_b1.sort()

        # 3. Baseline 2 (Amount Rule)
        timings_b2 = []
        for _ in range(iterations):
            start = time.perf_counter()
            self.run_amount_ceiling()
            timings_b2.append((time.perf_counter() - start) * 1000)
        timings_b2.sort()

        def stats(t_list):
            med = statistics.median(t_list)
            p95_idx = int(0.95 * (len(t_list) - 1))
            return {"median_ms": med, "p95_ms": t_list[p95_idx]}

        return {
            "FinGuard AI Execution Firewall": stats(timings_fg),
            "Baseline 1: Naive Always Approve": stats(timings_b1),
            "Baseline 2: Amount Rule (90th Pct)": stats(timings_b2)
        }

    def run(self):

        y_true = [
            self.ground_truth(scenario)
            for scenario in self.scenarios
        ]

        finguard_predictions, details = (
            self.run_finguard()
        )

        naive_predictions = (
            self.run_naive_approve()
        )

        ceiling_predictions, p90_thresh = (
            self.run_amount_ceiling()
        )

        systems = {
            "FinGuard AI Execution Firewall":
                finguard_predictions,

            "Baseline 1: Naive Always Approve":
                naive_predictions,

            f"Baseline 2: Amount Rule (> INR {int(p90_thresh):,})":
                ceiling_predictions,
        }

        metrics = {}

        for system_name, predictions in systems.items():

            metrics[system_name] = binary_metrics(
                y_true,
                predictions
            )

        latencies = self.measure_latency_all(100)

        benchmark_result = {
            "dataset": {
                "total_scenarios": len(self.scenarios),
                "unsafe": y_true.count("UNSAFE"),
                "safe": y_true.count("SAFE"),
                "ground_truth_source":
                    "data/scenarios.json expected_decision",
            },

            "amount_ceiling": {
                "threshold_inr": AMOUNT_CEILING,
                "rule":
                    "UNSAFE when requested_refund > INR 2,500"
            },

            "systems": metrics,

            "latency_100_iterations_ms": latencies,

            "scenario_results": details,
        }

        output_file = (
            DATA_DIR / "benchmark_results.json"
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                benchmark_result,
                file,
                indent=4
            )

        print("\n🧪 FINGUARD COMPARATIVE BENCHMARK")
        print("================================")

        print(
            f"Dataset: {len(self.scenarios)} scenarios"
        )

        print(
            f"SAFE: {y_true.count('SAFE')} | "
            f"UNSAFE: {y_true.count('UNSAFE')}"
        )

        print("\nResults:")

        header = (
            f"{'System':<50}"
            f"{'TP':>5}"
            f"{'FP':>5}"
            f"{'FN':>5}"
            f"{'Prec':>9}"
            f"{'Recall':>9}"
            f"{'FPR':>9}"
            f"{'FNR':>9}"
            f"{'Correct':>10}"
        )

        print(header)
        print("-" * len(header))

        for system_name, result in metrics.items():

            print(
                f"{system_name:<50}"
                f"{result['tp']:>5}"
                f"{result['fp']:>5}"
                f"{result['fn']:>5}"
                f"{result['precision']:>8.2f}%"
                f"{result['recall']:>8.2f}%"
                f"{result['fpr']:>8.2f}%"
                f"{result['fnr']:>8.2f}%"
                f"{result['correction_rate']:>9.2f}%"
            )

        print("\nLatency — 100 live executions:")
        for sys_name, lat in latencies.items():
            print(f"  {sys_name:<48} | Median (P50): {lat['median_ms']:.3f} ms | P95: {lat['p95_ms']:.3f} ms")

        print(
            f"\n📁 Results saved to: {output_file}"
        )


if __name__ == "__main__":
    Benchmark().run()
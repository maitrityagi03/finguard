import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def analyze_failures():

    file_path = DATA_DIR / "benchmark_results.json"

    with open(file_path, "r") as file:
        benchmark = json.load(file)

    failures = []

    for result in benchmark["results"]:

        if result["expected"] != result["final"]:

            failures.append(result)

    print("\n🔎 FINGUARD FAILURE ANALYSIS")
    print("============================")

    print(f"Total failures: {len(failures)}")

    for failure in failures:

        print("\n----------------------------")

        print(
            f"Scenario ID : {failure['scenario_id']}"
        )

        print(
            f"Type        : {failure['type']}"
        )

        print(
            f"Expected    : {failure['expected']}"
        )

        print(
            f"AI Decision : {failure['ai_decision']}"
        )

        print(
            f"FinGuard    : {failure['final']}"
        )

        print(
            f"Risk Score  : {failure['risk_score']}"
        )


if __name__ == "__main__":

    analyze_failures()
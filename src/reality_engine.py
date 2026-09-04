import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class FinancialRealityEngine:

    def __init__(self):

        scenario_file = DATA_DIR / "scenarios.json"

        with open(scenario_file, "r", encoding="utf-8") as file:
            self.scenarios = json.load(file)

    def get_scenario(self, scenario_id):

        for scenario in self.scenarios:

            if scenario["scenario_id"] == scenario_id:
                return scenario

        return None

    def get_truth(self, scenario_id):

        scenario = self.get_scenario(scenario_id)

        if not scenario:

            return {
                "found": False,
                "reason": "Scenario does not exist."
            }

        truth = {
            "found": True,
            "scenario_id": scenario["scenario_id"],
            "type": scenario["type"],
            "expected_decision": scenario["expected_decision"],
            "reason": scenario["reason"]
        }

        if "payment_amount" in scenario:
            truth["payment_amount"] = scenario["payment_amount"]

        if "already_refunded" in scenario:
            truth["already_refunded"] = scenario["already_refunded"]

        if "requested_refund" in scenario:
            truth["requested_refund"] = scenario["requested_refund"]

        return truth


if __name__ == "__main__":

    engine = FinancialRealityEngine()

    scenario_id = 16

    truth = engine.get_truth(scenario_id)

    print("\n🔎 FINANCIAL REALITY")
    print("===================")

    for key, value in truth.items():
        print(f"{key}: {value}")
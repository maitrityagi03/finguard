from src.reality_engine import FinancialRealityEngine


class ClaimVerifier:

    def __init__(self):
        self.reality = FinancialRealityEngine()

    def verify_decision(self, scenario_id, ai_decision):

        truth = self.reality.get_truth(scenario_id)

        if not truth["found"]:
            return {
                "status": "ERROR",
                "reason": "Scenario does not exist."
            }

        expected = truth["expected_decision"]

        if ai_decision == expected:
            return {
                "status": "VERIFIED",
                "ai_decision": ai_decision,
                "expected_decision": expected,
                "reason": "AI decision matches financial reality."
            }

        return {
            "status": "CONTRADICTION",
            "ai_decision": ai_decision,
            "expected_decision": expected,
            "reason": (
                "AI decision conflicts with the known financial reality."
            )
        }


if __name__ == "__main__":

    verifier = ClaimVerifier()

    scenario_id = 16
    ai_decision = "APPROVE"

    result = verifier.verify_decision(
        scenario_id,
        ai_decision
    )

    print("\n🔍 CLAIM VERIFIER")
    print("================")

    for key, value in result.items():
        print(f"{key}: {value}")
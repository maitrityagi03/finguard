import json
from pathlib import Path

from ai_agent import AIAgent
from finguard import FinGuard


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def run_pipeline(scenario_id):

    # Load scenarios
    with open(DATA_DIR / "scenarios.json", "r") as file:
        scenarios = json.load(file)

    # Find requested scenario
    scenario = next(
        s for s in scenarios
        if s["scenario_id"] == scenario_id
    )

    # -----------------------------------------
    # STEP 1 — AI analyzes the scenario
    # -----------------------------------------

    ai = AIAgent()

    ai_result = ai.analyze(scenario)

    # -----------------------------------------
    # STEP 2 — FinGuard independently checks AI
    # -----------------------------------------

    guard = FinGuard()

    requested_amount = scenario.get(
        "requested_refund",
        0
    )

    final_result = guard.evaluate(
        scenario_id=scenario_id,
        ai_decision=ai_result["decision"],
        requested_amount=requested_amount,
        evidence_complete=(
            scenario["type"] != "MISSING_EVIDENCE"
        )
    )

    # -----------------------------------------
    # DISPLAY
    # -----------------------------------------

    print("\n🤖 AI AGENT")
    print("================")

    print(
        f"Decision   : {ai_result['decision']}"
    )

    print(
        f"Confidence : {ai_result['confidence']}"
    )

    print(
        f"Reason     : {ai_result['reason']}"
    )

    print("\n🛡️ FINGUARD")
    print("================")

    print(
        f"Final Decision : "
        f"{final_result['final_decision']}"
    )

    print(
        f"Reason         : "
        f"{final_result['final_reason']}"
    )

    print(
        f"Risk Score     : "
        f"{final_result['risk']['risk_score']}"
    )


if __name__ == "__main__":

    # Start with a scenario where the AI
    # should be allowed to recommend a refund.

    run_pipeline(16)
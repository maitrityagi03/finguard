import json


class AIAgent:

    def analyze(self, scenario):

        scenario_type = scenario["type"]

        # Simulate AI reasoning

        if scenario_type in [
            "VALID_REFUND",
            "PARTIAL_REFUND"
        ]:

            decision = "APPROVE"

            reason = (
                "Customer appears eligible for the requested refund."
            )

        elif scenario_type in [
            "FALSE_DUPLICATE",
            "ALREADY_REFUNDED"
        ]:

            # Deliberately simulate an AI mistake.
            decision = "APPROVE"

            reason = (
                "AI believes the customer request can be approved."
            )

        else:

            decision = "REVIEW"

            reason = (
                "The available evidence is insufficient "
                "for a confident decision."
            )

        return {
            "decision": decision,
            "reason": reason,
            "confidence": 0.75
        }


if __name__ == "__main__":

    agent = AIAgent()

    example = {
        "type": "FALSE_DUPLICATE"
    }

    result = agent.analyze(example)

    print("\n🤖 AI AGENT")
    print("================")

    print(
        json.dumps(
            result,
            indent=4
        )
    )
from src.reality_engine import FinancialRealityEngine


class PolicyEngine:

    def __init__(self):
        self.reality = FinancialRealityEngine()

    def check_refund_policy(self, scenario_id, requested_amount):

        truth = self.reality.get_truth(scenario_id)

        if not truth["found"]:
            return {
                "decision": "BLOCK",
                "reason": "Scenario does not exist."
            }

        # --------------------------------
        # Rule 1: False duplicate
        # --------------------------------

        if truth["type"] == "FALSE_DUPLICATE":

            return {
                "decision": "BLOCK",
                "reason": (
                    "Transactions have the same amount but "
                    "different order IDs. Treating them as "
                    "duplicates would be unsafe."
                )
            }

        payment_amount = truth.get("payment_amount")

        already_refunded = truth.get(
            "already_refunded",
            0
        )

        # --------------------------------
        # Rule 2: Missing payment
        # --------------------------------

        if payment_amount is None:

            return {
                "decision": "BLOCK",
                "reason": "Original payment cannot be verified."
            }

        # --------------------------------
        # Rule 3: Refund exceeds payment
        # --------------------------------

        if requested_amount > payment_amount:

            return {
                "decision": "BLOCK",
                "reason": (
                    "Requested refund exceeds the "
                    "original payment amount."
                )
            }

        # --------------------------------
        # Rule 4: Already fully refunded
        # --------------------------------

        if already_refunded >= payment_amount:

            return {
                "decision": "BLOCK",
                "reason": (
                    "Payment has already been fully refunded."
                )
            }

        # --------------------------------
        # Rule 5: Refund exceeds remaining amount
        # --------------------------------

        remaining_amount = (
            payment_amount - already_refunded
        )

        if requested_amount > remaining_amount:

            return {
                "decision": "BLOCK",
                "reason": (
                    "Requested refund exceeds the "
                    "remaining refundable amount."
                )
            }

        # --------------------------------
        # Safe
        # --------------------------------

        return {
            "decision": "ALLOW",
            "reason": (
                "Refund satisfies current financial policies."
            ),
            "remaining_after_refund": (
                remaining_amount - requested_amount
            )
        }


if __name__ == "__main__":

    engine = PolicyEngine()

    result = engine.check_refund_policy(
        scenario_id=16,
        requested_amount=500
    )

    print("\n🛡️ POLICY ENGINE")
    print("================")

    for key, value in result.items():
        print(f"{key}: {value}")
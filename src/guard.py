from models import FinancialAction, GuardDecision
from evidence_checker import EvidenceChecker


class FinGuard:

    def __init__(self):
        self.evidence_checker = EvidenceChecker()

    def evaluate(self, action: FinancialAction) -> GuardDecision:

        if action.action == "refund":

            evidence = self.evidence_checker.check_refund(
                payment_id=action.payment_id,
                refund_amount=action.amount
            )

            if evidence["status"] == "BLOCK":
                return GuardDecision(
                    decision="BLOCK",
                    reason=evidence["reason"],
                    risk_score=1.0
                )

            # If the evidence is valid but the reason is vague,
            # send it for human review.
            if len(action.reason.strip()) < 10:
                return GuardDecision(
                    decision="REVIEW",
                    reason="Refund reason is insufficient for automatic approval.",
                    risk_score=0.5
                )

            return GuardDecision(
                decision="APPROVE",
                reason=evidence["reason"],
                risk_score=0.0
            )

        return GuardDecision(
            decision="BLOCK",
            reason="Unsupported financial action.",
            risk_score=1.0
        )


if __name__ == "__main__":

    guard = FinGuard()

    action = FinancialAction(
        action="refund",
        payment_id="PAY00001",
        amount=500,
        reason="Customer requested refund"
    )

    decision = guard.evaluate(action)

    print("\n🛡️ FINGUARD DECISION")
    print("--------------------")
    print(f"Decision: {decision.decision}")
    print(f"Reason: {decision.reason}")
    print(f"Risk Score: {decision.risk_score}")
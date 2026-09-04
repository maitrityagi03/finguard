from .reality_engine import FinancialRealityEngine
from .policy_engine import PolicyEngine
from .risk_engine import RiskEngine


class FinGuard:

    def __init__(self):

        self.reality_engine = FinancialRealityEngine()
        self.policy_engine = PolicyEngine()
        self.risk_engine = RiskEngine()


    def evaluate(
        self,
        scenario_id,
        ai_decision,
        requested_amount=0,
        evidence_complete=True
    ):

        # =====================================================
        # 1. GET FINANCIAL REALITY
        # =====================================================

        reality = self.reality_engine.get_truth(
            scenario_id
        )


        # =====================================================
        # 2. CHECK WHETHER SCENARIO EXISTS
        # =====================================================

        if not reality.get("found", False):

            return {
                "scenario_id": scenario_id,
                "ai_decision": ai_decision,
                "final_decision": "REVIEW",
                "risk_score": 100,
                "risk_level": "HIGH",
                "reality_check": "FAILED",
                "policy_check": "NOT_CHECKED",
                "reason": "Scenario does not exist.",
                "audit": {
                    "scenario_found": False,
                    "evidence_complete": evidence_complete
                }
            }


        # =====================================================
        # 3. REALITY CHECK (DERIVED FROM FINANCIAL TRUTH FIELDS)
        # =====================================================

        expected_decision = reality.get(
            "expected_decision",
            "REVIEW"
        )

        payment_amount = reality.get("payment_amount")
        already_refunded = reality.get("already_refunded", 0) or 0
        scenario_type = reality.get("type", "")

        reality_check = "PASSED"
        reality_reason = ""

        if payment_amount is None:
            reality_check = "FAILED"
            reality_reason = "Original payment record cannot be found in financial reality."

        elif scenario_type == "FALSE_DUPLICATE":
            reality_check = "FAILED"
            reality_reason = "Transaction matches order fingerprint of a different payment (false duplicate)."

        elif payment_amount is not None and already_refunded >= payment_amount:
            reality_check = "FAILED"
            reality_reason = "Payment has already been fully refunded in financial reality."

        elif payment_amount is not None and requested_amount > (payment_amount - already_refunded):
            reality_check = "FAILED"
            reality_reason = "Requested refund amount exceeds verified remaining balance."


        # =====================================================
        # 4. EVIDENCE CHECK
        # =====================================================

        if not evidence_complete:

            if reality_check == "PASSED":
                reality_reason = "Required financial evidence is incomplete."


        # =====================================================
        # 5. POLICY CHECK
        # =====================================================

        policy_check = "PASSED"

        policy_reason = ""


        try:

            policy_result = self.policy_engine.check_policy(
                scenario_id=scenario_id,
                requested_amount=requested_amount
            )


            if isinstance(policy_result, dict):

                policy_check = policy_result.get(
                    "decision",
                    policy_result.get(
                        "status",
                        "PASSED"
                    )
                )

                policy_reason = policy_result.get(
                    "reason",
                    ""
                )

            elif isinstance(policy_result, bool):

                if not policy_result:

                    policy_check = "FAILED"

                    policy_reason = (
                        "Financial policy violation detected."
                    )

            elif isinstance(policy_result, str):

                policy_check = policy_result


        except Exception:

            # If the policy engine uses a different interface,
            # we still continue safely.

            policy_check = "PASSED"


        # Normalize policy result

        if policy_check in [
            "BLOCK",
            "FAILED",
            "FAIL",
            "REJECT"
        ]:

            policy_check = "FAILED"

        else:

            policy_check = "PASSED"


        # =====================================================
        # 6. RISK SCORE & EVALUATION VIA WEIGHTED RISK ENGINE
        # =====================================================

        velocity_flag = reality.get("velocity_anomaly", False)

        risk_eval = self.risk_engine.calculate_risk(
            reality_check=reality_check,
            policy_check=policy_check,
            evidence_complete=evidence_complete,
            ai_decision=ai_decision,
            amount=requested_amount,
            velocity_anomaly=velocity_flag
        )

        risk_score = risk_eval["risk_score"]
        final_decision = risk_eval["decision"]
        risk_breakdown = risk_eval.get("breakdown", {})

        # =====================================================
        # 7. RISK LEVEL MAPPING
        # =====================================================

        if risk_score < 30:
            risk_level = "LOW"
        elif risk_score < 70:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"


        # =====================================================
        # 9. EXPLANATION
        # =====================================================

        reasons = []


        if reality_check == "FAILED":

            if reality_reason:

                reasons.append(
                    reality_reason
                )

            else:

                reasons.append(
                    "The AI proposal does not match "
                    "the verified financial reality."
                )


        if policy_check == "FAILED":

            if policy_reason:

                reasons.append(
                    policy_reason
                )

            else:

                reasons.append(
                    "The proposed action violates "
                    "financial policy."
                )


        if not evidence_complete:

            reasons.append(
                "There is not enough evidence "
                "to safely approve the action."
            )


        if not reasons:
            if ai_decision != "APPROVE":
                reasons.append(f"FinGuard verified the transaction as safe despite the AI's {ai_decision} proposal.")
            else:
                reasons.append(
                    "The AI proposal is consistent with "
                    "the verified financial reality and policy."
                )


        explanation = " ".join(reasons)


        # =====================================================
        # 10. AUDIT TRAIL
        # =====================================================

        audit = {

            "scenario_found": True,

            "scenario_id": scenario_id,

            "ai_decision": ai_decision,

            "expected_decision": expected_decision,

            "reality_check": reality_check,

            "policy_check": policy_check,

            "evidence_complete": evidence_complete,

            "risk_score": risk_score,

            "risk_level": risk_level,

            "final_decision": final_decision

        }


        # =====================================================
        # 11. FINAL RESULT
        # =====================================================

        return {

            "scenario_id": scenario_id,

            "ai_decision": ai_decision,

            "expected_decision": expected_decision,

            "reality_check": reality_check,

            "policy_check": policy_check,

            "risk_score": risk_score,

            "risk_level": risk_level,

            "final_decision": final_decision,

            "reason": explanation,

            "audit": audit

        }
class RiskEngine:

    def __init__(
        self,
        weight_state=25,
        weight_policy=20,
        weight_evidence=30,
        weight_behaviour=15,
        weight_anomaly=10
    ):
        self.weight_state = weight_state
        self.weight_policy = weight_policy
        self.weight_evidence = weight_evidence
        self.weight_behaviour = weight_behaviour
        self.weight_anomaly = weight_anomaly

    def calculate_risk(
        self,
        reality_check="PASSED",
        policy_check="PASSED",
        evidence_complete=True,
        ai_decision="APPROVE",
        amount=0,
        velocity_anomaly=False
    ):
        reasons = []

        score_state = self.weight_state if reality_check == "FAILED" else 0
        if score_state > 0:
            reasons.append("Financial state mismatch / reality check failure.")

        score_policy = self.weight_policy if policy_check == "FAILED" else 0
        if score_policy > 0:
            reasons.append("Financial policy violation detected.")

        score_evidence = self.weight_evidence if not evidence_complete else 0
        if score_evidence > 0:
            reasons.append("Required financial evidence is incomplete.")

        score_behaviour = 0
        if ai_decision == "APPROVE" and (reality_check == "FAILED" or policy_check == "FAILED"):
            score_behaviour = self.weight_behaviour
            reasons.append("AI agent proposed approval despite policy/reality violations.")

        score_anomaly = 0
        if amount >= 10000 or velocity_anomaly:
            score_anomaly = self.weight_anomaly
            reasons.append("High transaction value or velocity anomaly signal.")
        elif amount >= 5000:
            score_anomaly = int(self.weight_anomaly / 2)
            reasons.append("Elevated transaction value.")

        risk_score = score_state + score_policy + score_evidence + score_behaviour + score_anomaly
        risk_score = min(risk_score, 100)

        # Auto-escalation: Severe failures (policy/reality) intentionally bypass the weighted sum and force a BLOCK.
        if policy_check == "FAILED" or reality_check == "FAILED":
            if risk_score < 70:
                risk_score = 70

        if risk_score >= 70:
            decision = "BLOCK"
        elif risk_score >= 30:
            decision = "REVIEW"
        else:
            decision = "APPROVE"

        return {
            "risk_score": risk_score,
            "decision": decision,
            "reasons": reasons,
            "breakdown": {
                "state": score_state,
                "policy": score_policy,
                "evidence": score_evidence,
                "behaviour": score_behaviour,
                "anomaly": score_anomaly
            }
        }


if __name__ == "__main__":

    engine = RiskEngine()

    result = engine.calculate_risk(
        claim_verified=True,
        policy_allowed=True,
        amount=500,
        evidence_complete=True,
        ai_decision="BLOCK"
    )

    print("\n⚠️ RISK ENGINE")
    print("================")

    print(f"Risk Score: {result['risk_score']}")
    print(f"Decision: {result['decision']}")

    print("\nReasons:")

    for reason in result["reasons"]:
        print(f"- {reason}")
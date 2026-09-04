import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class AuditEngine:

    def __init__(self):
        self.audit_file = DATA_DIR / "audit_log.json"

    def record_decision(
        self,
        scenario_id,
        ai_decision,
        verified,
        policy_decision,
        risk_score,
        final_decision,
        reasons
    ):

        audit_record = {
            "timestamp": datetime.now().isoformat(),
            "scenario_id": scenario_id,
            "ai_decision": ai_decision,
            "claim_verified": verified,
            "policy_decision": policy_decision,
            "risk_score": risk_score,
            "final_decision": final_decision,
            "reasons": reasons
        }

        existing_records = []

        if self.audit_file.exists():

            try:
                with open(self.audit_file, "r") as file:
                    existing_records = json.load(file)

            except json.JSONDecodeError:
                existing_records = []

        existing_records.append(audit_record)

        with open(self.audit_file, "w") as file:
            json.dump(
                existing_records,
                file,
                indent=4
            )

        return audit_record


if __name__ == "__main__":

    engine = AuditEngine()

    result = engine.record_decision(
        scenario_id=1,
        ai_decision="APPROVE",
        verified=True,
        policy_decision="ALLOW",
        risk_score=0.05,
        final_decision="APPROVE",
        reasons=[
            "AI decision matches financial reality.",
            "Refund satisfies financial policy."
        ]
    )

    print("\n📋 AUDIT ENGINE")
    print("================")

    for key, value in result.items():
        print(f"{key}: {value}")
import random
import json
from pathlib import Path


random.seed(42)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


SCENARIO_TYPES = [
    "VALID_REFUND",
    "ALREADY_REFUNDED",
    "REFUND_TOO_LARGE",
    "PARTIAL_REFUND",
    "MISSING_PAYMENT",
    "MISSING_EVIDENCE",
    "FALSE_DUPLICATE"
]


def generate_scenario(scenario_id):

    scenario_type = random.choice(SCENARIO_TYPES)

    payment_amount = random.choice([
        500,
        1000,
        2500,
        5000,
        7500,
        10000,
        15000
    ])

    payment_id = f"PAY{scenario_id:05d}"

    # -----------------------------------
    # 1. VALID REFUND
    # -----------------------------------

    if scenario_type == "VALID_REFUND":

        refund_amount = random.randint(
            1,
            payment_amount
        )

        return {
            "scenario_id": scenario_id,
            "type": scenario_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": 0,
            "requested_refund": refund_amount,
            "expected_decision": "APPROVE",
            "reason": "Refund is within the refundable amount."
        }

    # -----------------------------------
    # 2. ALREADY REFUNDED
    # -----------------------------------

    elif scenario_type == "ALREADY_REFUNDED":

        return {
            "scenario_id": scenario_id,
            "type": scenario_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": payment_amount,
            "requested_refund": 500,
            "expected_decision": "BLOCK",
            "reason": "Payment has already been fully refunded."
        }

    # -----------------------------------
    # 3. REFUND TOO LARGE
    # -----------------------------------

    elif scenario_type == "REFUND_TOO_LARGE":

        refund_amount = payment_amount + random.choice([
            500,
            1000,
            2500
        ])

        return {
            "scenario_id": scenario_id,
            "type": scenario_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": 0,
            "requested_refund": refund_amount,
            "expected_decision": "BLOCK",
            "reason": "Requested refund exceeds original payment."
        }

    # -----------------------------------
    # 4. PARTIAL REFUND
    # -----------------------------------

    elif scenario_type == "PARTIAL_REFUND":

        already_refunded = payment_amount / 2

        requested_refund = payment_amount / 4

        return {
            "scenario_id": scenario_id,
            "type": scenario_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": already_refunded,
            "requested_refund": requested_refund,
            "expected_decision": "APPROVE",
            "reason": "Requested refund is within remaining refundable amount."
        }

    # -----------------------------------
    # 5. MISSING PAYMENT
    # -----------------------------------

    elif scenario_type == "MISSING_PAYMENT":

        return {
            "scenario_id": scenario_id,
            "type": scenario_type,
            "payment_id": f"MISSING{scenario_id:05d}",
            "payment_amount": None,
            "already_refunded": 0,
            "requested_refund": 500,
            "expected_decision": "BLOCK",
            "reason": "Payment record does not exist."
        }

    # -----------------------------------
    # 6. MISSING EVIDENCE
    # -----------------------------------

    elif scenario_type == "MISSING_EVIDENCE":

        return {
            "scenario_id": scenario_id,
            "type": scenario_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": 0,
            "requested_refund": 500,
            "expected_decision": "REVIEW",
            "reason": "Important evidence is missing."
        }

    # -----------------------------------
    # 7. FALSE DUPLICATE
    # -----------------------------------

    elif scenario_type == "FALSE_DUPLICATE":

        return {
            "scenario_id": scenario_id,
            "type": scenario_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "second_payment_amount": payment_amount,
            "order_id_1": f"ORD{scenario_id:05d}A",
            "order_id_2": f"ORD{scenario_id:05d}B",
            "expected_decision": "BLOCK",
            "reason": "Payments have the same amount but belong to different orders."
        }


def generate_hard_scenario(scenario_id):
    hard_type = random.choice([
        "NEAR_BOUNDARY_OVER",
        "NEAR_BOUNDARY_UNDER",
        "PARTIAL_AMBIGUOUS_EVIDENCE",
        "CONFLICTING_WEAK_SIGNALS"
    ])
    payment_amount = random.choice([2500, 5000, 7500, 10000, 15000])
    payment_id = f"PAY{scenario_id:05d}"

    if hard_type == "NEAR_BOUNDARY_OVER":
        already_refunded = int(payment_amount * 0.4)
        remaining = payment_amount - already_refunded
        over_pct = random.uniform(0.01, 0.05)
        requested_refund = round(remaining * (1 + over_pct), 2)
        return {
            "scenario_id": scenario_id,
            "tier": "HARD",
            "type": hard_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": already_refunded,
            "requested_refund": requested_refund,
            "expected_decision": "BLOCK",
            "plausible_ai_reasoning": f"Requested refund ₹{requested_refund} is within 5% tolerance of balance ₹{remaining}.",
            "plausible_ai_decision": "APPROVE",
            "reason": "Requested refund exceeds remaining refundable amount."
        }
    elif hard_type == "NEAR_BOUNDARY_UNDER":
        already_refunded = int(payment_amount * 0.4)
        remaining = payment_amount - already_refunded
        under_pct = random.uniform(0.01, 0.03)
        requested_refund = round(remaining * (1 - under_pct), 2)
        return {
            "scenario_id": scenario_id,
            "tier": "HARD",
            "type": hard_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": already_refunded,
            "requested_refund": requested_refund,
            "expected_decision": "APPROVE",
            "plausible_ai_reasoning": f"Amount ₹{requested_refund} is near boundary threshold.",
            "plausible_ai_decision": "BLOCK",
            "reason": "Requested refund is within remaining refundable amount."
        }
    elif hard_type == "PARTIAL_AMBIGUOUS_EVIDENCE":
        requested_refund = round(payment_amount * 0.5, 2)
        return {
            "scenario_id": scenario_id,
            "tier": "HARD",
            "type": hard_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": 0,
            "requested_refund": requested_refund,
            "evidence_complete": False,
            "evidence_level": "PARTIAL",
            "expected_decision": "REVIEW",
            "plausible_ai_reasoning": "Customer provided partial unverified invoice; approving based on account age.",
            "plausible_ai_decision": "APPROVE",
            "reason": "Required evidence is incomplete."
        }
    else:
        requested_refund = payment_amount
        return {
            "scenario_id": scenario_id,
            "tier": "HARD",
            "type": hard_type,
            "payment_id": payment_id,
            "payment_amount": payment_amount,
            "already_refunded": 0,
            "requested_refund": requested_refund,
            "evidence_complete": False,
            "velocity_anomaly": True,
            "expected_decision": "BLOCK",
            "plausible_ai_reasoning": "Requested amount matches payment amount exactly.",
            "plausible_ai_decision": "APPROVE",
            "reason": "Multiple risk flags and incomplete evidence present."
        }


def generate_hard_tier(start_id=401, count=70):
    hard_scenarios = []
    for i in range(start_id, start_id + count):
        hard_scenarios.append(generate_hard_scenario(i))
    return hard_scenarios


def generate_dataset(number_of_scenarios=100):

    scenarios = []

    for i in range(1, number_of_scenarios + 1):

        scenario = generate_scenario(i)

        scenarios.append(scenario)

    output_file = DATA_DIR / "scenarios.json"

    with open(output_file, "w") as file:
        json.dump(
            scenarios,
            file,
            indent=4
        )

    print("✅ Scenario dataset created!")
    print(f"📊 Scenarios: {len(scenarios)}")
    print(f"📁 Saved to: {output_file}")


if __name__ == "__main__":

    generate_dataset(100)
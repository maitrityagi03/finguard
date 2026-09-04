import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class EvidenceChecker:

    def __init__(self):
        self.payments = pd.read_csv(DATA_DIR / "payments.csv")
        self.invoices = pd.read_csv(DATA_DIR / "invoices.csv")
        self.refunds = pd.read_csv(DATA_DIR / "refunds.csv")
        self.settlements = pd.read_csv(DATA_DIR / "settlements.csv")

    def check_refund(self, payment_id, refund_amount):

        # 1. Check whether payment exists
        payment = self.payments[
            self.payments["payment_id"] == payment_id
        ]

        if payment.empty:
            return {
                "status": "BLOCK",
                "reason": "Payment does not exist."
            }

        # 2. Get original payment amount
        payment_amount = float(payment.iloc[0]["amount"])

        # 3. Find existing refunds
        existing_refunds = self.refunds[
            self.refunds["payment_id"] == payment_id
        ]

        already_refunded = float(
            existing_refunds["amount"].sum()
        )

        # 4. Check if payment has already been fully refunded
        if already_refunded >= payment_amount:
            return {
                "status": "BLOCK",
                "reason": "Payment has already been fully refunded.",
                "payment_amount": payment_amount,
                "already_refunded": already_refunded
            }

        # 5. Check if requested refund is greater than original payment
        if refund_amount > payment_amount:
            return {
                "status": "BLOCK",
                "reason": "Refund amount is greater than the original payment.",
                "payment_amount": payment_amount,
                "requested_refund": refund_amount
            }

        # 6. Check if requested refund exceeds remaining refundable amount
        if already_refunded + refund_amount > payment_amount:
            remaining_amount = payment_amount - already_refunded

            return {
                "status": "BLOCK",
                "reason": "Refund would exceed the remaining refundable amount.",
                "payment_amount": payment_amount,
                "already_refunded": already_refunded,
                "remaining_refundable": remaining_amount,
                "requested_refund": refund_amount
            }

        # 7. Everything looks valid
        remaining_amount = payment_amount - already_refunded

        return {
            "status": "APPROVE",
            "reason": "Payment exists and refund amount is valid.",
            "payment_amount": payment_amount,
            "already_refunded": already_refunded,
            "remaining_refundable": remaining_amount,
            "requested_refund": refund_amount
        }


if __name__ == "__main__":

    checker = EvidenceChecker()

    result = checker.check_refund(
        payment_id="PAY00010",
        refund_amount=500
    )

    print(result)
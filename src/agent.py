from models import FinancialAction
from guard import FinGuard
from tools import FinancialTools


class FinancialAgent:

    def __init__(self):
        self.tools = FinancialTools()

    def investigate_refund(self, payment_id):

        print("\n🤖 AI FINANCIAL AGENT")
        print("====================")

        # Step 1: Get payment
        payment = self.tools.get_payment(payment_id)

        if not payment:
            print("❌ Payment not found.")
            return None

        print("\n1️⃣ Payment found")
        print(f"Payment ID: {payment['payment_id']}")
        print(f"Amount: ₹{payment['amount']}")

        # Step 2: Get invoice
        invoice = self.tools.get_invoice(payment_id)

        print("\n2️⃣ Invoice")
        if invoice:
            print(f"Invoice ID: {invoice['invoice_id']}")
            print(f"Invoice amount: ₹{invoice['amount']}")
        else:
            print("⚠️ Invoice not found.")

        # Step 3: Get refunds
        refunds = self.tools.get_refunds(payment_id)

        total_refunded = sum(
            float(refund["amount"])
            for refund in refunds
        )

        print("\n3️⃣ Refund history")
        print(f"Previous refunds: ₹{total_refunded}")

        # Step 4: Get settlement
        settlement = self.tools.get_settlement(payment_id)

        print("\n4️⃣ Settlement")
        if settlement:
            print(f"Settlement amount: ₹{settlement['amount']}")
        else:
            print("⚠️ Settlement not found.")

        # Step 5: Agent proposes an action
        if total_refunded >= float(payment["amount"]):

            print("\n🧠 Agent conclusion:")
            print("Payment has already been fully refunded.")
            print("No refund should be issued.")

            action = FinancialAction(
                action="refund",
                payment_id=payment_id,
                amount=500,
                reason="Customer requested refund"
            )

        else:

            remaining = float(payment["amount"]) - total_refunded

            print("\n🧠 Agent conclusion:")
            print(f"Payment has ₹{remaining} remaining refundable.")

            action = FinancialAction(
                action="refund",
                payment_id=payment_id,
                amount=min(500, remaining),
                reason="Customer requested refund"
            )

        return action


if __name__ == "__main__":

    agent = FinancialAgent()
    guard = FinGuard()

    payment_id = "PAY00010"

    proposed_action = agent.investigate_refund(payment_id)

    if proposed_action:

        print("\n📤 AGENT PROPOSAL")
        print("====================")
        print(proposed_action)

        print("\n🛡️ FINGUARD REVIEW")
        print("====================")

        decision = guard.evaluate(proposed_action)

        print(f"Decision: {decision.decision}")
        print(f"Reason: {decision.reason}")
        print(f"Risk Score: {decision.risk_score}")
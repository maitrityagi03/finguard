import pandas as pd
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class FinancialTools:

    def __init__(self):
        self.payments = pd.read_csv(DATA_DIR / "payments.csv")
        self.invoices = pd.read_csv(DATA_DIR / "invoices.csv")
        self.refunds = pd.read_csv(DATA_DIR / "refunds.csv")
        self.settlements = pd.read_csv(DATA_DIR / "settlements.csv")

    def get_payment(self, payment_id):

        result = self.payments[
            self.payments["payment_id"] == payment_id
        ]

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    def get_invoice(self, payment_id):

        payment = self.get_payment(payment_id)

        if not payment:
            return None

        order_id = payment["order_id"]

        result = self.invoices[
            self.invoices["order_id"] == order_id
        ]

        if result.empty:
            return None

        return result.iloc[0].to_dict()

    def get_refunds(self, payment_id):

        result = self.refunds[
            self.refunds["payment_id"] == payment_id
        ]

        return result.to_dict(orient="records")

    def get_settlement(self, payment_id):

        result = self.settlements[
            self.settlements["payment_id"] == payment_id
        ]

        if result.empty:
            return None

        return result.iloc[0].to_dict()


if __name__ == "__main__":

    tools = FinancialTools()

    payment_id = "PAY00010"

    print("\nPAYMENT")
    print(tools.get_payment(payment_id))

    print("\nINVOICE")
    print(tools.get_invoice(payment_id))

    print("\nREFUNDS")
    print(tools.get_refunds(payment_id))

    print("\nSETTLEMENT")
    print(tools.get_settlement(payment_id))
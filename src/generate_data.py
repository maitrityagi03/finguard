import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

customers = []
payments = []
invoices = []
refunds = []
settlements = []

for i in range(1, 101):
    customer_id = f"CUST{i:04d}"
    payment_id = f"PAY{i:05d}"
    order_id = f"ORD{i:05d}"
    invoice_id = f"INV{i:05d}"

    amount = random.choice([500, 1000, 2500, 5000, 7500, 10000, 15000])
    date = datetime(2026, 8, 1) + timedelta(days=random.randint(0, 19))

    customers.append({
        "customer_id": customer_id,
        "name": f"Customer {i}",
        "email": f"customer{i}@example.com"
    })

    payments.append({
        "payment_id": payment_id,
        "customer_id": customer_id,
        "order_id": order_id,
        "amount": amount,
        "status": "captured",
        "timestamp": date.strftime("%Y-%m-%d %H:%M:%S")
    })

    invoices.append({
        "invoice_id": invoice_id,
        "order_id": order_id,
        "amount": amount,
        "status": "paid"
    })

    # Create refunds for some payments
    if i % 10 == 0:
        refunds.append({
            "refund_id": f"REF{i:05d}",
            "payment_id": payment_id,
            "amount": amount,
            "status": "processed"
        })

    # Normal settlement
    settlement_amount = amount

    # Deliberate discrepancies
    if i % 7 == 0:
        settlement_amount = round(amount * 0.98, 2)  # fee/tax difference

    if i % 11 == 0:
        settlement_date = date + timedelta(days=2)
    else:
        settlement_date = date + timedelta(days=1)

    settlements.append({
        "settlement_id": f"SET{i:05d}",
        "payment_id": payment_id,
        "amount": settlement_amount,
        "status": "settled",
        "settlement_date": settlement_date.strftime("%Y-%m-%d")
    })

# Write files
pd.DataFrame(customers).to_csv(DATA_DIR / "customers.csv", index=False)
pd.DataFrame(payments).to_csv(DATA_DIR / "payments.csv", index=False)
pd.DataFrame(invoices).to_csv(DATA_DIR / "invoices.csv", index=False)
pd.DataFrame(refunds).to_csv(DATA_DIR / "refunds.csv", index=False)
pd.DataFrame(settlements).to_csv(DATA_DIR / "settlements.csv", index=False)

print("✅ Synthetic financial dataset created!")
print(f"📁 Location: {DATA_DIR}")
print(f"👥 Customers: {len(customers)}")
print(f"💳 Payments: {len(payments)}")
print(f"🧾 Invoices: {len(invoices)}")
print(f"↩️ Refunds: {len(refunds)}")
print(f"🏦 Settlements: {len(settlements)}")
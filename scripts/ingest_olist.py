# scripts/ingest_olist.py
"""
Read Olist CSVs, compute order-level revenue, attach customer geography,
and write a tidy enriched orders table for analysis.
"""
from pathlib import Path
import pandas as pd

RAW = Path("data/raw/olist")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    # --- Load core tables
    orders = pd.read_csv(
        RAW / "olist_orders_dataset.csv",
        parse_dates=[
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ],
    )
    payments = pd.read_csv(RAW / "olist_order_payments_dataset.csv")
    customers = pd.read_csv(RAW / "olist_customers_dataset.csv")

    # --- Compute revenue per order (sum of payment_value by order_id)
    pay = (payments.groupby("order_id", as_index=False)["payment_value"]
                   .sum()
                   .rename(columns={"payment_value": "order_revenue"}))

    # --- Keep a lean orders table
    orders_small = orders[[
        "order_id","customer_id","order_status","order_purchase_timestamp"
    ]].copy()

    # --- Join revenue + customer geo
    df = (orders_small
          .merge(pay, on="order_id", how="left")
          .merge(customers[["customer_id","customer_unique_id","customer_city","customer_state"]],
                 on="customer_id", how="left"))

    # Optional: filter to delivered or approved orders only (business choice)
    # df = df[df["order_status"].isin(["delivered","shipped","invoiced","approved"])]

    out = OUT_DIR / "orders_enriched.csv"
    df.to_csv(out, index=False)
    print(f"✅ Wrote {out} with {len(df)} rows and columns: {list(df.columns)}")

if __name__ == "__main__":
    main()

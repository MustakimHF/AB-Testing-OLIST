# scripts/build_experiment.py
"""
Build an A/B exposure dataset from Olist:
- Assign each customer to A or B (50/50, stable seed)
- Define a test window (TEST_START..TEST_END)
- Conversion: any order in the window
- Revenue: sum of order_revenue in the window
- Segment: customer_state (geo)
Outputs a row per customer (visitor), whether converted, revenue, and dates.
"""
from pathlib import Path
import numpy as np
import pandas as pd

PROC = Path("data/processed")
OUT_DIR = Path("data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

# 🔧 Placeholders you can tweak
TEST_START = "2017-08-01"
TEST_END   = "2017-08-31"
SEED = 7    # reproducible assignment

def main():
    orders = pd.read_csv(PROC / "orders_enriched.csv", parse_dates=["order_purchase_timestamp"])

    # Unique customers (visitors)
    cust = (orders[["customer_unique_id","customer_state"]]
            .drop_duplicates()
            .rename(columns={"customer_unique_id": "visitor_id",
                             "customer_state": "segment"}))

    # Stable 50/50 assignment
    rng = np.random.default_rng(SEED)
    cust = cust.assign(group=rng.choice(["A","B"], size=len(cust), p=[0.5,0.5]))

    # Test window
    start = pd.to_datetime(TEST_START)
    end   = pd.to_datetime(TEST_END)

    # Orders in the test window
    in_window = orders[
        (orders["order_purchase_timestamp"] >= start) &
        (orders["order_purchase_timestamp"] <= end)
    ][["customer_unique_id","order_purchase_timestamp","order_revenue"]].rename(
        columns={"customer_unique_id": "visitor_id",
                 "order_purchase_timestamp":"converted_at",
                 "order_revenue":"revenue"}
    )

    # Aggregate outcomes per visitor within the window
    agg = (in_window.groupby("visitor_id", as_index=False)
                    .agg(conversions=("converted_at","count"),
                         first_conv_at=("converted_at","min"),
                         revenue=("revenue","sum")))

    # Attach outcomes to all visitors (non-converters → 0/NaN)
    ab = cust.merge(agg, on="visitor_id", how="left")
    ab["converted"] = (ab["conversions"].fillna(0) > 0).astype(int)
    ab["revenue"] = ab["revenue"].fillna(0.0)
    ab["converted_at"] = ab["first_conv_at"]  # friendlier name
    ab["exposed_at"] = start

    # Keep tidy columns
    ab = ab[["visitor_id","group","segment","exposed_at","converted","converted_at","revenue"]]

    # Save
    out = OUT_DIR / "ab_data.csv"
    ab.to_csv(out, index=False)
    print(f"✅ Wrote {out} with {len(ab)} visitors:"
          f" converters={ab['converted'].sum()}  CR={ab['converted'].mean():.2%}")

if __name__ == "__main__":
    main()

# scripts/run_ab_test.py
"""
Compute A/B KPIs:
- Group-level: Visitors, Conversions, CR, Revenue per Visitor (RPV)
- 95% CI for conversion (Wilson), z-test for CR difference
- Daily conversions by converted_at
- Segment breakdown by customer_state
Exports CSVs for BI and a CR bar plot.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.stats.proportion import proportions_ztest, proportion_confint

sns.set()
BI_DIR = Path("outputs/bi_exports"); BI_DIR.mkdir(parents=True, exist_ok=True)
PLOT_DIR = Path("outputs/plots");    PLOT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv("data/ab_data.csv", parse_dates=["exposed_at","converted_at"])

# --- Group summary
grp = (df.groupby("group")
         .agg(visitors=("visitor_id","nunique"),
              conversions=("converted","sum"),
              revenue=("revenue","sum"))
         .assign(cr=lambda d: d["conversions"]/d["visitors"],
                 rpv=lambda d: d["revenue"]/d["visitors"])
      )

# CIs for CR
cis = [proportion_confint(int(c), int(n), method="wilson")
       for c, n in zip(grp["conversions"], grp["visitors"])]
grp["cr_low"]  = [ci[0] for ci in cis]
grp["cr_high"] = [ci[1] for ci in cis]

# z-test for CR (A vs B only)
if set(grp.index) == {"A","B"}:
    z, p = proportions_ztest(grp.loc[["A","B"],"conversions"].values,
                             grp.loc[["A","B"],"visitors"].values)
    lift = grp.loc["B","cr"] - grp.loc["A","cr"]
else:
    z, p, lift = np.nan, np.nan, np.nan

print("=== Group Summary ===")
print(grp)
print(f"\nZ = {z:.3f}, p-value = {p:.4f}, lift(B-A) = {lift:.2%}")

grp.reset_index().to_csv(BI_DIR / "groups.csv", index=False)

# --- Daily conversions by group (based on converted_at)
daily = (df.dropna(subset=["converted_at"])
           .assign(date=lambda d: d["converted_at"].dt.date)
           .groupby(["date","group"])
           .agg(conversions=("converted","sum"),
                revenue=("revenue","sum"))
           .reset_index())

# Add CR per day using total group visitors as denominator (context metric)
vis_map = grp["visitors"].to_dict()
daily["visitors"] = daily["group"].map(vis_map).astype(int)
daily["cr_day"] = daily["conversions"] / daily["visitors"]
daily.to_csv(BI_DIR / "daily.csv", index=False)

# --- Segment (state) by group
seg = (df.groupby(["segment","group"])
         .agg(visitors=("visitor_id","nunique"),
              conversions=("converted","sum"),
              revenue=("revenue","sum"))
         .assign(cr=lambda d: d["conversions"]/d["visitors"],
                 rpv=lambda d: d["revenue"]/d["visitors"])
         .reset_index())
seg.to_csv(BI_DIR / "segments.csv", index=False)

# --- Plot CR by group with error bars
plt.figure(figsize=(6,4))
order = ["A","B"] if set(grp.index) == {"A","B"} else list(grp.index)
plt.bar(order, grp.loc[order,"cr"].values)
# add CI whiskers
for i, g in enumerate(order):
    lo, hi = grp.loc[g,"cr_low"], grp.loc[g,"cr_high"]
    plt.plot([i, i], [lo, hi])
plt.title("Conversion Rate by Group (95% CI)")
plt.ylabel("Conversion Rate")
plt.xlabel("Group")
plt.tight_layout()
plt.savefig(PLOT_DIR / "cr_by_group.png", dpi=150)
print("📊 Saved outputs/plots/cr_by_group.png")

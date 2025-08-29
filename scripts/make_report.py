#!/usr/bin/env python3
"""
Assemble a concise stakeholder Markdown report from the A/B exports.

Inputs (from run_ab_test.py):
- outputs/bi_exports/groups.csv
- outputs/bi_exports/daily.csv
- outputs/bi_exports/segments.csv
- outputs/plots/cr_by_group.png (optional but recommended)

Output:
- REPORT.md at repo root

Notes:
- Requires 'tabulate' (via pandas.to_markdown)
- Designed for British English wording and recruiter-friendly framing
"""
from __future__ import annotations
from pathlib import Path
import pandas as pd
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]
BI = ROOT / "outputs" / "bi_exports"
PLOTS = ROOT / "outputs" / "plots"
REPORT = ROOT / "REPORT.md"

def pct(x: float) -> str:
    try:
        return f"{100.0 * float(x):.2f}%"
    except Exception:
        return "—"

def money(x: float, currency: str = "£") -> str:
    try:
        return f"{currency}{float(x):,.2f}"
    except Exception:
        return "—"

def load_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing expected file: {path}")
    return pd.read_csv(path)

def main() -> None:
    # Load exports
    groups = load_csv(BI / "groups.csv")
    daily = load_csv(BI / "daily.csv")
    segments = load_csv(BI / "segments.csv")

    # Basic safety/normalisation
    # Ensure expected columns exist
    needed_groups = {"group","visitors","conversions","cr","rpv"}
    missing = needed_groups - set(groups.columns.str.lower())
    if missing:
        # Try case-insensitive fix
        groups.columns = [c.lower() for c in groups.columns]
        missing = needed_groups - set(groups.columns)
        if missing:
            raise ValueError(f"groups.csv missing columns: {missing}")

    # Compute headline lift if both A and B exist
    headline = []
    lift_line = ""
    try:
        g = groups.set_index("group")
        if {"A", "B"}.issubset(set(g.index)):
            cr_a = float(g.loc["A","cr"])
            cr_b = float(g.loc["B","cr"])
            rpv_a = float(g.loc["A","rpv"])
            rpv_b = float(g.loc["B","rpv"])
            lift_cr = cr_b - cr_a
            lift_rpv = rpv_b - rpv_a
            lift_line = (
                f"- **Lift (B vs A)**: CR {pct(lift_cr)} | RPV {money(lift_rpv)}"
            )
            headline.extend([
                f"- **Group A**: Visitors {int(g.loc['A','visitors']):,}, "
                f"CR {pct(cr_a)}, RPV {money(rpv_a)}",
                f"- **Group B**: Visitors {int(g.loc['B','visitors']):,}, "
                f"CR {pct(cr_b)}, RPV {money(rpv_b)}",
            ])
        else:
            # Fallback summary
            groups_sorted = groups.sort_values("cr", ascending=False)
            best = groups_sorted.iloc[0]
            headline.append(
                f"- **Top group**: {best['group']} (CR {pct(best['cr'])}, "
                f"RPV {money(best['rpv'])})"
            )
    except Exception:
        pass

    # Prepare tables (pretty Markdown)
    groups_md = groups[["group","visitors","conversions","cr","rpv"]] \
        .rename(columns={
            "group":"Group",
            "visitors":"Visitors",
            "conversions":"Conversions",
            "cr":"CR",
            "rpv":"RPV"
        })
    # Format CR/RPV for display copy (keep raw values in CSVs)
    groups_md_disp = groups_md.copy()
    groups_md_disp["CR"] = groups_md_disp["CR"].map(pct)
    groups_md_disp["RPV"] = groups_md_disp["RPV"].map(money)

    # Daily table (keep lean)
    daily_md = daily.copy()
    # Try to show last 14 days only (if long range)
    if "date" in daily_md.columns and len(daily_md["date"].unique()) > 14:
        recent_dates = sorted(daily_md["date"].unique())[-14:]
        daily_md = daily_md[daily_md["date"].isin(recent_dates)]
    # Order columns if present
    for col in ("cr_day",):
        if col in daily_md.columns:
            daily_md[col] = daily_md[col].apply(pct)

    # Segment table (top 10 by visitors)
    seg_md = segments.copy()
    seg_md = seg_md.sort_values("visitors", ascending=False).head(10)
    seg_md["cr"] = seg_md["cr"].apply(pct)
    seg_md["rpv"] = seg_md["rpv"].apply(money)
    seg_md = seg_md.rename(columns={
        "segment":"Segment",
        "group":"Group",
        "visitors":"Visitors",
        "conversions":"Conversions",
        "cr":"CR",
        "rpv":"RPV",
        "revenue":"Revenue"
    })

    # Build Markdown
    lines = []
    lines.append("# A/B Test Results — Olist E-commerce\n")
    lines.append(f"_Generated: {dt.datetime.now().strftime('%Y-%m-%d %H:%M %Z')}_\n")
    lines.append("## Executive summary\n")
    if headline:
        lines.extend(headline)
    if lift_line:
        lines.append(lift_line)
    lines.append("\n---\n")

    lines.append("## Group summary\n")
    lines.append(groups_md_disp.to_markdown(index=False))
    lines.append("\n*CR = Conversion Rate; RPV = Revenue per Visitor.*\n")

    lines.append("\n## Recent daily performance (last ~14 days)\n")
    # Pick a compact subset of columns if present
    daily_show_cols = [c for c in ["date","group","conversions","revenue","cr_day"] if c in daily_md.columns]
    if daily_show_cols:
        lines.append(daily_md[daily_show_cols].to_markdown(index=False))
    else:
        lines.append("_Daily table unavailable due to missing columns._")

    lines.append("\n## Top segments by visitors\n")
    lines.append(seg_md.to_markdown(index=False))

    # Plot
    plot_path = PLOTS / "cr_by_group.png"
    if plot_path.exists():
        lines.append("\n## Visuals\n")
        lines.append(f"![Conversion Rate by Group]({plot_path.as_posix()})\n")

    # Actionable notes
    lines.append("\n## Recommendation\n")
    if lift_line:
        lines.append("- If Group B shows a statistically meaningful lift, consider rolling out the B variant, "
                     "or continue the test to strengthen significance if the p-value is marginal.")
    else:
        lines.append("- Continue to collect data until each group has sufficient visitors to evaluate CR with confidence intervals.")
    lines.append("- Review segment performance: if certain states respond better, tailor creative/targeting there.")
    lines.append("- Track RPV and not just CR to avoid optimising for low-value conversions.\n")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"📝 Wrote {REPORT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()

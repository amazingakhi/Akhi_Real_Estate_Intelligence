from __future__ import annotations

from pathlib import Path

import pandas as pd

from real_estate_analysis import build_summary, clean_real_estate_data, load_real_estate_data

ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "final_analysis_report.md"


def generate_analysis_report() -> str:
    df = clean_real_estate_data(load_real_estate_data())
    summary = build_summary(df)

    top_localities = (
        df.groupby("Locality", as_index=False)["Price"]
        .mean()
        .sort_values("Price", ascending=False)
        .head(5)
    )

    top_bhk = df["BHK_Count"].value_counts().sort_index().head(5)

    report_lines = [
        "# Gurugram Real Estate Analysis Report",
        "",
        "## Executive Summary",
        f"- Total properties analyzed: {summary['rows']}",
        f"- Average property price: ₹{summary['avg_price']:.2f}",
        f"- Average rate per sqft: ₹{summary['avg_rate_per_sqft']:.2f}",
        f"- Average property area: {summary['avg_area']:.2f} sqft",
        f"- Average BHK count: {summary['avg_bhk']:.2f}",
        f"- Unique localities covered: {summary['locality_count']}",
        "",
        "## Top Localities by Average Price",
        "",
    ]

    for _, row in top_localities.iterrows():
        report_lines.append(f"- {row['Locality']}: ₹{row['Price']:.2f} average price")

    report_lines.extend(["", "## BHK Distribution", ""])
    for bhk, count in top_bhk.items():
        report_lines.append(f"- {bhk} BHK: {count} properties")

    REPORT_PATH.parent.mkdir(exist_ok=True)
    REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
    return str(REPORT_PATH)


if __name__ == "__main__":
    print(generate_analysis_report())

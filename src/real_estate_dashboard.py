from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from real_estate_analysis import build_summary, clean_real_estate_data, load_real_estate_data

ROOT = Path(__file__).resolve().parents[1]
VISUALIZATIONS_DIR = ROOT / "visualizations"
VISUALIZATIONS_DIR.mkdir(exist_ok=True)


def top_localities_by_price(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    return (
        df.groupby("Locality", as_index=False)["Price"]
        .mean()
        .sort_values("Price", ascending=False)
        .head(n)
        .rename(columns={"Price": "Average Price"})
    )


def bhk_distribution(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df["BHK_Count"]
        .value_counts()
        .sort_index()
        .rename_axis("BHK_Count")
        .reset_index(name="Count")
    )


def create_dashboard() -> dict:
    df = clean_real_estate_data(load_real_estate_data())
    summary = build_summary(df)

    sns.set_theme(style="whitegrid")

    locality_df = top_localities_by_price(df, n=10)
    bhk_df = bhk_distribution(df)

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    sns.histplot(df["Price"], bins=30, kde=True, color="#4C72B0", ax=axes[0])
    axes[0].set_title("Property Price Distribution")
    axes[0].set_xlabel("Price (INR)")
    axes[0].set_ylabel("Frequency")

    sns.barplot(
        data=locality_df,
        x="Average Price",
        y="Locality",
        color="#2E8B57",
        ax=axes[1],
    )
    axes[1].set_title("Top 10 Localities by Average Price")
    axes[1].set_xlabel("Average Price (INR)")
    axes[1].set_ylabel("Locality")

    sns.barplot(
        data=bhk_df,
        x="BHK_Count",
        y="Count",
        color="#B24C63",
        ax=axes[2],
    )
    axes[2].set_title("BHK Distribution")
    axes[2].set_xlabel("BHK Count")
    axes[2].set_ylabel("Properties")

    fig.tight_layout()
    output_path = VISUALIZATIONS_DIR / "gurgaon_real_estate_dashboard.png"
    fig.savefig(output_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    summary_file = ROOT / "reports" / "summary_report.txt"
    summary_file.parent.mkdir(exist_ok=True)
    summary_file.write_text(
        "Gurugram Real Estate Summary\n"
        + "=" * 28 + "\n"
        + f"Rows: {summary['rows']}\n"
        + f"Columns: {summary['columns']}\n"
        + f"Average Price: ₹{summary['avg_price']:.2f}\n"
        + f"Average Rate per sqft: ₹{summary['avg_rate_per_sqft']:.2f}\n"
        + f"Average Area: {summary['avg_area']:.2f} sqft\n"
        + f"Average BHK: {summary['avg_bhk']:.2f}\n"
        + f"Locality Count: {summary['locality_count']}\n",
        encoding="utf-8",
    )

    return {
        "summary": summary,
        "dashboard_path": str(output_path),
        "summary_report": str(summary_file),
    }


if __name__ == "__main__":
    result = create_dashboard()
    print("Dashboard created successfully.")
    print("Dashboard image:", result["dashboard_path"])
    print("Summary report:", result["summary_report"])
    print("Summary:", result["summary"])

"""
Phase 5: 論文用Figure生成
Figure 1: Monthly suicide rate pattern (bar chart)
Figure 2: Forest plot of May IRR by subgroup (age + cause)
Figure 3: Era comparison of monthly IRR patterns
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / "output"

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def fig1_monthly_rate():
    """Figure 1: Monthly suicide rate pattern (all ages)."""
    with open(OUTPUT_DIR / "table1_descriptive.csv") as f:
        rows = [r for r in csv.DictReader(f) if r["age_group"] == "all"]

    months = list(range(1, 13))
    rates = [float(rows[m - 1]["mean_rate"]) for m in months]
    sds = [float(rows[m - 1]["sd_rate"]) for m in months]

    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#e74c3c" if m in (3, 5) else "#95a5a6" for m in months]
    colors[4] = "#c0392b"  # May darker red
    bars = ax.bar(months, rates, color=colors, edgecolor="white", linewidth=0.5)
    ax.errorbar(months, rates, yerr=sds, fmt="none", color="black",
                capsize=3, linewidth=0.8)

    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_LABELS, fontsize=10)
    ax.set_ylabel("Suicide rate per 100,000 person-years", fontsize=11)
    ax.set_xlabel("Month", fontsize=11)
    ax.set_title("Monthly Suicide Rate in Japan (2009\u20132024)", fontsize=13, pad=10)

    # Annotate May and March
    ax.annotate(f"Mar: {rates[2]:.1f}", xy=(3, rates[2] + sds[2]),
                xytext=(3, rates[2] + sds[2] + 1.5),
                ha="center", fontsize=9, fontweight="bold", color="#e74c3c")
    ax.annotate(f"May: {rates[4]:.1f}", xy=(5, rates[4] + sds[4]),
                xytext=(5, rates[4] + sds[4] + 1.5),
                ha="center", fontsize=9, fontweight="bold", color="#c0392b")
    ax.annotate(f"Dec: {rates[11]:.1f}", xy=(12, rates[11]),
                xytext=(12, rates[11] - 2.5),
                ha="center", fontsize=9, color="#7f8c8d")

    ax.set_ylim(0, max(rates) + max(sds) + 4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figure1_monthly_rate.png", dpi=300)
    plt.close(fig)
    print("[OK] figure1_monthly_rate.png")


def fig2_forest_plot():
    """Figure 2: Forest plot of May IRR by age group and cause."""
    # Load age subgroup data
    with open(OUTPUT_DIR / "table3_age_subgroup.csv") as f:
        age_data = list(csv.DictReader(f))
    # Load cause subgroup data
    with open(OUTPUT_DIR / "table4_cause_subgroup.csv") as f:
        cause_data = list(csv.DictReader(f))

    fig, ax = plt.subplots(figsize=(7, 8))

    labels = []
    irrs = []
    ci_lows = []
    ci_highs = []
    sigs = []

    # Section: Age Groups
    for r in age_data:
        labels.append(r["age_group"])
        irrs.append(float(r["may_irr"]))
        ci_lows.append(float(r["ci_low"]))
        ci_highs.append(float(r["ci_high"]))
        sigs.append(r["bh_significant"] == "True")

    # Separator
    labels.append("")
    irrs.append(np.nan)
    ci_lows.append(np.nan)
    ci_highs.append(np.nan)
    sigs.append(False)

    # Section: Cause
    for r in cause_data:
        labels.append(r["cause"])
        irrs.append(float(r["may_irr"]))
        ci_lows.append(float(r["ci_low"]))
        ci_highs.append(float(r["ci_high"]))
        sigs.append(r["bh_significant"] == "True")

    n = len(labels)
    y_pos = list(range(n - 1, -1, -1))

    for i in range(n):
        if labels[i] == "":
            continue
        irr = irrs[i]
        if np.isnan(irr):
            continue
        color = "#e74c3c" if sigs[i] else "#3498db"
        ax.plot([ci_lows[i], ci_highs[i]], [y_pos[i], y_pos[i]],
                color=color, linewidth=2, solid_capstyle="round")
        ax.plot(irr, y_pos[i], "o", color=color, markersize=7, zorder=5)
        # IRR label
        ax.text(ci_highs[i] + 0.02, y_pos[i], f"{irr:.3f}",
                va="center", fontsize=8, color=color)

    ax.axvline(x=1.0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)

    # Section headers
    age_top = y_pos[0] + 0.8
    ax.text(0.88, age_top, "By Age Group", fontweight="bold", fontsize=10)
    sep_idx = labels.index("")
    cause_top = y_pos[sep_idx + 1] + 0.8
    ax.text(0.88, cause_top, "By Cause of Death", fontweight="bold", fontsize=10)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=10)
    ax.set_xlabel("Incidence Rate Ratio (May vs December)", fontsize=11)
    ax.set_title("May IRR by Subgroup\n(Negative Binomial Regression, BH-corrected)",
                 fontsize=12, pad=10)
    ax.set_xlim(0.6, 2.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Legend
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='#e74c3c', label='Significant (BH)',
               markersize=7, linewidth=2),
        Line2D([0], [0], marker='o', color='#3498db', label='Non-significant',
               markersize=7, linewidth=2),
    ]
    ax.legend(handles=legend_elements, loc="lower right", fontsize=9)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figure2_forest_plot.png", dpi=300)
    plt.close(fig)
    print("[OK] figure2_forest_plot.png")


def fig3_era_comparison():
    """Figure 3: Era comparison of monthly IRR patterns."""
    with open(OUTPUT_DIR / "table5_sensitivity.csv") as f:
        rows = list(csv.DictReader(f))

    era_names = [
        "2009-2014 (post-crisis)",
        "2015-2019 (pre-COVID)",
        "2020-2024 (COVID+post)",
    ]
    era_irrs = []
    era_cis = []
    for name in era_names:
        for r in rows:
            if r["analysis"] == name:
                era_irrs.append(float(r["may_irr"]))
                era_cis.append((float(r["ci_low"]), float(r["ci_high"])))
                break

    fig, ax = plt.subplots(figsize=(7, 4))
    x = range(len(era_names))
    short_names = ["2009\u20132014", "2015\u20132019", "2020\u20132024"]

    for i in x:
        ci_lo, ci_hi = era_cis[i]
        ax.plot([i, i], [ci_lo, ci_hi], color="#e74c3c", linewidth=3,
                solid_capstyle="round")
        ax.plot(i, era_irrs[i], "o", color="#e74c3c", markersize=10, zorder=5)
        ax.text(i, ci_hi + 0.015, f"{era_irrs[i]:.3f}", ha="center",
                fontsize=10, fontweight="bold")

    ax.axhline(y=1.0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)

    # Full period reference
    full_irr = None
    for r in rows:
        if r["analysis"] == "Full (2009-2024)":
            full_irr = float(r["may_irr"])
            break
    if full_irr:
        ax.axhline(y=full_irr, color="#3498db", linestyle=":", linewidth=1.5,
                    alpha=0.7, label=f"Full period IRR={full_irr:.3f}")
        ax.legend(fontsize=9, loc="lower right")

    ax.set_xticks(list(x))
    ax.set_xticklabels(short_names, fontsize=11)
    ax.set_ylabel("May IRR (vs December)", fontsize=11)
    ax.set_title("Temporal Stability of May Suicide IRR Across Three Eras",
                 fontsize=12, pad=10)
    ax.set_ylim(1.0, 1.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "figure3_era_comparison.png", dpi=300)
    plt.close(fig)
    print("[OK] figure3_era_comparison.png")


if __name__ == "__main__":
    fig1_monthly_rate()
    fig2_forest_plot()
    fig3_era_comparison()
    print("\nAll manuscript figures generated.")

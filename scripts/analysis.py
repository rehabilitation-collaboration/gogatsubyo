"""
Phase 3: 主分析
5月に特異的な自殺増加があるかを統計的に検定する。

分析内容:
1. 月別ダミー負の二項回帰: 各月のIRR（Incidence Rate Ratio）と95%CI
2. 年齢層別サブグループ分析
3. 原因動機別分析
4. 5月 vs 春全体（3-5月）の分離検定
5. HAC標準誤差（Newey-West）
6. 多重比較補正（Benjamini-Hochberg）

出力:
- output/table2_monthly_irr.csv: 月別IRRテーブル
- output/table3_age_subgroup.csv: 年齢層別5月IRR
- output/table4_cause_subgroup.csv: 原因動機別5月IRR
- output/fig5_irr_forest.png: IRRフォレストプロット
"""

import csv
import warnings
from collections import defaultdict
from pathlib import Path

import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SUICIDE_CSV = DATA_DIR / "suicide_monthly_age_sex_cause.csv"
POP_CSV = DATA_DIR / "population" / "population_by_age_group_2009_2024.csv"

AGE_MAP = {
    "under_20": "0-19", "20-29": "20-29", "30-39": "30-39",
    "40-49": "40-49", "50-59": "50-59", "60-69": "60-69",
    "70-79": "70-79", "80_over": "80plus", "all": "total",
}

AGE_DISPLAY = {
    "all": "All ages", "under_20": "<20", "20-29": "20-29",
    "30-39": "30-39", "40-49": "40-49", "50-59": "50-59",
    "60-69": "60-69", "70-79": "70-79", "80_over": "80+",
}

CAUSE_LABELS = {
    "family": "Family", "health": "Health", "economic": "Economic",
    "work": "Work", "relationship": "Relationship", "school": "School",
}

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_data():
    with open(SUICIDE_CSV) as f:
        suicide = list(csv.DictReader(f))
    pop = {}
    with open(POP_CSV) as f:
        for r in csv.DictReader(f):
            pop[(int(r["year"]), r["age_group"])] = float(r["total_1000"]) * 1000
    return suicide, pop


def build_panel(rows, pop, age_filter="all", sex_filter="total"):
    """分析用パネルデータを構築: (year, month, count, population)"""
    panel = []
    for r in rows:
        if r["age_group"] != age_filter or r["sex"] != sex_filter:
            continue
        year = int(r["year"])
        month = int(r["month"])
        count = int(r["total_suicides"])
        pop_key = (year, AGE_MAP.get(age_filter, age_filter))
        population = pop.get(pop_key)
        if population and population > 0:
            panel.append({
                "year": year, "month": month,
                "count": count, "population": population,
            })
    return panel


def build_cause_panel(rows, cause, age_filter="all", sex_filter="total"):
    """原因動機別パネルデータ"""
    panel = []
    pop_data = {}
    with open(POP_CSV) as f:
        for r in csv.DictReader(f):
            pop_data[(int(r["year"]), r["age_group"])] = float(r["total_1000"]) * 1000

    for r in rows:
        if r["age_group"] != age_filter or r["sex"] != sex_filter:
            continue
        year = int(r["year"])
        month = int(r["month"])
        count = int(r[cause])
        pop_key = (year, AGE_MAP.get(age_filter, age_filter))
        population = pop_data.get(pop_key)
        if population and population > 0:
            panel.append({
                "year": year, "month": month,
                "count": count, "population": population,
            })
    return panel


# ============================================================
# Negative Binomial Regression (statsmodels)
# ============================================================

def fit_nb_regression(panel, reference_month=12):
    """
    負の二項回帰: count ~ month_dummies + year_trend + offset(log(pop/12))
    Returns: dict of {month: (IRR, CI_low, CI_high, p_value)}
    """
    try:
        import statsmodels.api as sm
    except ImportError:
        print("[WARN] statsmodels not available, using Poisson GLM fallback")
        return fit_poisson_fallback(panel, reference_month)

    n = len(panel)
    y = np.array([p["count"] for p in panel])
    offset = np.log(np.array([p["population"] / 12 for p in panel]))

    # Design matrix: 11 month dummies (ref=December) + year trend
    X = np.zeros((n, 12))  # 11 month dummies + 1 year trend
    for i, p in enumerate(panel):
        m = p["month"]
        if m != reference_month:
            col = m - 1 if m < reference_month else m - 2
            X[i, col] = 1
        X[i, 11] = p["year"] - 2009  # year trend (centered)

    X = sm.add_constant(X)

    try:
        model = sm.GLM(y, X, family=sm.families.NegativeBinomial(alpha=1.0),
                       offset=offset)
        result = model.fit(maxiter=100)

        # alpha推定付きNB
        from statsmodels.discrete.discrete_model import NegativeBinomial as NB2
        nb_model = NB2(y, X, offset=offset)
        nb_result = nb_model.fit(disp=0, maxiter=200)
        result = nb_result
    except Exception:
        # NB2が失敗したらPoisson
        model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
        result = model.fit()

    # IRR抽出
    irr_results = {}
    month_order = [m for m in range(1, 13) if m != reference_month]
    for idx, m in enumerate(month_order):
        coef = result.params[idx + 1]  # +1 for constant
        se = result.bse[idx + 1]
        irr = np.exp(coef)
        ci_low = np.exp(coef - 1.96 * se)
        ci_high = np.exp(coef + 1.96 * se)
        p_val = result.pvalues[idx + 1]
        irr_results[m] = (irr, ci_low, ci_high, p_val)

    # Reference month
    irr_results[reference_month] = (1.0, 1.0, 1.0, 1.0)

    return irr_results


def fit_nb_with_hac(panel, reference_month=12):
    """
    HAC標準誤差（Newey-West）付きの負の二項回帰
    """
    try:
        import statsmodels.api as sm
    except ImportError:
        return None

    n = len(panel)
    y = np.array([p["count"] for p in panel])
    offset = np.log(np.array([p["population"] / 12 for p in panel]))

    X = np.zeros((n, 12))
    for i, p in enumerate(panel):
        m = p["month"]
        if m != reference_month:
            col = m - 1 if m < reference_month else m - 2
            X[i, col] = 1
        X[i, 11] = p["year"] - 2009

    X = sm.add_constant(X)

    # Poisson with HAC (NB2 doesn't directly support HAC in statsmodels)
    model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
    result = model.fit(cov_type="HAC", cov_kwds={"maxlags": 12})

    irr_results = {}
    month_order = [m for m in range(1, 13) if m != reference_month]
    for idx, m in enumerate(month_order):
        coef = result.params[idx + 1]
        se = result.bse[idx + 1]
        irr = np.exp(coef)
        ci_low = np.exp(coef - 1.96 * se)
        ci_high = np.exp(coef + 1.96 * se)
        p_val = result.pvalues[idx + 1]
        irr_results[m] = (irr, ci_low, ci_high, p_val)
    irr_results[reference_month] = (1.0, 1.0, 1.0, 1.0)
    return irr_results


# ============================================================
# Multiple comparison correction
# ============================================================

def benjamini_hochberg(p_values: list[float], alpha=0.05) -> list[bool]:
    """BH法による多重比較補正。True=有意"""
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    significant = [False] * n
    for rank, (orig_idx, p) in enumerate(indexed, 1):
        threshold = alpha * rank / n
        if p <= threshold:
            significant[orig_idx] = True
        else:
            break
    return significant


# ============================================================
# Main analyses
# ============================================================

def analysis1_monthly_irr(rows, pop):
    """Analysis 1: 全年齢の月別IRR（12月=reference）"""
    print("\n=== Analysis 1: Monthly IRR (All Ages) ===")
    panel = build_panel(rows, pop, "all", "total")

    irr = fit_nb_regression(panel)
    irr_hac = fit_nb_with_hac(panel)

    # p値の多重比較補正（12月除く11ヶ月）
    p_vals = [irr[m][3] for m in range(1, 12)]
    bh_sig = benjamini_hochberg(p_vals)

    results = []
    print(f"{'Month':>5s} | {'IRR':>6s} | {'95% CI':>15s} | {'p':>8s} | {'BH sig':>6s} | {'HAC IRR':>8s}")
    print("-" * 70)
    for m in range(1, 13):
        irr_val, ci_lo, ci_hi, p = irr[m]
        sig = bh_sig[m - 1] if m < 12 else False
        hac_str = ""
        if irr_hac and m in irr_hac:
            hac_irr = irr_hac[m][0]
            hac_str = f"{hac_irr:.3f}"

        print(f"{MONTH_LABELS[m-1]:>5s} | {irr_val:.3f} | ({ci_lo:.3f}, {ci_hi:.3f}) | {p:.4f} | {'*' if sig else '':>6s} | {hac_str:>8s}")

        results.append({
            "month": m, "month_label": MONTH_LABELS[m - 1],
            "irr": f"{irr_val:.4f}", "ci_low": f"{ci_lo:.4f}", "ci_high": f"{ci_hi:.4f}",
            "p_value": f"{p:.6f}", "bh_significant": sig,
            "irr_hac": hac_str,
        })

    # CSV出力
    with open(OUTPUT_DIR / "table2_monthly_irr.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[OK] table2_monthly_irr.csv")

    return irr


def analysis2_age_subgroup(rows, pop):
    """Analysis 2: 年齢層別の5月IRR"""
    print("\n=== Analysis 2: May IRR by Age Group ===")
    age_groups = ["all", "under_20", "20-29", "30-39", "40-49",
                  "50-59", "60-69", "70-79", "80_over"]

    results = []
    p_vals = []

    print(f"{'Age':>8s} | {'May IRR':>8s} | {'95% CI':>15s} | {'p':>8s}")
    print("-" * 50)

    for age in age_groups:
        panel = build_panel(rows, pop, age, "total")
        if len(panel) < 24:
            continue

        irr = fit_nb_regression(panel)
        may_irr, ci_lo, ci_hi, p = irr[5]
        p_vals.append(p)

        print(f"{AGE_DISPLAY[age]:>8s} | {may_irr:.3f} | ({ci_lo:.3f}, {ci_hi:.3f}) | {p:.4f}")

        results.append({
            "age_group": AGE_DISPLAY[age],
            "may_irr": f"{may_irr:.4f}",
            "ci_low": f"{ci_lo:.4f}",
            "ci_high": f"{ci_hi:.4f}",
            "p_value": f"{p:.6f}",
        })

    # BH補正
    bh_sig = benjamini_hochberg(p_vals)
    for i, r in enumerate(results):
        r["bh_significant"] = bh_sig[i]

    with open(OUTPUT_DIR / "table3_age_subgroup.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[OK] table3_age_subgroup.csv")

    return results


def analysis3_cause_subgroup(rows, pop):
    """Analysis 3: 原因動機別の5月IRR"""
    print("\n=== Analysis 3: May IRR by Cause ===")
    causes = ["work", "school", "health", "family", "economic", "relationship"]

    results = []
    p_vals = []

    print(f"{'Cause':>15s} | {'May IRR':>8s} | {'95% CI':>15s} | {'p':>8s}")
    print("-" * 55)

    for cause in causes:
        panel = build_cause_panel(rows, cause, "all", "total")
        if len(panel) < 24:
            continue

        irr = fit_nb_regression(panel)
        may_irr, ci_lo, ci_hi, p = irr[5]
        p_vals.append(p)

        print(f"{CAUSE_LABELS[cause]:>15s} | {may_irr:.3f} | ({ci_lo:.3f}, {ci_hi:.3f}) | {p:.4f}")

        results.append({
            "cause": CAUSE_LABELS[cause],
            "may_irr": f"{may_irr:.4f}",
            "ci_low": f"{ci_lo:.4f}",
            "ci_high": f"{ci_hi:.4f}",
            "p_value": f"{p:.6f}",
        })

    bh_sig = benjamini_hochberg(p_vals)
    for i, r in enumerate(results):
        r["bh_significant"] = bh_sig[i]

    with open(OUTPUT_DIR / "table4_cause_subgroup.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)
    print(f"\n[OK] table4_cause_subgroup.csv")

    return results


def analysis4_may_vs_spring(rows, pop):
    """Analysis 4: 5月 vs 春全体（3-5月）。5月が春の中で特異的かを検定"""
    print("\n=== Analysis 4: May vs Spring (Mar-May) ===")
    panel = build_panel(rows, pop, "all", "total")

    # 春（3-5月）のみ抽出し、5月ダミーで検定
    spring = [p for p in panel if p["month"] in (3, 4, 5)]

    try:
        import statsmodels.api as sm
    except ImportError:
        print("[SKIP] statsmodels not available")
        return

    n = len(spring)
    y = np.array([p["count"] for p in spring])
    offset = np.log(np.array([p["population"] / 12 for p in spring]))

    # Design: may_dummy + apr_dummy + year_trend (ref=March)
    X = np.zeros((n, 3))
    for i, p in enumerate(spring):
        if p["month"] == 4:
            X[i, 0] = 1
        elif p["month"] == 5:
            X[i, 1] = 1
        X[i, 2] = p["year"] - 2009
    X = sm.add_constant(X)

    model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
    result = model.fit()

    may_coef = result.params[2]
    may_se = result.bse[2]
    may_irr = np.exp(may_coef)
    may_ci_lo = np.exp(may_coef - 1.96 * may_se)
    may_ci_hi = np.exp(may_coef + 1.96 * may_se)
    may_p = result.pvalues[2]

    apr_coef = result.params[1]
    apr_irr = np.exp(apr_coef)
    apr_p = result.pvalues[1]

    print(f"  May vs March:  IRR={may_irr:.3f} ({may_ci_lo:.3f}, {may_ci_hi:.3f}), p={may_p:.4f}")
    print(f"  April vs March: IRR={apr_irr:.3f}, p={apr_p:.4f}")
    print(f"  -> May {'IS' if may_p < 0.05 else 'is NOT'} significantly different from March")


def fig5_forest_plot(irr_all, age_results, cause_results):
    """Forest plot of May IRR across subgroups"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(8, 10))

    labels = []
    irrs = []
    ci_lows = []
    ci_highs = []

    # All ages
    may = irr_all[5]
    labels.append("All ages")
    irrs.append(may[0])
    ci_lows.append(may[1])
    ci_highs.append(may[2])

    # Separator
    labels.append("")
    irrs.append(np.nan)
    ci_lows.append(np.nan)
    ci_highs.append(np.nan)

    # Age groups
    for r in age_results:
        if r["age_group"] == "All ages":
            continue
        labels.append(f"  {r['age_group']}")
        irrs.append(float(r["may_irr"]))
        ci_lows.append(float(r["ci_low"]))
        ci_highs.append(float(r["ci_high"]))

    # Separator
    labels.append("")
    irrs.append(np.nan)
    ci_lows.append(np.nan)
    ci_highs.append(np.nan)

    # Causes
    for r in cause_results:
        labels.append(f"  {r['cause']}")
        irrs.append(float(r["may_irr"]))
        ci_lows.append(float(r["ci_low"]))
        ci_highs.append(float(r["ci_high"]))

    y_pos = list(range(len(labels)))
    y_pos.reverse()

    for i in range(len(labels)):
        if labels[i] == "":
            continue
        irr = irrs[i]
        if np.isnan(irr):
            continue
        ci_lo = ci_lows[i]
        ci_hi = ci_highs[i]
        color = "#e74c3c" if ci_lo > 1.0 else "#3498db"
        ax.plot([ci_lo, ci_hi], [y_pos[i], y_pos[i]], color=color, linewidth=2)
        ax.plot(irr, y_pos[i], "o", color=color, markersize=8)

    ax.axvline(x=1.0, color="black", linestyle="--", linewidth=0.5)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Incidence Rate Ratio (May vs December)")
    ax.set_title("May IRR: Forest Plot by Subgroup\n(Reference: December)")

    # Section headers
    ax.text(0.85, y_pos[0] + 0.5, "Overall", fontweight="bold", fontsize=10)
    ax.text(0.85, y_pos[2] + 0.5, "By Age Group", fontweight="bold", fontsize=10)
    sep2_idx = labels.index("", labels.index("") + 1)
    ax.text(0.85, y_pos[sep2_idx + 1] + 0.5, "By Cause", fontweight="bold", fontsize=10)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig5_irr_forest.png", dpi=150)
    plt.close(fig)
    print("\n[OK] fig5_irr_forest.png")


def main():
    warnings.filterwarnings("ignore")
    print("Loading data...")
    rows, pop = load_data()

    irr_all = analysis1_monthly_irr(rows, pop)
    age_results = analysis2_age_subgroup(rows, pop)
    cause_results = analysis3_cause_subgroup(rows, pop)
    analysis4_may_vs_spring(rows, pop)

    print("\nGenerating forest plot...")
    fig5_forest_plot(irr_all, age_results, cause_results)

    # Summary
    print("\n" + "=" * 60)
    print("ANALYSIS SUMMARY")
    print("=" * 60)
    may_all = irr_all[5]
    print(f"\nMay IRR (all ages, vs Dec): {may_all[0]:.3f} ({may_all[1]:.3f}-{may_all[2]:.3f})")
    print(f"  p = {may_all[3]:.6f}")

    print("\nMay is highest in March? Let's check:")
    for m in [3, 4, 5]:
        v = irr_all[m]
        print(f"  {MONTH_LABELS[m-1]}: IRR={v[0]:.3f} ({v[1]:.3f}-{v[2]:.3f}), p={v[3]:.6f}")


if __name__ == "__main__":
    main()

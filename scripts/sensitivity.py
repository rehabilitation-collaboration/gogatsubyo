"""
Phase 4: 感度分析

1. COVID-19期間（2020-2023）除外
2. 時代別比較（前期2009-2014 / 後期2015-2019 / COVID 2020-2024）
3. 5月 vs 他の春月（3月、4月）の年齢層別比較
4. 20-29歳の5月を勤務問題・学校問題別に深掘り

出力:
- output/table5_sensitivity.csv
- output/fig6_era_comparison.png
"""

import csv
import warnings
from pathlib import Path

import numpy as np

warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
SUICIDE_CSV = DATA_DIR / "suicide_monthly_age_sex_cause.csv"
POP_CSV = DATA_DIR / "population" / "population_by_age_group_2009_2024.csv"

AGE_MAP = {
    "under_20": "0-19", "20-29": "20-29", "30-39": "30-39",
    "40-49": "40-49", "50-59": "50-59", "60-69": "60-69",
    "70-79": "70-79", "80_over": "80plus", "all": "total",
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


def build_panel(rows, pop, age_filter="all", sex_filter="total",
                year_range=None, exclude_years=None):
    panel = []
    for r in rows:
        if r["age_group"] != age_filter or r["sex"] != sex_filter:
            continue
        year = int(r["year"])
        if year_range and not (year_range[0] <= year <= year_range[1]):
            continue
        if exclude_years and year in exclude_years:
            continue
        month = int(r["month"])
        count = int(r["total_suicides"])
        pop_key = (year, AGE_MAP.get(age_filter, age_filter))
        population = pop.get(pop_key)
        if population and population > 0:
            panel.append({"year": year, "month": month,
                          "count": count, "population": population})
    return panel


def build_cause_panel(rows, cause, age_filter="all", sex_filter="total",
                      year_range=None, exclude_years=None):
    panel = []
    pop_data = {}
    with open(POP_CSV) as f:
        for r in csv.DictReader(f):
            pop_data[(int(r["year"]), r["age_group"])] = float(r["total_1000"]) * 1000
    for r in rows:
        if r["age_group"] != age_filter or r["sex"] != sex_filter:
            continue
        year = int(r["year"])
        if year_range and not (year_range[0] <= year <= year_range[1]):
            continue
        if exclude_years and year in exclude_years:
            continue
        month = int(r["month"])
        count = int(r[cause])
        pop_key = (year, AGE_MAP.get(age_filter, age_filter))
        population = pop_data.get(pop_key)
        if population and population > 0:
            panel.append({"year": year, "month": month,
                          "count": count, "population": population})
    return panel


def fit_nb_may_irr(panel, reference_month=12):
    """May IRR only (simplified)"""
    import statsmodels.api as sm

    n = len(panel)
    if n < 24:
        return None

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

    try:
        from statsmodels.discrete.discrete_model import NegativeBinomial as NB2
        model = NB2(y, X, offset=offset)
        result = model.fit(disp=0, maxiter=200)
    except Exception:
        model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
        result = model.fit()

    # May is column index 4 (months 1-11 excl Dec, May=5 -> idx 4)
    may_idx = 5  # 1-indexed in params (0=const, 1=Jan, ..., 5=May)
    coef = result.params[may_idx]
    se = result.bse[may_idx]
    irr = np.exp(coef)
    ci_lo = np.exp(coef - 1.96 * se)
    ci_hi = np.exp(coef + 1.96 * se)
    p_val = result.pvalues[may_idx]
    return (irr, ci_lo, ci_hi, p_val)


def fit_all_month_irrs(panel, reference_month=12):
    """全月のIRRを返す"""
    import statsmodels.api as sm

    n = len(panel)
    if n < 24:
        return None

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

    try:
        from statsmodels.discrete.discrete_model import NegativeBinomial as NB2
        model = NB2(y, X, offset=offset)
        result = model.fit(disp=0, maxiter=200)
    except Exception:
        model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
        result = model.fit()

    irr_results = {}
    month_order = [m for m in range(1, 13) if m != reference_month]
    for idx, m in enumerate(month_order):
        coef = result.params[idx + 1]
        se = result.bse[idx + 1]
        irr_results[m] = (np.exp(coef), np.exp(coef - 1.96 * se),
                          np.exp(coef + 1.96 * se), result.pvalues[idx + 1])
    irr_results[reference_month] = (1.0, 1.0, 1.0, 1.0)
    return irr_results


def sensitivity1_covid_exclusion(rows, pop):
    """Sensitivity 1: COVID期間（2020-2023）を除外"""
    print("\n=== Sensitivity 1: COVID-19 Exclusion (2020-2023) ===")

    configs = [
        ("Full (2009-2024)", None, None),
        ("Excl COVID (2009-2019 + 2024)", None, {2020, 2021, 2022, 2023}),
        ("Pre-COVID only (2009-2019)", (2009, 2019), None),
    ]

    results = []
    for label, yr, excl in configs:
        panel = build_panel(rows, pop, "all", "total",
                            year_range=yr, exclude_years=excl)
        irr = fit_nb_may_irr(panel)
        if irr:
            print(f"  {label:35s}: IRR={irr[0]:.3f} ({irr[1]:.3f}-{irr[2]:.3f}), p={irr[3]:.4f}, n={len(panel)}")
            results.append({
                "analysis": label,
                "may_irr": f"{irr[0]:.4f}",
                "ci_low": f"{irr[1]:.4f}",
                "ci_high": f"{irr[2]:.4f}",
                "p_value": f"{irr[3]:.6f}",
                "n_observations": len(panel),
            })
    return results


def sensitivity2_era_comparison(rows, pop):
    """Sensitivity 2: 時代別比較"""
    print("\n=== Sensitivity 2: Era Comparison ===")

    eras = [
        ("2009-2014 (post-crisis)", (2009, 2014)),
        ("2015-2019 (pre-COVID)", (2015, 2019)),
        ("2020-2024 (COVID+post)", (2020, 2024)),
    ]

    results = []
    era_irrs = {}

    for label, yr in eras:
        panel = build_panel(rows, pop, "all", "total", year_range=yr)
        irr = fit_nb_may_irr(panel)
        all_irrs = fit_all_month_irrs(panel)
        if irr:
            print(f"  {label:30s}: May IRR={irr[0]:.3f} ({irr[1]:.3f}-{irr[2]:.3f}), p={irr[3]:.4f}")
            results.append({
                "analysis": label,
                "may_irr": f"{irr[0]:.4f}",
                "ci_low": f"{irr[1]:.4f}",
                "ci_high": f"{irr[2]:.4f}",
                "p_value": f"{irr[3]:.6f}",
                "n_observations": len(panel),
            })
            era_irrs[label] = all_irrs

    return results, era_irrs


def sensitivity3_young_cause_deep_dive(rows, pop):
    """Sensitivity 3: 20-29歳の5月を原因動機別に分析"""
    print("\n=== Sensitivity 3: Young Adults (20-29) Cause Breakdown ===")

    causes = ["work", "school", "health", "economic", "relationship", "family"]
    cause_labels = {
        "work": "Work", "school": "School", "health": "Health",
        "economic": "Economic", "relationship": "Relationship", "family": "Family",
    }

    results = []
    for cause in causes:
        panel = build_cause_panel(rows, cause, age_filter="20-29", sex_filter="total")
        irr = fit_nb_may_irr(panel)
        if irr:
            sig = "***" if irr[3] < 0.001 else "**" if irr[3] < 0.01 else "*" if irr[3] < 0.05 else ""
            print(f"  {cause_labels[cause]:>15s}: IRR={irr[0]:.3f} ({irr[1]:.3f}-{irr[2]:.3f}), p={irr[3]:.4f} {sig}")
            results.append({
                "analysis": f"20-29: {cause_labels[cause]}",
                "may_irr": f"{irr[0]:.4f}",
                "ci_low": f"{irr[1]:.4f}",
                "ci_high": f"{irr[2]:.4f}",
                "p_value": f"{irr[3]:.6f}",
                "n_observations": len(panel),
            })
    return results


def sensitivity4_may_rank_by_era(rows, pop):
    """Sensitivity 4: 各時代で5月のランキングが変わるか"""
    print("\n=== Sensitivity 4: May Rank by Era ===")

    eras = [
        ("2009-2014", (2009, 2014)),
        ("2015-2019", (2015, 2019)),
        ("2020-2024", (2020, 2024)),
    ]

    for label, yr in eras:
        panel = build_panel(rows, pop, "all", "total", year_range=yr)
        irrs = fit_all_month_irrs(panel)
        if irrs:
            ranked = sorted(irrs.items(), key=lambda x: -x[1][0])
            may_rank = next(i for i, (m, _) in enumerate(ranked, 1) if m == 5)
            top3 = [(MONTH_LABELS[m - 1], v[0]) for m, v in ranked[:3]]
            print(f"  {label}: May rank=#{may_rank}/12, Top 3: {top3}")


def fig6_era_comparison(era_irrs):
    """Figure 6: 時代別の月別IRRパターン比較"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(12, 6))
    months = list(range(1, 13))
    colors = ["#3498db", "#2ecc71", "#e74c3c"]
    markers = ["o", "s", "^"]

    for idx, (label, irrs) in enumerate(era_irrs.items()):
        if irrs is None:
            continue
        means = [irrs[m][0] for m in months]
        short_label = label.split("(")[0].strip()
        ax.plot(months, means, color=colors[idx], marker=markers[idx],
                label=short_label, linewidth=2, markersize=8)

    ax.axhline(y=1.0, color="gray", linestyle="--", alpha=0.3)
    ax.axvspan(4.5, 5.5, alpha=0.1, color="red", label="May")
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_LABELS)
    ax.set_ylabel("IRR (vs December)")
    ax.set_title("Monthly Suicide IRR by Era (Reference: December)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig6_era_comparison.png", dpi=150)
    plt.close(fig)
    print("\n[OK] fig6_era_comparison.png")


def main():
    print("Loading data...")
    rows, pop = load_data()

    all_results = []

    r1 = sensitivity1_covid_exclusion(rows, pop)
    all_results.extend(r1)

    r2, era_irrs = sensitivity2_era_comparison(rows, pop)
    all_results.extend(r2)

    r3 = sensitivity3_young_cause_deep_dive(rows, pop)
    all_results.extend(r3)

    sensitivity4_may_rank_by_era(rows, pop)

    # CSV出力
    with open(OUTPUT_DIR / "table5_sensitivity.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=all_results[0].keys())
        writer.writeheader()
        writer.writerows(all_results)
    print(f"\n[OK] table5_sensitivity.csv ({len(all_results)} rows)")

    fig6_era_comparison(era_irrs)

    # Summary
    print("\n" + "=" * 60)
    print("SENSITIVITY ANALYSIS SUMMARY")
    print("=" * 60)

    print("\nKey findings:")
    print("1. COVID exclusion: Does May IRR change?")
    for r in r1:
        print(f"   {r['analysis']}: IRR={r['may_irr']}")

    print("\n2. 20-29 cause breakdown:")
    for r in r3:
        sig = float(r['p_value']) < 0.05
        print(f"   {r['analysis']}: IRR={r['may_irr']} {'(sig)' if sig else '(ns)'}")


if __name__ == "__main__":
    main()

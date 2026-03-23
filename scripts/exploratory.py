"""
Phase 2: 記述統計・可視化
月別自殺パターンを可視化し、5月に特異的なピークがあるかを確認。

出力:
- output/fig1_monthly_pattern_all.png: 全年齢の月別パターン
- output/fig2_monthly_by_age.png: 年齢層別の月別パターン
- output/fig3_may_vs_others.png: 5月 vs 他の月の比較
- output/fig4_cause_by_month.png: 原因動機別の月別パターン
- output/table1_descriptive.csv: 記述統計テーブル
"""

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

SUICIDE_CSV = DATA_DIR / "suicide_monthly_age_sex_cause.csv"
POP_CSV = DATA_DIR / "population" / "population_by_age_group_2009_2024.csv"

# 年齢グループのマッピング（自殺データ → 人口データ）
AGE_MAP = {
    "under_20": "0-19",
    "20-29": "20-29",
    "30-39": "30-39",
    "40-49": "40-49",
    "50-59": "50-59",
    "60-69": "60-69",
    "70-79": "70-79",
    "80_over": "80plus",
    "all": "total",
}

MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

AGE_DISPLAY = {
    "under_20": "<20",
    "20-29": "20-29",
    "30-39": "30-39",
    "40-49": "40-49",
    "50-59": "50-59",
    "60-69": "60-69",
    "70-79": "70-79",
    "80_over": "80+",
}

CAUSE_LABELS = {
    "family": "Family",
    "health": "Health",
    "economic": "Economic",
    "work": "Work",
    "relationship": "Relationship",
    "school": "School",
}


def load_suicide_data() -> list[dict]:
    with open(SUICIDE_CSV) as f:
        return list(csv.DictReader(f))


def load_population() -> dict:
    """人口データを {(year, age_group): population} で返す"""
    pop = {}
    with open(POP_CSV) as f:
        for r in csv.DictReader(f):
            pop[(int(r["year"]), r["age_group"])] = float(r["total_1000"]) * 1000
    return pop


def compute_monthly_rates(rows, pop):
    """月別の自殺率（per 100,000）を計算"""
    # sex=total のみ使用（全年度で利用可能）
    monthly = defaultdict(lambda: defaultdict(list))

    for r in rows:
        if r["sex"] != "total":
            continue
        year = int(r["year"])
        month = int(r["month"])
        age = r["age_group"]
        count = int(r["total_suicides"])

        pop_key = (year, AGE_MAP.get(age, age))
        population = pop.get(pop_key, None)
        if population and population > 0:
            # 年率換算（月別データ → 年換算 per 100k）
            rate = (count / population) * 100_000 * 12
            monthly[age][month].append(rate)

    return monthly


def fig1_monthly_pattern_all(monthly_rates):
    """Figure 1: 全年齢の月別自殺率パターン"""
    fig, ax = plt.subplots(figsize=(10, 6))

    months = list(range(1, 13))
    rates = monthly_rates["all"]
    means = [np.mean(rates[m]) for m in months]
    sds = [np.std(rates[m]) for m in months]

    ax.bar(months, means, color=["#e74c3c" if m == 5 else "#3498db" for m in months],
           yerr=sds, capsize=4, alpha=0.8)
    ax.set_xticks(months)
    ax.set_xticklabels(MONTH_LABELS)
    ax.set_ylabel("Suicide rate (per 100,000 person-years)")
    ax.set_title("Monthly Suicide Rate in Japan (2009-2024, All Ages)")

    # 5月にアノテーション
    may_mean = means[4]
    annual_mean = np.mean(means)
    ax.axhline(y=annual_mean, color="gray", linestyle="--", alpha=0.5, label=f"Annual mean: {annual_mean:.1f}")
    ax.annotate(f"May: {may_mean:.1f}", xy=(5, may_mean), xytext=(6.5, may_mean + 2),
                arrowprops=dict(arrowstyle="->"), fontsize=10)
    ax.legend()

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig1_monthly_pattern_all.png", dpi=150)
    plt.close(fig)
    print(f"[OK] fig1_monthly_pattern_all.png")
    return means


def fig2_monthly_by_age(monthly_rates):
    """Figure 2: 年齢層別の月別パターン"""
    age_groups = ["under_20", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80_over"]
    fig, axes = plt.subplots(2, 4, figsize=(18, 8), sharey=False)

    months = list(range(1, 13))
    for idx, age in enumerate(age_groups):
        ax = axes[idx // 4][idx % 4]
        rates = monthly_rates.get(age, {})
        if not rates:
            ax.set_title(AGE_DISPLAY[age])
            continue

        means = [np.mean(rates[m]) if rates[m] else 0 for m in months]
        colors = ["#e74c3c" if m == 5 else "#3498db" for m in months]
        ax.bar(months, means, color=colors, alpha=0.8)
        ax.set_xticks(months)
        ax.set_xticklabels(MONTH_LABELS, fontsize=7, rotation=45)
        ax.set_title(AGE_DISPLAY[age], fontsize=12, fontweight="bold")

        # 5月の値をアノテーション
        if means[4] > 0:
            annual_mean = np.mean(means)
            pct = (means[4] / annual_mean - 1) * 100
            ax.set_xlabel(f"May: {pct:+.1f}% vs mean", fontsize=8)

    fig.suptitle("Monthly Suicide Rate by Age Group (2009-2024)", fontsize=14, fontweight="bold")
    fig.supylabel("Rate per 100,000 person-years", fontsize=11)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig2_monthly_by_age.png", dpi=150)
    plt.close(fig)
    print("[OK] fig2_monthly_by_age.png")


def fig3_may_vs_others(rows):
    """Figure 3: 5月 vs 年間平均の偏差（年齢層別）"""
    age_groups = ["under_20", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80_over"]

    # 月別合計（sex=total, 全年）
    monthly_counts = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if r["sex"] != "total" or r["age_group"] == "all":
            continue
        monthly_counts[r["age_group"]][int(r["month"])].append(int(r["total_suicides"]))

    fig, ax = plt.subplots(figsize=(10, 6))
    x = np.arange(len(age_groups))

    # 5月の平均 vs 年間月平均の比率
    ratios = []
    for age in age_groups:
        may_mean = np.mean(monthly_counts[age].get(5, [0]))
        annual_mean = np.mean([np.mean(monthly_counts[age].get(m, [0])) for m in range(1, 13)])
        ratio = (may_mean / annual_mean - 1) * 100 if annual_mean > 0 else 0
        ratios.append(ratio)

    colors = ["#e74c3c" if r > 0 else "#3498db" for r in ratios]
    ax.bar(x, ratios, color=colors, alpha=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels([AGE_DISPLAY[a] for a in age_groups])
    ax.set_ylabel("Deviation from annual monthly mean (%)")
    ax.set_title("May Suicide Count: Deviation from Annual Monthly Mean by Age Group")
    ax.axhline(y=0, color="black", linewidth=0.5)

    for i, r in enumerate(ratios):
        ax.text(i, r + (0.5 if r >= 0 else -1.5), f"{r:+.1f}%", ha="center", fontsize=9)

    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig3_may_vs_others.png", dpi=150)
    plt.close(fig)
    print("[OK] fig3_may_vs_others.png")
    return dict(zip(age_groups, ratios))


def fig4_cause_by_month(rows):
    """Figure 4: 原因動機別の月別パターン（五月病関連の動機に注目）"""
    causes = ["work", "school", "health", "family", "economic", "relationship"]
    monthly_cause = defaultdict(lambda: defaultdict(list))

    for r in rows:
        if r["sex"] != "total" or r["age_group"] != "all":
            continue
        month = int(r["month"])
        for cause in causes:
            monthly_cause[cause][month].append(int(r[cause]))

    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharey=False)
    months = list(range(1, 13))

    for idx, cause in enumerate(causes):
        ax = axes[idx // 3][idx % 3]
        means = [np.mean(monthly_cause[cause][m]) for m in months]
        colors = ["#e74c3c" if m == 5 else "#3498db" for m in months]
        ax.bar(months, means, color=colors, alpha=0.8)
        ax.set_xticks(months)
        ax.set_xticklabels(MONTH_LABELS, fontsize=7, rotation=45)
        ax.set_title(CAUSE_LABELS[cause], fontsize=12, fontweight="bold")

        # 5月の偏差
        annual_mean = np.mean(means)
        may_pct = (means[4] / annual_mean - 1) * 100 if annual_mean > 0 else 0
        ax.set_xlabel(f"May: {may_pct:+.1f}% vs mean", fontsize=8)

    fig.suptitle("Monthly Suicide by Cause (2009-2024, All Ages)", fontsize=14, fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "fig4_cause_by_month.png", dpi=150)
    plt.close(fig)
    print("[OK] fig4_cause_by_month.png")


def table1_descriptive(rows, pop):
    """Table 1: 記述統計テーブル"""
    # 月別 × 年齢層の平均自殺数・率
    output_rows = []
    age_groups = ["all", "under_20", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80_over"]

    for age in age_groups:
        for month in range(1, 13):
            counts = []
            rates = []
            for r in rows:
                if r["sex"] != "total" or r["age_group"] != age:
                    continue
                if int(r["month"]) != month:
                    continue
                year = int(r["year"])
                count = int(r["total_suicides"])
                counts.append(count)

                pop_key = (year, AGE_MAP.get(age, age))
                population = pop.get(pop_key)
                if population and population > 0:
                    rate = (count / population) * 100_000 * 12
                    rates.append(rate)

            if counts:
                output_rows.append({
                    "age_group": age,
                    "month": month,
                    "mean_count": f"{np.mean(counts):.1f}",
                    "sd_count": f"{np.std(counts):.1f}",
                    "min_count": min(counts),
                    "max_count": max(counts),
                    "mean_rate": f"{np.mean(rates):.2f}" if rates else "",
                    "sd_rate": f"{np.std(rates):.2f}" if rates else "",
                    "n_years": len(counts),
                })

    output_path = OUTPUT_DIR / "table1_descriptive.csv"
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_rows[0].keys())
        writer.writeheader()
        writer.writerows(output_rows)
    print(f"[OK] table1_descriptive.csv ({len(output_rows)} rows)")


def print_summary(rows, monthly_rates, may_deviations):
    """サマリーを表示"""
    print("\n" + "=" * 60)
    print("EXPLORATORY ANALYSIS SUMMARY")
    print("=" * 60)

    # 全年齢の月別ランキング
    all_rates = monthly_rates["all"]
    means = [(m, np.mean(all_rates[m])) for m in range(1, 13)]
    means.sort(key=lambda x: -x[1])

    print("\nMonthly suicide rate ranking (all ages, per 100k person-years):")
    for rank, (m, rate) in enumerate(means, 1):
        marker = " <-- MAY" if m == 5 else ""
        print(f"  {rank:2d}. {MONTH_LABELS[m-1]:>3s}: {rate:.1f}{marker}")

    print("\nMay deviation from annual mean by age group:")
    for age, dev in may_deviations.items():
        print(f"  {AGE_DISPLAY[age]:>5s}: {dev:+.1f}%")

    # 五月病仮説の暫定評価
    may_rank = next(i for i, (m, _) in enumerate(means, 1) if m == 5)
    print(f"\nMay is ranked #{may_rank}/12 in overall suicide rate.")

    young_dev = may_deviations.get("20-29", 0)
    print(f"May deviation for 20-29 age group (gogatsubyo target): {young_dev:+.1f}%")


def main():
    print("Loading data...")
    rows = load_suicide_data()
    pop = load_population()
    monthly_rates = compute_monthly_rates(rows, pop)

    print("\nGenerating figures...")
    means = fig1_monthly_pattern_all(monthly_rates)
    fig2_monthly_by_age(monthly_rates)
    may_deviations = fig3_may_vs_others(rows)
    fig4_cause_by_month(rows)
    table1_descriptive(rows, pop)

    print_summary(rows, monthly_rates, may_deviations)


if __name__ == "__main__":
    main()

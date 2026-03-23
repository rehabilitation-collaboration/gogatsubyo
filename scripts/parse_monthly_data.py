"""
厚労省月次ZIPから表3（原因動機×年齢階級×性別）を抽出し、統合CSVを生成。

フォーマットは2種類:
- 旧 (2009-2021): 15行×11列、性別なし（年齢×原因動機のみ）
- 新 (2022-2024): 36行×12列、性別あり（年齢×性別×原因動機）

入力: data/mhlw_monthly_zips/*.zip
出力: data/suicide_monthly_age_sex_cause.csv
"""

import csv
import re
import zipfile
import tempfile
from pathlib import Path

import xlrd

DATA_DIR = Path(__file__).parent.parent / "data"
ZIP_DIR = DATA_DIR / "mhlw_monthly_zips"
OUTPUT_CSV = DATA_DIR / "suicide_monthly_age_sex_cause.csv"

AGE_GROUPS = [
    "under_20", "20-29", "30-39", "40-49", "50-59", "60-69", "70-79", "80_over"
]
AGE_LABELS_JP = {
    "20歳未満": "under_20", "20": "20-29", "30": "30-39", "40": "40-49",
    "50": "50-59", "60": "60-69", "70": "70-79", "80": "80_over",
}
SEX_MAP = {"総数": "total", "男": "male", "女": "female"}

# 原因動機列名（出力CSV用）
CAUSE_COLUMNS = [
    "cause_total", "family", "health", "economic",
    "work", "relationship", "school", "other", "unknown"
]

# 旧フォーマットの原因動機列ヘッダー順（col 2-10）
# [総数, 家庭, 健康, 経済, 勤務, 男女問題/交際, 学校, その他, 不詳]

FIELDNAMES = [
    "year", "month", "age_group", "sex", "total_suicides"
] + CAUSE_COLUMNS


def find_a1_4_xls(zip_path: Path) -> str | None:
    """ZIP内からA1-4表のxlsファイル名を探す"""
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if "A1-4" in name and name.endswith(".xls"):
                return name
            if "A1_4" in name and name.endswith(".xls"):
                return name
    # 文字化け対策: サイズで推測
    with zipfile.ZipFile(zip_path) as zf:
        for name in zf.namelist():
            if not name.endswith(".xls"):
                continue
            info = zf.getinfo(name)
            if 80_000 < info.file_size < 200_000:
                return name
    return None


def find_sheet3(wb: xlrd.Book) -> xlrd.sheet.Sheet | None:
    """表3/a3シートを探す"""
    for i in range(wb.nsheets):
        sh = wb.sheet_by_index(i)
        name = sh.name.strip()
        if name in ("表3", "表３", "a3"):
            return sh
    # 内容で判定
    for i in range(wb.nsheets):
        sh = wb.sheet_by_index(i)
        if sh.nrows > 2:
            for r in range(min(3, sh.nrows)):
                row_text = " ".join(str(sh.cell_value(r, c)) for c in range(min(sh.ncols, 12)))
                if "原因" in row_text and "動機" in row_text:
                    return sh
    return None


def detect_format(sheet: xlrd.sheet.Sheet) -> str:
    """旧/新フォーマットを判定"""
    if sheet.nrows > 20 and sheet.ncols >= 12:
        return "new"  # 36行×12列 (2022-)
    return "old"  # 15行×11列 (2009-2021)


def parse_old_format(sheet: xlrd.sheet.Sheet, year: int, month: int) -> list[dict]:
    """旧フォーマット (2009-2021): 性別なし、年齢×原因動機のみ"""
    rows = []
    # データ行は通常 R3 (総数) から始まる
    for r in range(3, sheet.nrows):
        vals = [sheet.cell_value(r, c) for c in range(sheet.ncols)]
        age_str = str(vals[0]).strip()

        if not age_str:
            continue

        # 年齢グループの特定
        age_group = None
        if age_str == "総数":
            age_group = "all"
        else:
            for jp_label, en_label in AGE_LABELS_JP.items():
                if jp_label in age_str:
                    age_group = en_label
                    break

        if age_group is None:
            continue

        # 列: [年齢, 自殺者総数, 原因特定者総数, 家庭, 健康, 経済, 勤務, 男女/交際, 学校, その他, 不詳]
        total_suicides = _to_int(vals[1])
        cause_vals = [_to_int(vals[c]) for c in range(2, min(2 + len(CAUSE_COLUMNS), sheet.ncols))]
        while len(cause_vals) < len(CAUSE_COLUMNS):
            cause_vals.append(0)

        row = {
            "year": year,
            "month": month,
            "age_group": age_group,
            "sex": "total",  # 旧フォーマットは性別なし → totalのみ
            "total_suicides": total_suicides,
        }
        for i, col_name in enumerate(CAUSE_COLUMNS):
            row[col_name] = cause_vals[i]
        rows.append(row)

    return rows


def parse_new_format(sheet: xlrd.sheet.Sheet, year: int, month: int) -> list[dict]:
    """新フォーマット (2022-): 年齢×性別×原因動機"""
    rows = []
    current_age = None

    for r in range(4, sheet.nrows):
        vals = [sheet.cell_value(r, c) for c in range(sheet.ncols)]
        age_str = str(vals[0]).strip()
        sex_str = str(vals[1]).strip()

        # 年齢グループの更新
        if age_str:
            if age_str == "総数":
                current_age = "all"
            else:
                for jp_label, en_label in AGE_LABELS_JP.items():
                    if jp_label in age_str:
                        current_age = en_label
                        break

        if current_age is None:
            continue
        if sex_str not in SEX_MAP:
            continue

        sex = SEX_MAP[sex_str]
        total_suicides = _to_int(vals[2])

        # 列: [年齢, 性別, 自殺者総数, 原因特定者総数, 家庭, 健康, 経済, 勤務, 交際, 学校, その他, 不詳]
        cause_vals = [_to_int(vals[c]) for c in range(3, min(3 + len(CAUSE_COLUMNS), sheet.ncols))]
        while len(cause_vals) < len(CAUSE_COLUMNS):
            cause_vals.append(0)

        row = {
            "year": year,
            "month": month,
            "age_group": current_age,
            "sex": sex,
            "total_suicides": total_suicides,
        }
        for i, col_name in enumerate(CAUSE_COLUMNS):
            row[col_name] = cause_vals[i]
        rows.append(row)

    return rows


def _to_int(val) -> int:
    if isinstance(val, (int, float)):
        return int(val)
    s = str(val).strip().replace(",", "").replace("-", "0").replace("－", "0").replace("−", "0")
    if s in ("", "…", "‥"):
        return 0
    try:
        return int(float(s))
    except ValueError:
        return 0


def process_zip(zip_path: Path, year: int, month: int) -> list[dict]:
    """1つのZIPファイルを処理"""
    xls_name = find_a1_4_xls(zip_path)
    if xls_name is None:
        print(f"  [WARN] No A1-4 xls found in {zip_path.name}")
        return []

    with zipfile.ZipFile(zip_path) as zf:
        xls_data = zf.read(xls_name)

    with tempfile.NamedTemporaryFile(suffix=".xls", delete=False) as tmp:
        tmp.write(xls_data)
        tmp_path = tmp.name

    try:
        wb = xlrd.open_workbook(tmp_path)
        sheet = find_sheet3(wb)
        if sheet is None:
            print(f"  [WARN] No sheet3 found in {zip_path.name}")
            return []

        fmt = detect_format(sheet)
        if fmt == "old":
            rows = parse_old_format(sheet, year, month)
        else:
            rows = parse_new_format(sheet, year, month)

        return rows
    except Exception as e:
        print(f"  [ERROR] {zip_path.name}: {e}")
        return []
    finally:
        Path(tmp_path).unlink(missing_ok=True)


def main():
    all_rows = []
    zip_files = sorted(ZIP_DIR.glob("*.zip"))
    print(f"Processing {len(zip_files)} ZIP files...")

    success = 0
    fail = 0
    for zp in zip_files:
        m = re.match(r"(\d{4})-(\d{2})\.zip", zp.name)
        if not m:
            continue
        year, month = int(m.group(1)), int(m.group(2))
        rows = process_zip(zp, year, month)
        if rows:
            print(f"  [OK] {zp.name}: {len(rows)} rows")
            success += 1
        else:
            fail += 1
        all_rows.extend(rows)

    if not all_rows:
        print("[ERROR] No data extracted!")
        return

    # CSV出力
    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\n=== 完了 ===")
    print(f"Success: {success}, Failed: {fail}")
    print(f"Total rows: {len(all_rows)}")
    print(f"Output: {OUTPUT_CSV}")

    # サマリー
    years = sorted(set(r["year"] for r in all_rows))
    print(f"Years: {years[0]}-{years[-1]} ({len(years)} years)")
    for y in years:
        month_count = len(set(r["month"] for r in all_rows if r["year"] == y))
        row_count = len([r for r in all_rows if r["year"] == y])
        has_sex = any(r["sex"] != "total" for r in all_rows if r["year"] == y)
        fmt = "new (sex)" if has_sex else "old (no sex)"
        print(f"  {y}: {month_count} months, {row_count} rows [{fmt}]")


if __name__ == "__main__":
    main()

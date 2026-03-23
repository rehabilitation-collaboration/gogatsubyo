"""
統計局 人口推計 年齢各歳別人口データ ダウンロードスクリプト
対象: 2009-2024年 各年10月1日現在
"""

import urllib.request
import time
import os

SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

# 各年のダウンロードURL
# 2021-2024: stat.go.jp 直接
# 2009-2019: stat.go.jp 直接（xls形式）
# 2010, 2015: e-Stat経由
YEAR_URLS = {
    2024: ("https://www.stat.go.jp/data/jinsui/2024np/zuhyou/05k2024-1.xlsx", "pop2024.xlsx"),
    2023: ("https://www.stat.go.jp/data/jinsui/2023np/zuhyou/05k2023-1.xlsx", "pop2023.xlsx"),
    2022: ("https://www.stat.go.jp/data/jinsui/2022np/zuhyou/05k2022-1.xlsx", "pop2022.xlsx"),
    2021: ("https://www.stat.go.jp/data/jinsui/2021np/zuhyou/05k2021-1.xlsx", "pop2021.xlsx"),
    2019: ("https://www.stat.go.jp/data/jinsui/2019np/zuhyou/05k01-1.xlsx", "pop2019.xlsx"),
    2018: ("https://www.stat.go.jp/data/jinsui/2018np/zuhyou/05k30-1.xls", "pop2018.xls"),
    2017: ("https://www.stat.go.jp/data/jinsui/2017np/zuhyou/05k29-1.xls", "pop2017.xls"),
    2016: ("https://www.stat.go.jp/data/jinsui/2016np/zuhyou/05k28-1.xls", "pop2016.xls"),
    2015: ("https://www.e-stat.go.jp/stat-search/file-download?statInfId=000031495530&fileKind=0", "pop2015.xls"),
    2014: ("https://www.stat.go.jp/data/jinsui/2014np/zuhyou/05k26-1.xls", "pop2014.xls"),
    2013: ("https://www.stat.go.jp/data/jinsui/2013np/zuhyou/05k25-1.xls", "pop2013.xls"),
    2012: ("https://www.stat.go.jp/data/jinsui/2012np/zuhyou/05k24-1.xls", "pop2012.xls"),
    2011: ("https://www.stat.go.jp/data/jinsui/2011np/zuhyou/05k23-1.xls", "pop2011.xls"),
    2010: ("https://www.e-stat.go.jp/stat-search/file-download?statInfId=000012660847&fileKind=0", "pop2010.xls"),
    2009: ("https://www.stat.go.jp/data/jinsui/2009np/zuhyou/05k21-1.xls", "pop2009.xls"),
}

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.ms-excel,*/*",
}

success = []
failed = []

for year in sorted(YEAR_URLS.keys(), reverse=True):
    url, filename = YEAR_URLS[year]
    save_path = os.path.join(SAVE_DIR, filename)

    if os.path.exists(save_path) and os.path.getsize(save_path) > 5000:
        print(f"[SKIP] {year}: {filename} already exists ({os.path.getsize(save_path):,} bytes)")
        success.append(year)
        continue

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        with open(save_path, "wb") as f:
            f.write(data)
        size = len(data)
        print(f"[OK] {year}: {filename} ({size:,} bytes)")
        success.append(year)
    except Exception as e:
        print(f"[FAIL] {year}: {e}")
        failed.append((year, str(e)))

    time.sleep(1)

print(f"\n--- 結果 ---")
print(f"成功: {len(success)} 年 ({sorted(success)})")
if failed:
    print(f"失敗: {len(failed)} 年")
    for y, e in failed:
        print(f"  {y}: {e}")

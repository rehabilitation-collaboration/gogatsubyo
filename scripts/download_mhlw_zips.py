"""
厚労省「地域における自殺の基礎資料」月次ZIPを一括ダウンロード。
2段階スクレイピング: 年度一覧 → 各年度ページ → ZIPリンク抽出 → ダウンロード
"""

import re
import time
import urllib.request
import urllib.parse
from pathlib import Path
from html.parser import HTMLParser

BASE_URL = "https://www.mhlw.go.jp"
INDEX_URL = f"{BASE_URL}/stf/seisakunitsuite/bunya/0000140901.html"
DATA_DIR = Path(__file__).parent.parent / "data" / "mhlw_monthly_zips"

# 対象: 平成21年(2009) ～ 令和6年(2024)
TARGET_YEARS = {
    "h21": 2009, "h22": 2010, "h23": 2011, "h24": 2012,
    "h25": 2013, "h26": 2014, "h27": 2015, "h28": 2016,
    "h29": 2017, "h30": 2018,
    "r1": 2019, "r01": 2019,
    "r2": 2020, "r02": 2020,
    "r3": 2021, "r03": 2021,
    "r4": 2022, "r04": 2022,
    "r5": 2023, "r05": 2023,
    "r6": 2024, "r06": 2024,
}


class LinkExtractor(HTMLParser):
    """HTMLからリンクを抽出する"""
    def __init__(self):
        super().__init__()
        self.links = []
        self._current_href = None
        self._current_text = []
        self._in_a = False

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._in_a = True
            self._current_text = []
            for name, val in attrs:
                if name == "href":
                    self._current_href = val

    def handle_data(self, data):
        if self._in_a:
            self._current_text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._in_a:
            self._in_a = False
            text = "".join(self._current_text).strip()
            if self._current_href:
                self.links.append((self._current_href, text))
            self._current_href = None


def fetch_page(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def resolve_url(href: str) -> str:
    if href.startswith("http"):
        return href
    return BASE_URL + href


def get_year_page_urls() -> list[tuple[str, str]]:
    """年度一覧ページから各年度ページのURLを取得"""
    html = fetch_page(INDEX_URL)
    parser = LinkExtractor()
    parser.feed(html)

    year_pages = []
    for href, text in parser.links:
        # jisatsu_kiso_h21 ~ jisatsu_kiso_r6 のパターンにマッチ
        if "jisatsu_kiso_" in href or "jisatsu_year" in href:
            # 年度識別子を抽出
            m = re.search(r"jisatsu_kiso_([a-z]\d+)", href)
            if m:
                year_key = m.group(1).lower()
                if year_key in TARGET_YEARS:
                    url = resolve_url(href)
                    year_pages.append((url, year_key))
    return year_pages


def get_monthly_zip_urls(year_page_url: str, year_key: str) -> list[tuple[str, str]]:
    """年度ページから月次ZIPのURLを抽出"""
    html = fetch_page(year_page_url)
    parser = LinkExtractor()
    parser.feed(html)

    zips = []
    western_year = TARGET_YEARS[year_key]

    for href, text in parser.links:
        if not href.lower().endswith(".zip"):
            continue
        url = resolve_url(href)
        fname = href.split("/")[-1]

        # 月次ZIPかどうかを判定（確定値ZIP・年間集計は除外）
        # 月次: YYYYMM-CHIIKI, 連番ID等
        # 除外: KAKUTEI, 年間集計
        fname_lower = fname.lower()

        # 確定値ZIPは含める（年間集計の別名）
        if "kakutei" in fname_lower:
            # 確定値はスキップ（年間集計なので月次ではない）
            continue

        # 月を特定できるか試みる
        month = _extract_month(fname, text, western_year)
        if month:
            label = f"{western_year}-{month:02d}"
            zips.append((url, label))
        else:
            # 月が特定できないがZIPはある → テキストから推測
            month_from_text = _extract_month_from_text(text)
            if month_from_text:
                label = f"{western_year}-{month_from_text:02d}"
                zips.append((url, label))

    # 重複除去（同じ月に複数ZIPがある場合は最初のものを採用）
    seen = set()
    unique_zips = []
    for url, label in zips:
        if label not in seen:
            seen.add(label)
            unique_zips.append((url, label))

    return unique_zips


def _extract_month(fname: str, text: str, year: int) -> int | None:
    """ファイル名から月を抽出"""
    # パターン1: YYYYMM-CHIIKI (例: 200901-CHIIKI.ZIP)
    m = re.match(rf"{year}(\d{{2}})", fname)
    if m:
        month = int(m.group(1))
        if 1 <= month <= 12:
            return month

    # パターン2: テキストに「○月」
    return _extract_month_from_text(text)


def _extract_month_from_text(text: str) -> int | None:
    """リンクテキストから月を抽出"""
    m = re.search(r"(\d{1,2})月", text)
    if m:
        month = int(m.group(1))
        if 1 <= month <= 12:
            return month
    return None


def download_zip(url: str, dest: Path) -> bool:
    """ZIPをダウンロード"""
    if dest.exists():
        print(f"  [SKIP] {dest.name} already exists")
        return True
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (research)"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            dest.write_bytes(resp.read())
        print(f"  [OK] {dest.name} ({dest.stat().st_size / 1024:.0f} KB)")
        return True
    except Exception as e:
        print(f"  [FAIL] {dest.name}: {e}")
        return False


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("=== Step 1: 年度ページURL取得 ===")
    year_pages = get_year_page_urls()
    print(f"Found {len(year_pages)} year pages")
    for url, key in year_pages:
        print(f"  {key} -> {url}")

    print("\n=== Step 2: 月次ZIPリンク抽出 + ダウンロード ===")
    total_downloaded = 0
    total_failed = 0
    all_zips = []

    for year_url, year_key in sorted(year_pages, key=lambda x: TARGET_YEARS[x[1]]):
        western_year = TARGET_YEARS[year_key]
        print(f"\n--- {western_year} ({year_key}) ---")
        time.sleep(1)  # 礼儀正しくアクセス

        try:
            monthly_zips = get_monthly_zip_urls(year_url, year_key)
        except Exception as e:
            print(f"  [ERROR] Failed to scrape {year_url}: {e}")
            continue

        print(f"  Found {len(monthly_zips)} monthly ZIPs")

        for zip_url, label in sorted(monthly_zips, key=lambda x: x[1]):
            fname = f"{label}.zip"
            dest = DATA_DIR / fname
            time.sleep(0.5)  # サーバー負荷軽減

            ok = download_zip(zip_url, dest)
            if ok:
                total_downloaded += 1
                all_zips.append((label, str(dest)))
            else:
                total_failed += 1

    print(f"\n=== 結果 ===")
    print(f"Downloaded: {total_downloaded}")
    print(f"Failed: {total_failed}")

    # マニフェストファイル出力
    manifest_path = DATA_DIR / "manifest.txt"
    with open(manifest_path, "w") as f:
        for label, path in sorted(all_zips):
            f.write(f"{label}\t{path}\n")
    print(f"Manifest: {manifest_path}")


if __name__ == "__main__":
    main()

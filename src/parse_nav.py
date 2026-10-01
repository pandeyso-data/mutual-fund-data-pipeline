import sys
from pathlib import Path

import pandas as pd

RAW_DIR = Path("data/raw")
INTERIM_DIR = Path("data/interim")

COLUMNS = [
    "scheme_code",
    "isin_div_payout_or_growth",
    "isin_div_reinvestment",
    "scheme_name",
    "plan",
    "option",
    "nav",
    "nav_date",
]
CATEGORY_PREFIXES = ("Open Ended", "Close Ended", "Interval Fund")


def parse_nav_file(path):
    category = None
    fund_house = None
    fund_house_explicit = False  # True once a fund house line is seen under the current category
    rows = []

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("Scheme Code"):
                continue
            if line.count(";") == 7:
                source = "file" if fund_house_explicit else "carried_forward"
                rows.append(line.split(";") + [category, fund_house, source])
            elif line.startswith(CATEGORY_PREFIXES):
                category = line
                fund_house_explicit = False  # keep fund_house, but mark it as not re-stated
            else:
                fund_house = line
                fund_house_explicit = True

    return pd.DataFrame(
        rows, columns=COLUMNS + ["category", "fund_house", "fund_house_source"]
    )


if __name__ == "__main__":
    if len(sys.argv) > 1:
        raw_file = Path(sys.argv[1])
    else:
        raw_file = sorted(RAW_DIR.glob("NAVAll_*.txt"))[-1]  # latest download

    df = parse_nav_file(raw_file)

    INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    out_file = INTERIM_DIR / f"nav_flat_{raw_file.stem.split('_')[-1]}.csv"
    df.to_csv(out_file, index=False)

    print(f"Parsed {raw_file.name}")
    print(f"Rows: {len(df):,}")
    print(f"Rows missing category: {df['category'].isna().sum()}")
    print(f"Rows missing fund_house: {df['fund_house'].isna().sum()}")
    print(f"Distinct scheme codes: {df['scheme_code'].nunique():,}")
    print(f"Distinct fund houses: {df['fund_house'].nunique()}")
    print(f"Distinct categories: {df['category'].nunique()}")
    print(f"Saved to {out_file}")
    print()
    print("fund_house_source counts:")
    print(df["fund_house_source"].value_counts().to_string())
    print()
    print("Rows with carried-forward fund house:")
    cf = df[df["fund_house_source"] == "carried_forward"]
    print(
        cf.groupby(["fund_house", "scheme_name"])
        .size()
        .reset_index(name="rows")
        .to_string(max_colwidth=60)
    )
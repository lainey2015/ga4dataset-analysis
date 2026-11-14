import argparse
from pathlib import Path

import duckdb

from ga4case.path import COMPACT_DATA, RAW_DIR

parser = argparse.ArgumentParser()
parser.add_argument("--input", type=Path, help="path to the raw parquet file")

args = parser.parse_args()

if args.input:
    raw = args.input
else:
    found = list(RAW_DIR.glob("*.parquet"))
    if len(found) != 1:
        raise SystemExit(
            "Pass --input /path/to/file.parquet, or put one parquet file in data/raw_data/."
        )
    raw = found[0]
if not raw.exists():
    raise SystemExit(f"Raw parquet file {raw} does not exist.")

if COMPACT_DATA.exists():
    print(f"{COMPACT_DATA} already exists. No more to do.")
    raise SystemExit(0)

COMPACT_DATA.parent.mkdir(parents=True, exist_ok=True)
duckdb.sql(f"""
    copy (
        select * 
        from read_parquet('{raw.as_posix()}') 
        )
    to '{COMPACT_DATA.as_posix()}' 
    (format parquet, compression zstd,row_group_size 122880);
""")

print(f"Done! {COMPACT_DATA.name} created.")

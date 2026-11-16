from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data/raw_data"
COMPACT_DATA = ROOT / "data/processed_data/ga4_events_compact.parquet"
EVENTS_FLATTENED = ROOT / "data/processed_data/events_flattened.parquet"

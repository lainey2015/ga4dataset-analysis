# Data
Nothing is tracked by git except this README file.

- `raw_data/`: the original parquet file 1.3GB.
- `processed_data/ga4_events_compact.parquet`: by `python -m ga4case.prepare_data`.
- `processed_data/events_flattened.parquet`: one row one event, by `python -m ga4case.flatten_events`.

# Advantages of compacting
The original parquet file splits 4,295,584 rows into 33,627 chunk up to 128 rows. With 94 columns, there will be around 3.2M index entries and a query takes about 18s. 
The compact copy has the same rows in 35 chunks, so index is 1000 times smaller than the original file, answering the same query takes less than 0.1s.


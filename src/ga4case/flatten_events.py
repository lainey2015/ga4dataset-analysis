import duckdb
from ga4case.path import COMPACT_DATA, EVENTS_FLATTENED


# 1. If the input is missing, raise an error and exit the program
if not COMPACT_DATA.exists():
    raise SystemExit(
        f"Compact data file {COMPACT_DATA} does not exist. Run first: "
        "python -m ga4case.prepare_data --input /path/to/ga4_events.parquet"
    )
SRC = COMPACT_DATA.as_posix()
OUT = EVENTS_FLATTENED.as_posix()

# 2. Query: one row per event, with selected fields flattened and extracted from the nested structure
flattened_sql = f"""
    with src as(
        select *, map_from_entries(event_params) as params
        from read_parquet('{SRC}')
    )
    select
        user_pseudo_id,
        make_timestamp(event_timestamp) as event_timestamp,
        strptime(event_date, '%Y%m%d')::date as event_date,
        event_name,
        params['entrances'].int_value as entrances,
        params['ga_session_id'].int_value as ga_session_id,
        params['ga_session_number'].int_value as ga_session_number,
        params['page_location'].string_value as page_location,
        params['page_referrer'].string_value as page_referrer,
        params['page_title'].string_value as page_title,
        params['engagement_time_msec'].int_value as engagement_time_msec,
        coalesce(params['session_engaged'].string_value, cast(params['session_engaged'].int_value as varchar)) as session_engaged,
        device.category as device_category,
        device.operating_system as device_os,
        device.web_info.browser as device_browser,
        geo.country as geo_country,
        traffic_source.source as traffic_source,
        traffic_source.medium as traffic_medium,
        ecommerce.purchase_revenue_in_usd as purchase_revenue_in_usd,
        nullif(ecommerce.transaction_id, '(not set)') as transaction_id 
    from src
    """
# About transaction_id: '(not set)' is a placeholder for missing values in GA4,  we will replace it with NULL, otherwise when counting
# distinct transaction_id, it will be counted as a valid transaction_id.


# 3. Create the table

EVENTS_FLATTENED.parent.mkdir(parents=True, exist_ok=True)
duckdb.sql(f"copy ({flattened_sql}) to '{OUT}' (format parquet, compression zstd)")

# 4. Check rows
rows_in = duckdb.sql(f"select count(*) from read_parquet('{SRC}')").fetchall()[0][0]
rows_out = duckdb.sql(f"select count(*) from read_parquet('{OUT}')").fetchall()[0][0]
if rows_in != rows_out:
    raise SystemExit(
        f"Row check failed: {rows_in:,} rows in the source, {rows_out:,} in the flatten table"
    )
# 5. Report the results
print(f"Super! {EVENTS_FLATTENED.name} created with {rows_out:,} rows.")

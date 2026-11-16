import duckdb
from ga4case.path import EVENTS_FLATTENED, SESSIONS

if not EVENTS_FLATTENED.exists():
    raise SystemExit(
        f"Flat event file {EVENTS_FLATTENED} does not exist. Run first: "
        "python -m ga4case.flatten_events"
    )

SRC = EVENTS_FLATTENED.as_posix()
OUT = SESSIONS.as_posix()

session_sql = f"""
    with events as (
        select * from read_parquet('{SRC}')
    ),
   per_session as (
       select
         user_pseudo_id, ga_session_id,
         min(ga_session_number) as session_number,
         min(event_timestamp) as session_start,
         max(event_timestamp) as session_end,
         count(*) as n_events,
         count(distinct page_location) filter (where event_name = 'page_view') as distinct_pages,
         coalesce(sum(engagement_time_msec), 0) / 1000 as active_seconds,
         max((event_name = 'view_item')::int) as viewed_product,
         max((event_name = 'view_search_results')::int) as searched,
         max((event_name = 'begin_checkout')::int) as began_checkout,
         max((event_name = 'purchase')::int) as purchased,
         coalesce(max((page_title = 'Page Unavailable')::int), 0) as saw_error_page
    from events
    group by user_pseudo_id, ga_session_id
   ),
   landing as (
       select
            user_pseudo_id,
            ga_session_id,
            coalesce(page_title, '(no title)') as landing_page_title,
            page_location as landing_page_location
        from events
        where event_name = 'page_view'
        qualify row_number() over (
            partition by user_pseudo_id, ga_session_id
            order by coalesce(entrances, 0) desc, event_timestamp
        ) = 1
    )
    select
        per_session.*,
        coalesce(landing.landing_page_title, '(no page view)') as landing_page_title,
        landing.landing_page_location
    from per_session
    left join landing using (user_pseudo_id, ga_session_id)
"""

SESSIONS.parent.mkdir(parents=True, exist_ok=True)
duckdb.sql(f"copy ({session_sql}) to '{OUT}' (format parquet, compression zstd)")

checks = duckdb.sql(f"""
     select
        (select count(distinct(user_pseudo_id, ga_session_id)) from read_parquet('{SRC}')) as sessions_in_events,
        count(*) as rows_in_sessions,
        (select count(*)from read_parquet('{SRC}')) as events_in_events,
        sum(n_events) as events_in_sessions
        from read_parquet('{OUT}')                
        """).fetchall()[0]
sessions_in_events, rows_in_sessions, events_in_events, events_in_sessions = checks
if sessions_in_events != rows_in_sessions or events_in_events != events_in_sessions:
    raise SystemExit(f"Session check failure: {checks}")

print(
    f"Sessions table created with {rows_in_sessions:,} rows with {events_in_sessions:,} events."
)

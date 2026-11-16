import duckdb
from ga4case.path import SESSIONS, USERS

# If input missing, raise an error and exit
if not SESSIONS.exists():
    raise SystemExit(
        f"Sessions file {SESSIONS} does not exist. Run first: "
        "python -m ga4case.build_sessions"
    )

SRC = SESSIONS.as_posix()
OUT = USERS.as_posix()

# Query: one row per user
users_sql = f"""
    with ordered as (
        select
            *,
            row_number() over (
                partition by user_pseudo_id
                order by session_start
            ) as visit_order
        from read_parquet('{SRC}')
    ),
    first_visit as (
        select * from ordered where visit_order = 1
    ),
    later_visits as (
        select
            user_pseudo_id,
            count(*) as n_later_visits,
            min(session_start) as next_visit_start,
            min(session_start) filter (where landing_page_title <> '(no page view)') as next_visit_page_view_start,
            min(session_start) filter (where purchased = 1) as later_purchase_start
        from ordered
        where visit_order > 1
        group by user_pseudo_id
    )
    select
        first_visit.user_pseudo_id,
        first_visit.session_number as first_session_number,
        first_visit.session_start as first_visit_start,
        first_visit.session_end as first_visit_end,
        first_visit.landing_page_title,
        first_visit.n_events,
        first_visit.distinct_pages,
        first_visit.active_seconds,
        first_visit.viewed_product,
        first_visit.searched,
        first_visit.began_checkout,
        first_visit.purchased as purchased_in_first_visit,
        first_visit.saw_error_page,
        coalesce(later_visits.n_later_visits, 0) as n_later_visits,
        later_visits.next_visit_start,
        later_visits.next_visit_page_view_start,
        later_visits.later_purchase_start
    from first_visit
    left join later_visits using (user_pseudo_id)
"""

# Create the table
USERS.parent.mkdir(parents=True, exist_ok=True)
duckdb.sql(f"copy ({users_sql}) to '{OUT}' (format parquet, compression zstd)")

# Check whether all visitors are counted and only counted once
checks = duckdb.sql(f"""
    select
        (select count(distinct user_pseudo_id) from read_parquet ('{SRC}')) as users_in_sessions,
        count(*) as rows_in_users,
        (select count(*) from read_parquet('{SRC}')) as visits_in_sessions,
        sum(1+ n_later_visits)::bigint as visits_in_users
    from read_parquet('{OUT}')  
""").fetchall()[0]

users_in_sessions, rows_in_users, visits_in_sessions, visits_in_users = checks
if users_in_sessions != rows_in_users or visits_in_sessions != visits_in_users:
    raise SystemExit(f"Users check failure: {checks}")

# Report
print(f"Users table created: {rows_in_users:,} rows covers {visits_in_users:,} visits")

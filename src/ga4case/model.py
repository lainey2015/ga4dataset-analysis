import duckdb
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier

from ga4case.path import USERS

OUTCOMES = ["came_back", "purchase_later"]

TOP_LANDING_PAGES = [
    "Home",
    "Google Online Store",
    "Apparel | Google Merchandise Store",
    "YouTube | Shop by Brand | Google Merchandise Store",
    "Google Dino Game Tee",
]


def load_first_visits(start, end):
    """Return one row per user who started from 'start' to 'end' ('end' not included) and did not buy in the first visit.
    - Come back = a later revisit with a page view  within 7 days after the first visit.
    - Purchase later = a later visit with a purchase within 7 days after the first visit.
    - columns: the first visit measures and above two outcomes.
    """
    return duckdb.sql(f"""
        select
            first_visit_start,
            landing_page_title,
            distinct_pages,
            active_seconds,
            viewed_product,
            searched,
            began_checkout,
            saw_error_page,
            coalesce(next_visit_page_view_start <= first_visit_end + interval 7 day, false)::int as came_back,
            coalesce(later_purchase_start <= first_visit_end + interval 7 day, false)::int as purchase_later
        from read_parquet('{USERS.as_posix()}')
        where first_session_number = 1
            and purchased_in_first_visit = 0
            and first_visit_start >= timestamp '{start}'
            and first_visit_start < timestamp '{end}'
        order by user_pseudo_id  
""").df()


def generate_input(df):
    """Build model inputs which are extraced from the first visit.
    - distinct_pages and active_seconds used as log(1+x) to avoid long visit dominance.
    - landing pages were turned to yes or no column
    """
    X = pd.DataFrame(
        {
            "log_distinct_pages": np.log1p(df["distinct_pages"]),
            "log_active_seconds": np.log1p(df["active_seconds"]),
            "viewed_product": df["viewed_product"],
            "searched": df["searched"],
            "began_checkout": df["began_checkout"],
            "saw_error_page": df["saw_error_page"],
        }
    )
    for page in TOP_LANDING_PAGES:
        X["landing:" + page.split("|")[0].strip()] = (
            df["landing_page_title"] == page
        ).astype(int)
    return X


def rule_flag(df):
    """Rule used as baseline: viewed a product or began checkout --- true"""
    return ((df["viewed_product"] == 1) | (df["began_checkout"] == 1)).to_numpy()


def logistic_model(C=1.0):
    """On standardised inputs: C for regularisation"""
    return make_pipeline(StandardScaler(), LogisticRegression(C=C, max_iter=1000))


def xgboost_model(max_depth=3, n_estimators=300, learning_rate=0.05, seed=0):
    """Seed was used to fix the sampling of rows and columns"""
    return XGBClassifier(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=seed,
    )


def top_scored(score, n):
    """Flag visitors with the highest score"""
    flagged = np.zeros(len(score), dtype=bool)
    flagged[np.argsort(-score, kind="stable")[:n]] = True
    return flagged


def flag_result(y, flagged):
    """Outcome from flagged group"""
    return {
        "pct_average": 100 * y.mean(),
        "pct_flagged": 100 * flagged.mean(),
        "pct_outcome_among_flagged": 100 * y[flagged].mean(),
        "times_average": y[flagged].mean() / y.mean(),
        "cases_caught": int(y[flagged].sum()),
        "pct_of_cases_caught": 100 * y[flagged].sum() / y.sum(),
    }

# Case study provided by ATG  
Public dataset: three months of GA4 web events from November 2020 to January 2021 

**Main questions** 
- how visitors use the website
- what predictors link to the engagement revisit and purchase behaviour
- what product team could change

## Summary of results
- **Data can be trusted:** Analysis uses landing page, distinct pages, active time, viewed a product, searched, began checkout, saw error page, and five most common landing pages. channel, device, country and hour are not useful and page view counts differently from Dec 29th, and thus not used.
- **Visiting events** 60% of new users viewed one page, and only 0.08% of them bought later. 18.7% of new users viewed a product, but they account for 60.7% of later purchasers.
- **Prediction on 'come back' and 'later purchase'**: rule based on viewed a product or began checkout as the baseline flagged 18% of new users. Rule caught 71% of later purchasers while Logistic regression 82% on validating. Testing passed after running according to settings in `Predict_analysis_plan.md`.
    - Plan before test: `Predict_analysis_plan.md` was committed (`a7268ca`) before the January test (`e12a574`).
    - January testing result: flagged users purchased later showed 4.86 times as often as the average and flagged come_back showed 2.08 times as often as the average.
- **Predictive, not causal** results only showed who is likely to come back or purchase, but not the reason of their behaviours.

## Repository guide on notebooks
- 01_dataExp_QC: flat events table
- 02_Information_check: check the trustable fields and event
- 03_Session_checks: check session table and the change in page views from Dec 29th
- 04_User_check: check users table, define analysis cohort and two outcomes
- 05_First_visit_table: Depth of the first visit against two outcomes - come back and later purchase
- 06_Predict_analysis: rule, Logistic regression and XGBoost on train/validation data
- 07_January_test: one time test on January new users

## Setup
Requires Python 3.11
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run
The data is not included in repo. Run the following steps in order.
1. Rewrite a compacted copy: 
- `python -m ga4case.prepare_data --input /path/to/ga4_events.parquet`

- Reason for compacting data: referring `data/README.md`

2. Build the flatten events table: one row one event:
```
python -m ga4case.flatten_events
```

3. Build sessions table: one row per visit
```
python -m ga4case.build_sessions
```
4. Build users table: one row per user
```
python -m ga4case.build_users
```
5. Run 'analysis_notebooks' in the numbered order.
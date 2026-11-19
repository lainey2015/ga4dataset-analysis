# Case study  
Public dataset: three months of GA4 web events from November 2020 to January 2021 

**Main questions** 
- how visitors use the website
- what predictors link to the engagement revisit and purchase behaviour
- what product team could change

## Summary of results
- **Data can be trusted:** Analysis uses landing page, distinct pages, active time, viewed a product, searched, began checkout, saw error page, and five most common landing pages. channel, device, country and hour are not useful and page view counts differently from Dec 29th, and thus not used.
- **Visiting events:** 60% of new users viewed one page, and only 0.08% of them bought later. 18.7% of new users viewed a product, but they account for 60.7% of later purchasers.
- **Prediction on 'come back' and 'later purchase':** rule based on viewed a product or began checkout as the baseline flagged 18% of new users. Rule caught 71% of later purchasers while Logistic regression 82% on validating. Testing passed after running according to settings in `Predict_analysis_plan.md`.
    - Plan before test: `Predict_analysis_plan.md` was committed (`a7268ca`) before the January test (`e12a574`).
    - January testing result: flagged users purchased later showed 4.86 times as often as the average and flagged come_back showed 2.08 times as often as the average.
- **Predictive, not causal:** modeling results only showed who is likely to come back or purchase, but not the reason of their behaviours.
- **Error page: a sign, not a proven cause:** 1 of 5573 visits met an error had a purchase, while other visits have much higher purchase rate: 1.46% vs 0.02%.
    - Test_1 showed that among users who came back with no error page in the first visit: users who met an error in later visit is far lower than who did not met an error regarding to the purchase rate in the first visit (0.2% vs 2.32%).
    - Test_2 showed that in visits with no less than 4 pages viewed without an error page: the purchase from visitors who met an error page in another visit is far lower than that of visitors who did not met an error (1.06% vs 8.76%). And splitting of the met an error visits, it showed that purchase before or after the error met both showed very lower rate (0.67% and 1.50%), so this gap is not caused by error page.
    - Error met groups seldom buy but it did not prove that error page cost sales. More experiments are in need to test the effect.
- **What product team can change:** New users who land on Home viewed a product accounts for 26.1% while 11.3% of those who land on the entrance page 'Google Online Store'. This gap cannot be read as the effect of the page, because different users land on different pages. Thus, a test is needed.
    - Test designed: new users who land on the entrance page are randomly splitting into two groups 50% vs 50% and the treated group is sent to Home to measure how many viewed a product in the first visit. 3342 users per group for a 20% relative lift (5% significance, 80% power, two sided) for two full weeks.
    - Purchases would need 200 days as the main measure so it will be tracked to ensure not get worse.
    - 'Google Dino Game Tee' page increased sharply from 30 per day in November to 480 per day in mid of December and this is a point to check for more information before a test.

## Repository guide on notebooks
- 01_dataExp_QC: flat events table
- 02_Information_check: check the trustable fields and event
- 03_Session_checks: check session table and the change in page views from Dec 29th
- 04_User_check: check users table, define analysis cohort and two outcomes
- 05_First_visit_table: Depth of the first visit against two outcomes - come back and later purchase
- 06_Predict_analysis: rule, Logistic regression and XGBoost on train/validation data
- 07_January_test: one time test on January new users
- 08_Tests_error_pages: test whether error page cost sales
- 09_Potential_change: a test designed on landing pages of new users

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

6. Tested with a run from a fresh clone.

## Use of AI
AI assistance:
- Data understanding and preparation: Claude helped to explore GA4 structure and initial data quality checks.
- Analytical review: Claude and Codex assisted in challenging the analysis plan, identifying potential leakage and discussing results and experiment design.
- Code development: Claude assisted with Python and SQL code, debugging, and documentation revision.
- Presentation: Claude and Codex helped to structure findings and slides. Canva AI supported visual formatting.

I defined the key concepts used in analysis, selected the analytical questions and final approach, fixed pass marks, reviewed and ran the code, check the reported results, and interpreted the findings and limitations. 


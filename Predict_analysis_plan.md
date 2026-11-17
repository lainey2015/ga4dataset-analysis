# Analysis plan: prediction after the first visit

## Aim: 
- predict who comes back and who buy products within 7 days after a first visit.

## Data split:
- Model development dataset: new users from Nov 1st to Dec 24th who did not buy in the first visit.
- Test dataset: new users from Jan 1st to Jan 24th who did not buy in the first visit.
- Arrivals excluded from Dec 25th to Dec 31st: the 7 days follow up of users ends on Dec 31st.

## Input:
11 inputs, the first visit columns ( `generate_input` in `src/ga4case/model.py`):
- log of distinct pages, and log of active seconds
- viewed a product, searched, began checkout, saw error page: yes/no
- five most common landing pages: yes / no

## Outcome:
- Come back: a later revisit with a page view  within 7 days after the first visit.
- Purchase later: a later visit with a purchase within 7 days after the first visit.

## Models:
- Logistic Regression: with default setting (C = 1.0)
- Before the test, Logistic regression fitted on all data spanning Nov 1st to Dec 24th, and then apply to the test dataset.
- XGBoost: for comparison.

## Comparison:
- Baseline rule: flag a new user who viewed a product or began checkout.
- Model flags the same number of new users as in rule, choosing the highest score.
- Report share flagged, outcome, times the average, AUC

## Pass standard for testing: Logistic Regression with testing dataset
All three must hold:
- The flagged return at least two times as often as the average visitors.
- The flagged purchase later at least four times of the average visitors.
- Catch at least as many returners and later purchasers as the baseline rule.

## The test is run only once and nothing will be changed about the settings and data, and result is reported either pass or fail.
- About the testing dataset:
    - the number of new users, inputs and outcome rates of all three months in 04_User_check.ipynb.
    - no model fitted for January before, no any check of first visit behaviour against outcomes on data in January.
    - During planning, Claude used to check the recording change for all three months. One of its test scripts also printed a first-visit outcome table with January arrival mixed in. But it did not show me and not used.




# Analysis plan: prediction after the first visit

## Aim: 
- predict who comes back and who buy products within 7 days after a first visit.

## Data split:
- Model development dataset: new users from Nov 1st to Dec 24th who did not buy in the first visit.
- Test dataset: new users from Jan 1st to Jan 24th who did not buy in the first visit.
- Arrivals excluded fro Dec 25th to Dec 31st: the 7 days follow up of users ends on Dec 31st.

## Input:
- the first visit columns

## Outcome:
- Come back: a later revisit with a page view  within 7 days after the first visit.
- Purchase later: a later visit with a purchase within 7 days after the first visit.


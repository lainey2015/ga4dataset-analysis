# Case study provided by ATG  
Public dataset: three months of GA4 web events from November 2020 to January 2021 

**Main questions** 
- how visitors use the website
- what predictors link to the engagement revisit and purchase behaviour
- what product team could change

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

3. Build session table: one row per visit
```
python -m ga4case.build_sessions
```

4. Run 'analysis_notebooks' in the numbered order.
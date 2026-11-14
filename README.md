# Case study provided by ATG  
Public dataset: three months of GA4 web events

Analysis aims to be decided

# Setup
Python 3.11
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

# Prepare data
Write a compacted copy to `data/processed_data/`: 
`python -m ga4case.prepare_data --input /path/to/ga4_events.parquet`

Reason for compacting data: referring `data/README.md`



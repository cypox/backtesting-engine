# finance data gather

You need to replace the line:
dt_now = end_dt.tzinfo.localize(_datetime.datetime.utcnow())

by:
dt_now = pd.Timestamp.utcnow()

in:
env/lib/python3.10/site-packages/yfinance/base.py

line:
654

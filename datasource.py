import pandas as pd
import yfinance as yf


df = yf.download("MSFT", period="7d", interval="1m")
print(f"got {len(df)} entries")

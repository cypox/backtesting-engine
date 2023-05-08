import pandas as pd
from yahoo_fin import stock_info as si
import yfinance as yf
from tqdm import tqdm
import requests
from bs4 import BeautifulSoup
import pickle
import sys

sys.setrecursionlimit(20000) # for pickling


df1 = pd.DataFrame( si.tickers_sp500() )
df2 = pd.DataFrame( si.tickers_nasdaq() )
df3 = pd.DataFrame( si.tickers_dow() )
df4 = pd.DataFrame( si.tickers_other() )

sym1 = set( symbol for symbol in df1[0].values.tolist() )
sym2 = set( symbol for symbol in df2[0].values.tolist() )
sym3 = set( symbol for symbol in df3[0].values.tolist() )
sym4 = set( symbol for symbol in df4[0].values.tolist() )

symbols = set.union( sym1, sym2, sym3, sym4 )

my_list = ['W', 'R', 'P', 'Q']

del_set = set()
sav_set = set()

for symbol in symbols:
    if len( symbol ) > 4 and symbol[-1] in my_list:
        del_set.add( symbol )
    else:
        sav_set.add( symbol )

print( f'Removed {len( del_set )} unqualified stock symbols...' )
print( f'There are {len( sav_set )} qualified stock symbols...' )

for ticker in (pbar := tqdm(sav_set)):
    try:
        pbar.set_description(f"processing {ticker}")

        # get ticker history
        df = yf.download(ticker, period='7d', interval='1m', progress=False, show_errors=False)

        pickle.dump(df, open(f"findata/{ticker}-hist.pkl", "wb"))

        # get ticker finviz info
        url = "https://finviz.com/quote.ashx?t=" + ticker
        result = requests.get(url, headers={"user-agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"})
        soup = BeautifulSoup(result.text, features="lxml")
        finviz_data = {}
        key = ""
        attr = ""
        for p in soup.find_all("td"):
            if p.has_attr("class") and p["class"][0] == "snapshot-td2-cp":
                key = p.string
            elif p.has_attr("class") and p["class"][0] == "snapshot-td2":
                finviz_data[key] = p.string

        pickle.dump(finviz_data, open("findata/{ticker}-info.pkl", "wb"))

    except ValueError:
        pass

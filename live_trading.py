import time
import api_func
import requests
from datetime import datetime, timedelta, timezone
import uuid
import websocket
import json
import threading
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS

from api_func import get_positions

# Strategy parameters
z_window = 42
spread_window = 10
z_threshold = 1.14


def trade():
    access_token = api_func.authorize(api_func.get_token_from_txt_file())


    # api_func.start_order_book_ws(access_token, "SBER", depth=1)
    # api_func.start_order_book_ws(access_token, "SBERP", depth=1)

    while True:
        max_window = max(z_window, spread_window)
        now = datetime.now(timezone.utc).replace(second=0, microsecond=0)

        since_dt = now - timedelta(minutes=max_window + 1)
        since_dt = since_dt.replace(second=0, microsecond=0)

        since = since_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        sber_candles = api_func.get_last_candles(access_token, "SBER",since=since)
        sberp_candles = api_func.get_last_candles(access_token, "SBERP",since=since)

        sber = pd.DataFrame(sber_candles)[["close"]]
        sberp = pd.DataFrame(sberp_candles)[["close"]]

        y = sber['close']
        X = sm.add_constant(sberp['close'])
        rols = RollingOLS(y, X, window=spread_window)
        rres = rols.fit()

        a = rres.params['close'].iloc[-1]
        b = rres.params['const'].iloc[-1]

        spread = y - (a * sberp['close'] + b)

        spread_mean = spread.rolling(z_window).mean().iloc[-1]
        spread_std = spread.rolling(z_window).std().iloc[-1]

        z_score = (spread.iloc[-1] - spread_mean) / spread_std

        print(z_score)
        time.sleep(5)

while True:
    trade()
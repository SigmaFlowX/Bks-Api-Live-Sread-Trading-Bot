import time
import api_func
import requests
from datetime import datetime, timedelta, timezone
import uuid
import websocket
import json
import threading


# Strategy parameters
z_window = 42
spread_window = 10
z_threshold = 1.14


def trade():
    access_token = api_func.authorize(api_func.get_token_from_txt_file())

    api_func.start_last_candle_ws(access_token, "SBER")
    api_func.start_order_book_ws(access_token, "SBER")

    api_func.start_last_candle_ws(access_token, "SBERP")
    api_func.start_order_book_ws(access_token, "SBERP")

    while True:
        print(api_func.last_candles)
        print(api_func.order_books)

while True:
    try:
        trade()
    except:
        time.sleep(10)
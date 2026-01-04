import requests
from datetime import datetime, timedelta, timezone
import uuid

def get_token_from_txt_file():
    file = open("token.txt")
    token = file.read()
    return token

def authorize(refresh_token):
    url = "https://be.broker.ru/trade-api-keycloak/realms/tradeapi/protocol/openid-connect/token"

    payload = {
        "client_id": "trade-api-write",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        tokens = response.json()
        token = tokens["access_token"]
        return token
    else:
        print("Error while trying  to authorize:", response.status_code, response.text)
        return None

def get_current_price(token, ticker, class_code = "TQBR"):
    url = "https://be.broker.ru/trade-api-market-data-connector/api/v1/candles-chart"

    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=40)
    start_date_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    payload = {
        "classCode": class_code,
        "ticker": ticker,
        "startDate": start_date_str,
        "endDate": end_date_str,
        "timeFrame": "MN"
    }

    response = requests.get(url, headers=headers, params=payload)

    if response.status_code == 200:
        data = response.json()
        candles = data.get("bars", [])
        if candles:
            return candles[0]['close']
        else:
            print("No candles obtained")
            return None
    else:
        print("Failed to get current price:", response.status_code, response.text)
        return None

def place_order(token, ticker, quantity, direction,  order_type, class_code="TQBR", price=None):  # 1 - buy, 2 - sell, 1 - market, 2 - limit

    url = "https://be.broker.ru/trade-api-bff-operations/api/v1/orders"

    client_order_id = str(uuid.uuid4())

    headers = {
      "Content-Type": "application/json",
      "Accept": "application/json",
      "Authorization": f"Bearer {token}"
    }

    payload = {
        "clientOrderId": client_order_id,
        "side": str(direction),
        "orderType": str(order_type),
        "orderQuantity": quantity,
        "ticker": ticker,
        "classCode": class_code,
    }
    if order_type == 2:
        payload["price"] = float(price)

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        print("Order placed")
        return client_order_id
    else:
        print("Failed to place the order:", response.status_code, response.text)
        return None

def get_order_status(token, id):
    url = f"https://be.broker.ru/trade-api-bff-operations/api/v1/orders/{id}"

    payload = {
        "originalClientOrderId": id
    }

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    return response.json()['data']['orderStatus']

# Состояние заявки:
# 0 — Новая
# 1 — Частично исполнена
# 2 — Полностью исполнена
# 4 — Отменена
# 5 — Заменена
# 6 — Отменяется (в процессе отмены)
# 8 — Отклонена
# 9 — Заменяется (например, если вы изменяли заявку)
# 10 — Ожидает подтверждения новой заявки

if __name__ == "__main__":
    access_token = authorize(get_token_from_txt_file())
    order = place_order(access_token, "SBER", 1, 1, 2, price = 100)
    print(get_order_status(access_token, order))
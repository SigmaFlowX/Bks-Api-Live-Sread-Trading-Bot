import requests
from datetime import datetime, timedelta, timezone

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

def get_current_price(ticker, token,class_code = "TQBR"):
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


if __name__ == "__main__":
    access_token = authorize(get_token_from_txt_file())
    print(get_current_price("SBER", access_token))
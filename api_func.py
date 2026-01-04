import requests

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
        return 0


if __name__ == "__main__":
    access_token = authorize(get_token_from_txt_file())

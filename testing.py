import requests
def getToken():
    url = "https://identitysso.betfair.com.au/api/login"

    headers = {
        "Accept": "application/json",
        "X-Application": "5fLJufLlOuWDWpM7",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {
        "username": "lucas.peiyangj@gmail.com",
        "password": "cycsu4-wetzug-xodzeF"
    }

    response = requests.post(url, headers=headers, data=body)

    response_data = response.json()

    if response_data.get("status") == "SUCCESS":
        print("Login Successful!")
        token = response_data.get("token")
        print("Your Token:", token)
        return token
    else:
        print("Login Failed.")
        print("Status:", response_data.get("status"))
        print("Error Reason:", response_data.get("error"))

def listEventTypes():
    session_token = getToken();
    app_key = "5fLJufLlOuWDWpM7"

    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    headers = {
        "X-Authentication": session_token,
        "X-Application": app_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listEventTypes",
        "id": 1,
        "params": {
            "filter": {
                
            }
        }
    }

    response = requests.post(url, headers=headers, json=body)

    # print(response.json())

def listMarketCatalogue():
    session = getToken()
    app_key = "5fLJufLlOuWDWpM7" 

    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    headers = {
        "X-Authentication": session,
        "X-Application": app_key,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "id": 1,
        "params": {
            "filter": {
                "eventTypeIds": ["1"],
                "marketCountries": ["AU"],
                "marketTypeCodes": ["MATCH_ODDS"],
                "marketStartTime": {
                    "from": "2026-02-22T00:00:00Z"
                }
            },
            "maxResults": "20",
            "marketProjection": [
                "EVENT",
                "RUNNER_DESCRIPTION",
                "MARKET_START_TIME"
            ],
        },
        "id": 1
    }
    {home, away, startTime} = getMatch()
    
    response = requests.post(url, headers=headers, json=body)
    data = response.json()
    result = {
        "marketId": data["result"][0]["marketId"],
        "selectionId": data["result"][0]["runners"][0]["selectionId"]
    }
    return result

def getMatch():
    result = {
        "home": "Central Coast Mariners",
        "away": "Western Sydney Wanderers",
        "startTime": "2026-02-22T06:00:00.000Z"
    }
    return result

listEventTypes()
listMarketCatalogue()

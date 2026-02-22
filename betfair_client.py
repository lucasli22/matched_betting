import requests


def getMatch():
    # stub for now
    result = {
        "home": "Central Coast Mariners",
        "away": "Western Sydney Wanderers",
        "startTime": "2026-02-22T06:00:00.000Z",
    }
    return result


def getToken():
    url = "https://identitysso.betfair.com.au/api/login"

    headers = {
        "Accept": "application/json",
        "X-Application": "5fLJufLlOuWDWpM7",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    body = {"username": "lucas.peiyangj@gmail.com", "password": "cycsu4-wetzug-xodzeF"}

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
    session_token = getToken()
    app_key = "5fLJufLlOuWDWpM7"

    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    headers = {
        "X-Authentication": session_token,
        "X-Application": app_key,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listEventTypes",
        "id": 1,
        "params": {"filter": {}},
    }

    response = requests.post(url, headers=headers, json=body)

    return response.json()


def listMarketCatalogue():
    session = getToken()
    app_key = "5fLJufLlOuWDWpM7"

    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    headers = {
        "X-Authentication": session,
        "X-Application": app_key,
        "Content-Type": "application/x-www-form-urlencoded",
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
                "marketStartTime": {"from": "2026-02-22T00:00:00Z"},
            },
            "maxResults": "20",
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"],
        },
        "id": 1,
    }

    response = requests.post(url, headers=headers, json=body)
    return response.json()["result"]

def normalise(name):
    return name.lower().replace("fc", "").replace(".", "").strip()

def findMarket(match, catalogue):
    home = match["home"]
    away = match["away"]
    matchStartTime = match["startTime"]
    for market in catalogue:
        event = market["event"]
        marketStartTime = market["marketStartTime"]
        if matchStartTime != marketStartTime:
            continue
        runners = market["runners"]
        runnerNames = [normalise(runner["runnerName"]) for runner in runners]
        if normalise(home) in runnerNames and normalise(away) in runnerNames:
            return market
    return None

def getSelectionId(market, teamToLay):
    runners = market["runners"]
    for runner in runners:
        if normalise(runner["runnerName"]) == normalise(teamToLay):
            return runner["selectionId"]
    return None

eventTypes = listEventTypes()
match = getMatch()
catalogue = listMarketCatalogue()
market = findMarket(match, catalogue)
if market:
    teamToLay = match["home"]
    selectionId = getSelectionId(market, teamToLay)
    if selectionId:
        print(f"Safe to lay {teamToLay}!")
        print(f"Market id: {market["marketId"]}")
        print(f"Selection id: {selectionId}")
    else:
        print(f"Could not find {teamToLay} in Betfair :(")
else:
    print("No matching market found for this match :(")



import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
load_dotenv()

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
app_key = os.getenv("APP_KEY")


def getMatch(time):
    # stub for now
    auTime = time.replace(tzinfo=ZoneInfo("Australia/Sydney"))
    utcTime = auTime.astimezone(ZoneInfo("UTC"))
    isoString = utcTime.isoformat()
    result = {
        "home": "Liverpool",
        "away": "West Ham",
        "startTime": isoString,
    }
    return result


def getToken():
    url = "https://identitysso.betfair.com.au/api/login"

    headers = {
        "Accept": "application/json",
        "X-Application": "5fLJufLlOuWDWpM7",
        "Content-Type": "application/x-www-form-urlencoded",
    }

    body = {"username": f"{username}", "password": f"{password}"}

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

    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    headers = {
        "X-Authentication": session,
        "X-Application": app_key,
        "Content-Type": "application/json",
    }

    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds": ["1"],
                "marketCountries": ["GB"],
                "marketTypeCodes": ["MATCH_ODDS"],
                "marketStartTime": {"from": "2026-02-28T00:00:00Z"},
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

def parse_betfair_time(timeStr):
    return datetime.fromisoformat(timeStr.replace("Z", "+00:00"))

def findMarket(match, catalogue):
    home = match["home"]
    away = match["away"]
    matchStartTime = match["startTime"]
    for market in catalogue:
        marketStartTime = market["marketStartTime"]
        delta = abs(
        parse_betfair_time(matchStartTime) -
        parse_betfair_time(marketStartTime)
        )   

        if delta.total_seconds() > 60:
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

def listMarketBook(marketId, selectionId):
    session = getToken()

    url = "https://api.betfair.com/exchange/betting/json-rpc/v1"

    headers = {
        "X-Authentication": session,
        "X-Application": app_key,
        "Content-Type": "application/json",
    }

    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketBook",
        "params": {
            "marketIds": [marketId],
            "priceProjection": {
                "priceData": ["EX_BEST_OFFERS"]
            },
        },
        "id": 1,
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()["result"] 
    market = data[0]
    for runner in market["runners"]:
        if runner["selectionId"] == selectionId:
            if runner.get("ex", {}).get("availableToLay"):
                return runner["ex"]["availableToLay"][0]["price"]
    return None    


eventTypes = listEventTypes()
startTime = datetime(year=2026, month=3, day=1, hour=2, minute=0)
match = getMatch(startTime)
catalogue = listMarketCatalogue()
market = findMarket(match, catalogue)
if market:
    teamToLay = match["home"]
    selectionId = getSelectionId(market, teamToLay)
    if selectionId:
        print(f"Safe to lay {teamToLay}!")
        print(f"Market id: {market["marketId"]}")
        print(f"Selection id: {selectionId}")
        bestLayPrice = listMarketBook(market["marketId"], selectionId)
        if bestLayPrice:
            print(f"The best lay price right now is {bestLayPrice}!")
        else:
            print("There are no prices for this match :(")
    else:
        print(f"Could not find {teamToLay} in Betfair :(")
else:
    print("No matching market found for this match :(")



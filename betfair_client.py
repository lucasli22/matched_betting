import requests
import os
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
APP_KEY = os.getenv("APP_KEY")

BETFAIR_API_URL = "https://api.betfair.com/exchange/betting/json-rpc/v1"
BETFAIR_LOGIN_URL = "https://identitysso.betfair.com.au/api/login"
BETFAIR_APP_KEY = "5fLJufLlOuWDWpM7"


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

# Log in to Betfair and return a session token.
def get_token() -> str:
    headers = {
        "Accept": "application/json",
        "X-Application": BETFAIR_APP_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    response = requests.post(
        BETFAIR_LOGIN_URL,
        headers=headers,
        data={"username": USERNAME, "password": PASSWORD},
    )
    data = response.json()

    if data.get("status") != "SUCCESS":
        raise RuntimeError(f"Betfair login failed: {data.get('error')}")

    return data["token"]


# ---------------------------------------------------------------------------
# Betfair API calls
# ---------------------------------------------------------------------------

# Return all event types available on Betfair (e.g. Soccer, Tennis).
def list_event_types() -> list[dict]:
    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listEventTypes",
        "id": 1,
        "params": {"filter": {}},
    }
    return _post(body)


# Fetch upcoming Match Odds markets from Betfair starting from the match date.
# Returns a list of market dicts, each containing runners and event info.
def list_market_catalogue(match: dict) -> list[dict]:
    match_time = parse_betfair_time(match["startTime"])
    from_time = match_time.replace(hour=0, minute=0, second=0).strftime("%Y-%m-%dT%H:%M:%SZ")

    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketCatalogue",
        "params": {
            "filter": {
                "eventTypeIds": ["1"],  # 1 = Soccer
                "marketCountries": ["GB"],
                "marketTypeCodes": ["MATCH_ODDS"],
                "marketStartTime": {"from": from_time},
            },
            "maxResults": "20",
            "marketProjection": ["EVENT", "RUNNER_DESCRIPTION", "MARKET_START_TIME"],
        },
        "id": 1,
    }
    return _post(body)


# Return the best available lay price for a given selection.
# Returns None if no lay prices are currently available.
def list_market_book(market_id: str, selection_id: int) -> float | None:
    body = {
        "jsonrpc": "2.0",
        "method": "SportsAPING/v1.0/listMarketBook",
        "params": {
            "marketIds": [market_id],
            "priceProjection": {"priceData": ["EX_BEST_OFFERS"]},
        },
        "id": 1,
    }
    result = _post(body)
    market = result[0]

    for runner in market["runners"]:
        if runner["selectionId"] == selection_id:
            lay_prices = runner.get("ex", {}).get("availableToLay", [])
            return lay_prices[0]["price"] if lay_prices else None

    return None


# Make an authenticated POST request to the Betfair JSON-RPC API.
def _post(body: dict) -> list:
    headers = {
        "X-Authentication": get_token(),
        "X-Application": APP_KEY,
        "Content-Type": "application/json",
    }
    response = requests.post(BETFAIR_API_URL, headers=headers, json=body)
    data = response.json()

    if "result" not in data:
        raise RuntimeError(f"Unexpected Betfair response: {data}")

    return data["result"]


# ---------------------------------------------------------------------------
# Market matching
# ---------------------------------------------------------------------------

# Normalise a team name for fuzzy comparison (lowercase, strip FC etc.).
def normalise(name: str) -> str:
    return name.lower().replace("fc", "").replace(".", "").strip()


# Parse a Betfair ISO timestamp (with or without Z suffix) into a datetime.
def parse_betfair_time(time_str: str) -> datetime:
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


# Build a match dict from a UTC kickoff time.
# Stub: home/away are hardcoded until hooked up to a real data source.
def get_match(utc_time: datetime) -> dict:
    utc_time = utc_time.replace(tzinfo=ZoneInfo("UTC"))
    return {
        "home": "West Ham",
        "away": "Wolves",
        "startTime": utc_time.isoformat(),
    }


# Find the Betfair market matching the given home/away teams.
# Checks runner names only — time is not used for matching.
# Returns the market dict if found, otherwise None.
def find_market(match: dict, catalogue: list[dict]) -> dict | None:
    home = normalise(match["home"])
    away = normalise(match["away"])

    for market in catalogue:
        runner_names = [normalise(r["runnerName"]) for r in market["runners"]]
        if home in runner_names and away in runner_names:
            return market

    return None


# Return the Betfair selection ID for a given team within a market.
def get_selection_id(market: dict, team: str) -> int | None:
    for runner in market["runners"]:
        if normalise(runner["runnerName"]) == normalise(team):
            return runner["selectionId"]
    return None
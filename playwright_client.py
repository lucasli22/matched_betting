from playwright.sync_api import sync_playwright, Playwright, Page
from rich import print

SPORTSBET_SOCCER_URL = "https://www.sportsbet.com.au/betting/soccer"

# Selector for each match card on the soccer page.
EVENT_CARD_SELECTOR = 'div[data-automation-id$="-competition-event-card"]'

# Selectors for team names and odds within a card.
NAME_SELECTOR = '[data-automation-id$="-three-outcome-captioned-label"]'
ODDS_SELECTOR = '[data-automation-id$="-three-outcome-captioned-text"]'


# Normalise a team name for fuzzy comparison (lowercase, strip FC etc.).
def normalise(name: str) -> str:
    return name.lower().replace("fc", "").replace(".", "").strip()


# ---------------------------------------------------------------------------
# Scraping
# ---------------------------------------------------------------------------

# Scrape the Sportsbet soccer page and return the back odds for the home team.
# Returns the odds as a string, or None if the match isn't found.
def run(playwright: Playwright, home: str, away: str) -> str | None:
    chrome = playwright.chromium
    browser = chrome.launch(headless=False)
    page = browser.new_page()

    page.goto(SPORTSBET_SOCCER_URL)
    page.wait_for_selector(EVENT_CARD_SELECTOR)

    event_cards = page.locator(EVENT_CARD_SELECTOR)
    count = event_cards.count()
    print(f"Found {count} events.")

    for i in range(count):
        card = event_cards.nth(i)

        names = card.locator(NAME_SELECTOR)
        odds  = card.locator(ODDS_SELECTOR)

        if names.count() == 0 or odds.count() == 0:
            continue

        # Build a dict of { normalised_team_name: odds } for this card.
        game: dict[str, str] = {}
        for j in range(names.count()):
            name  = names.nth(j).inner_text()
            price = odds.nth(j).inner_text() if j < odds.count() else "N/A"
            game[normalise(name)] = price

        if normalise(home) in game and normalise(away) in game:
            return game[normalise(home)]

    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

# Launch a browser, scrape Sportsbet, and return the back odds for the home team.
def get_back_odds(home: str, away: str) -> str | None:
    with sync_playwright() as playwright:
        return run(playwright, home, away)
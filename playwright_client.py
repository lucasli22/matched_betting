from playwright.sync_api import sync_playwright, Playwright
from rich import print

def normalise(name):
    return name.lower().replace("fc", "").replace(".", "").strip()

def run(playwright):
    start_url = "https://www.sportsbet.com.au/betting/soccer"
    team = "Newcastle"
    away = "Barcelona"
    chrome = playwright.chromium
    browser = chrome.launch()
    page = browser.new_page()
    page.goto(start_url)

    # Wait for the specific container or elements to load to avoid scraping an empty page
    page.wait_for_selector('div[data-automation-id$="-competition-event-card"]')

    # Locate all event cards. The $= means "ends with"
    event_cards = page.locator('div[data-automation-id$="-competition-event-card"]')
    
    # Get the count to iterate over them safely
    count = event_cards.count()
    print(f"Found {count} events.")

    for i in range(count):
        card = event_cards.nth(i)
        # Find the <a> tag within this specific card to get the link
        link_element = card.locator('a').first
        
        if link_element.count() > 0:
            href = link_element.get_attribute('href')
        else:
            href = "N/A"
        # print(f"Match Link: {href}")
        names = card.locator('[data-automation-id$="-three-outcome-captioned-label"]')
        odds = card.locator('[data-automation-id$="-three-outcome-captioned-text"]')
        if names.count() == 0 or odds.count() == 0:
            continue
        name_count = names.count()
        game = {}
        for j in range(name_count):
            name = names.nth(j).inner_text()
            if j < odds.count():
                price = odds.nth(j).inner_text()
            else:
                price = "N/A"
            game[normalise(name)] = price
            
        if normalise(team) in game and normalise(away) in game:
            for x, y in game.items():
                print(f"Name: {x}\nPrice: {y}\n")
        else:
            game.clear()


with sync_playwright() as playwright:
    run(playwright)

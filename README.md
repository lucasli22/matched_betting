# Matched Betting Calculator

A CLI tool that automates the core workflow of matched betting on soccer matches. It fetches live lay odds from Betfair and back odds from Sportsbet, then calculates the optimal lay stake and expected profit for both outcomes.

## How it works

Matched betting involves placing a **back bet** (outcome will happen) on a bookmaker and a **lay bet** (outcome won't happen) on a betting exchange, so that one position always covers the other. The tool automates the two most tedious steps — pulling live odds — and then runs the hedge calculations.

```
Home team / Away team / Kickoff time / Back stake / Bet type
        ↓                                   ↓
  Betfair API (lay odds)        Sportsbet scrape (back odds)
        ↓                                   ↓
              Hedge calculator
                    ↓
         Terminal breakdown
```

## Bet types

| Code | Name | Use case |
|------|------|----------|
| `sr` | Stake Returned | Normal cash bet — you get your stake back if the back wins |
| `snr` | Stake Not Returned | Bonus/free bet — you only receive winnings, not the stake |
| `qualifying` | Qualifying Bet | Used to unlock a bonus offer (treated as `sr` in calculations) |

## Setup

**Requirements:** Python 3.9+

```bash
pip install requests python-dotenv playwright rich
playwright install chromium
```

Create a `.env` file in the project root:

```
USERNAME=your_betfair_username
PASSWORD=your_betfair_password
APP_KEY=your_betfair_app_key
```

You need a [Betfair](https://www.betfair.com.au) account and a delayed-data API application key. The APP_KEY for your application is available in the Betfair developer portal.

## Usage

```bash
python main.py
```

You'll be prompted for:

- **Home team** / **Away team** — used to find the market on both Betfair and Sportsbet
- **Kickoff time** (year / month / day / hour / minute in UTC)
- **Back stake** — amount you're placing on the bookmaker
- **Bet type** — `sr`, `snr`, or `qualifying`

A browser window opens to scrape Sportsbet odds, then the terminal prints a breakdown:

```
  ──────────────────────────────────────
        Matched Betting Calculator
           Bonus Bet (SNR)
  ──────────────────────────────────────
  Bet Type               Bonus Bet (SNR)
  Back Stake             $50.00
  Back Odds              4.20
  Lay Odds               4.40
  Betfair Commission     5%
  ──────────────────────────────────────
  Lay Stake              $34.52
  Liability              $117.37
  ──────────────────────────────────────
  If back wins           +$161.48
  If back loses          +$32.79
  ──────────────────────────────────────
```

## Project structure

| File | Purpose |
|------|---------|
| `main.py` | Entry point — prompts for input, orchestrates fetching and calculation |
| `betfair_client.py` | Betfair JSON-RPC API calls (auth, market catalogue, live prices) |
| `playwright_client.py` | Playwright scraper for Sportsbet soccer odds |
| `calculator.py` | Lay stake, liability, and profit calculations |
| `cli.py` | Terminal output formatting |

## Calculations

**Lay stake (SR):**
```
lay_stake = (back_odds × back_stake) / (lay_odds − commission)
```

**Lay stake (SNR / bonus bet):**
```
lay_stake = ((back_odds − 1) × back_stake) / (lay_odds − commission)
```

**Liability:**
```
liability = lay_stake × (lay_odds − 1)
```

Betfair commission is fixed at 5%.

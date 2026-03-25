from betfair_client import get_match, list_market_catalogue, find_market, get_selection_id, list_market_book
from calculator import calculate_lay_stake, calculate_liability, calculate_profit
from cli import print_breakdown
from playwright_client import get_back_odds
from datetime import datetime

def prompt_kickoff() -> datetime:
    print("\nKickoff time:")
    year  = int(input("  Year  : ").strip())
    month = int(input("  Month : ").strip())
    day   = int(input("  Day   : ").strip())
    hour  = int(input("  Hour  : ").strip())
    minute = int(input("  Minute: ").strip())
    return datetime(year=year, month=month, day=day, hour=hour, minute=minute)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    
    # args = parse_args()

    # Prompt user for match details
    home = input("Home team: ").strip()
    away = input("Away team: ").strip()
    kickoff_utc = prompt_kickoff()
    back_stake = float(input("Back stake ($): ").strip())
    bet_type = input("Bet type (qualifying / snr / sr): ").strip()
    
   
    print("\nFetching odds...")

    # Get lay odds from Betfair
    match = get_match(kickoff_utc)
    catalogue = list_market_catalogue(match)
    market = find_market(match, catalogue)

    if not market:
        print(f"Could not find a Betfair market for {home} vs {away}.")
        exit()

    selection_id = get_selection_id(market, home)

    if not selection_id:
        print(f"Could not find {home} in the Betfair market.")
        exit()

    lay_odds = list_market_book(market["marketId"], selection_id)

    if not lay_odds:
        print(f"No lay prices available for {home} on Betfair yet.")
        exit()

    # Get back odds from Sportsbet
    back_odds = get_back_odds(home, away)
    # back_odds = 1.72

    if not back_odds:
        print(f"Could not find {home} vs {away} on Sportsbet.")
        exit()

    # Calculate
    lay_stake = calculate_lay_stake(back_stake, back_odds, lay_odds, bet_type)
    liability = calculate_liability(lay_stake, lay_odds)
    back_wins, back_loses = calculate_profit(back_stake, back_odds, lay_stake, lay_odds, bet_type)

    # Print results
    print_breakdown(
        bet_type,
        back_stake,
        back_odds,
        lay_odds,
        lay_stake,
        liability,
        back_wins,
        back_loses,
    )

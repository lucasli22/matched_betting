# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------
 
# Print a full breakdown of the bet to the terminal.
def print_breakdown(
    bet_type: str,
    back_stake: float,
    back_odds: float,
    lay_odds: float,
    lay_stake: float,
    liability: float,
    back_wins: float,
    back_loses: float
) -> None:
    type_label = {"qualifying": "Qualifying Bet", "snr": "Bonus Bet (SNR)", "sr": "Bonus Bet (SR)"}
 
    print()
    print(f"  {'─' * 38}")
    print(f"  {'Matched Betting Calculator':^38}")
    print(f"  {type_label[bet_type]:^38}")
    print(f"  {'─' * 38}")
    print(f"  {'Bet Type':<22} {type_label[bet_type]}")
    print(f"  {'Back Stake':<22} ${back_stake:.2f}")
    print(f"  {'Back Odds':<22} {back_odds:.2f}")
    print(f"  {'Lay Odds':<22} {lay_odds:.2f}")
    print(f"  {'Betfair Commission':<22} {0.05 * 100:.0f}%")
    print(f"  {'─' * 38}")
    print(f"  {'Lay Stake':<22} ${lay_stake:.2f}")
    print(f"  {'Liability':<22} ${liability:.2f}")
    print(f"  {'─' * 38}")
    print(f"  {'If back wins':<22} ${back_wins:+.2f}")
    print(f"  {'If back loses':<22} ${back_loses:+.2f}")
    print(f"  {'─' * 38}")
 
    # Warning if outcomes are significantly unbalanced
    if abs(back_wins - back_loses) > 0.5:
        print(f"  ⚠  Outcomes differ by ${abs(back_wins - back_loses):.2f}")
        print(f"  {'─' * 38}")
 
    print()
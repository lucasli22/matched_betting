# ---------------------------------------------------------------------------
# Calculations
# ---------------------------------------------------------------------------

BETFAIR_COMMISSION = 0.05  # float: Commission rate charged on lay winnings (5%)

"""
    Calculate the required lay stake to balance a matched bet.

    Parameters:
        back_stake (float): Amount placed on the back bet.
        back_odds (float): Odds of the back bet.
        lay_odds (float): Odds of the lay bet.
        bet_type (str): Type of bet:
                        - "sr"  = stake returned (normal cash bet)
                        - "snr" = stake not returned (bonus bet)

    Returns:
        float: The lay stake required to hedge the bet.
"""
def calculate_lay_stake(
    back_stake: float,
    back_odds: float,
    lay_odds: float,
    bet_type: str
) -> float:
    
    if bet_type == "sr":
        # Stake Returned:
        # Lay stake = (back odds * back stake) / (lay odds - commission)
        return back_odds * back_stake / (lay_odds - BETFAIR_COMMISSION)

    elif bet_type == "snr":
        # Stake Not Returned (free/bonus bet):
        # Lay stake = ((back odds - 1) * back stake) / (lay odds - commission)
        return (back_odds - 1) * back_stake / (lay_odds - BETFAIR_COMMISSION)

    else:
        # Default to SR formula if bet_type is unrecognised
        return back_odds * back_stake / (lay_odds - BETFAIR_COMMISSION)


"""
    Calculate the liability of a lay bet (amount you risk losing).

    Parameters:
        lay_stake (float): The lay stake placed.
        lay_odds (float): Odds of the lay bet.

    Returns:
        float: The liability (maximum loss if lay bet loses).
"""
def calculate_liability(
    lay_stake: float,
    lay_odds: float
) -> float:
    # Liability = lay stake * (lay odds - 1)
    return lay_stake * (lay_odds - 1)


"""
    Calculate profit for both outcomes of a matched bet.

    Parameters:
        back_stake (float): Amount placed on the back bet.
        back_odds (float): Odds of the back bet.
        lay_stake (float): Amount placed on the lay bet.
        lay_odds (float): Odds of the lay bet.
        bet_type (str): Type of bet:
                        - "sr"  = stake returned
                        - "snr" = stake not returned

    Returns:
        tuple[float, float]:
            - back_wins (float): Profit if the back bet wins
            - back_loses (float): Profit if the back bet loses
"""
def calculate_profit(
    back_stake: float,
    back_odds: float,
    lay_stake: float,
    lay_odds: float,
    bet_type: str
) -> tuple[float, float]:
    

    # Commission is only paid on lay winnings
    lay_commission = lay_stake * BETFAIR_COMMISSION

    if bet_type == "snr":
        # Stake Not Returned (bonus bet):
        # You only receive winnings, not the original stake
        back_wins = ((back_odds - 1) * back_stake) - ((lay_odds - 1) * lay_stake)
        back_loses = lay_stake - lay_commission

    elif bet_type == "sr":
        # Stake Returned:
        # You receive both stake + profit when back bet wins
        back_wins = back_odds * back_stake - ((lay_odds - 1) * lay_stake)
        back_loses = lay_stake - lay_commission

    else:
        # Generic/other case (treated like normal betting with stake loss)
        back_wins = ((back_odds - 1) * back_stake) - (lay_stake * (lay_odds - 1))
        back_loses = lay_stake - lay_commission - back_stake

    return back_wins, back_loses
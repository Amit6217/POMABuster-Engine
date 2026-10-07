from typing import List, Dict
from core.models import Trade

class MarketDominationDetector:
    """
    Detects Price Oracle Manipulation (POM) using SEC-inspired Market Domination rules.
    """
    
    def __init__(self, token_supplies: Dict[str, float], threshold: float = 0.0001):
        """
        :param token_supplies: A dictionary mapping token addresses to their total supply.
        :param threshold: The domination threshold (e.g., 0.0001 for 0.01%).
        """
        self.token_supplies = token_supplies
        self.threshold = threshold

    def detect(self, trades: List[Trade]) -> List[Trade]:
        pom_trades = []
        
        for trade in trades:
            supply_in = self.token_supplies.get(trade.asset_in, float('inf'))
            supply_out = self.token_supplies.get(trade.asset_out, float('inf'))
            
            if trade.amount_in >= supply_in * self.threshold or trade.amount_out >= supply_out * self.threshold:
                pom_trades.append(trade)
                
        return pom_trades

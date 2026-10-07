from typing import List, Dict
from core.models import Trade

class ArbitrageDetector:
    """
    Detects Arbitrage trades by finding cyclic patterns where Profit > 0.
    """
    
    @staticmethod
    def detect(trades: List[Trade]) -> List[List[Trade]]:
        arbitrages = []
        
        tx_trades: Dict[str, List[Trade]] = {}
        for trade in trades:
            if trade.transaction_hash not in tx_trades:
                tx_trades[trade.transaction_hash] = []
            tx_trades[trade.transaction_hash].append(trade)
            
        for tx_hash, t_trades in tx_trades.items():
            if len(t_trades) >= 2:
                # Check if it forms a cycle (e.g., A -> B -> C -> A)
                if t_trades[0].asset_in == t_trades[-1].asset_out:
                    # Calculate profit: if final output is greater than initial input
                    if t_trades[-1].amount_out > t_trades[0].amount_in:
                        arbitrages.append(t_trades)
                        
        return arbitrages

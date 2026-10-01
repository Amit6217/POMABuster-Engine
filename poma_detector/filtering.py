"""
Stage 2: SEC-Inspired Filtering Gate

Applies financial market manipulation heuristics (inspired by US SEC rules)
to filter out legitimate trading activity and isolate suspicious oracle manipulation.
"""

from typing import List, Dict, Set, Tuple
from .models import Trade, ActionType


class SECFilteringGate:
    """Filtering engine enforcing market manipulation indicators."""

    def __init__(self,
                 trade_size_threshold_pct: float = 0.05,
                 holder_concentration_threshold_pct: float = 30.0,
                 max_block_proximity: int = 2):
        self.trade_size_threshold_pct = trade_size_threshold_pct
        self.holder_concentration_threshold_pct = holder_concentration_threshold_pct
        self.max_block_proximity = max_block_proximity

    def is_trade_size_anomalous(self, trade: Trade, pool_liquidity: float) -> bool:
        """Flags trades moving > threshold% of pool's total depth."""
        if pool_liquidity <= 0:
            return True
        return (trade.amount_in / pool_liquidity) > self.trade_size_threshold_pct

    def detect_wash_round_trips(self, trades: List[Trade]) -> Set[str]:
        """
        Detects round-trip wash trades (e.g. User buys Asset A then sells Asset A back
        within a small log window to temporarily shift AMM spot price).
        """
        suspicious_tx_hashes = set()
        for i, t1 in enumerate(trades):
            for t2 in trades[i + 1:]:
                same_operator = t1.operator.lower() == t2.operator.lower()
                opposite_direction = (
                    t1.asset_in.lower() == t2.asset_out.lower() and
                    t1.asset_out.lower() == t2.asset_in.lower()
                )
                close_proximity = abs(t1.log_index - t2.log_index) <= 10
                
                if same_operator and opposite_direction and close_proximity:
                    t1.flags.append("SEC_WASH_ROUND_TRIP")
                    t2.flags.append("SEC_WASH_ROUND_TRIP")
                    suspicious_tx_hashes.add(t1.transaction_hash)
                    suspicious_tx_hashes.add(t2.transaction_hash)

        return suspicious_tx_hashes

    def filter_trades(self,
                      trades: List[Trade],
                      pool_liquidity_map: Dict[str, float] = None,
                      concentrated_tokens: Set[str] = None) -> List[Trade]:
        """
        Master filtering pipeline. Evaluates trades against SEC manipulation rules.
        """
        if pool_liquidity_map is None:
            pool_liquidity_map = {}
        if concentrated_tokens is None:
            concentrated_tokens = set()

        # Phase A: Flag individual trade anomalies
        for trade in trades:
            pool_depth = pool_liquidity_map.get(trade.pool_address.lower(), float('inf'))
            if self.is_trade_size_anomalous(trade, pool_depth):
                trade.flags.append("SEC_ANOMALOUS_TRADE_SIZE")

            if trade.asset_in.lower() in concentrated_tokens or trade.asset_out.lower() in concentrated_tokens:
                trade.flags.append("SEC_HIGH_TOKEN_CONCENTRATION")

        # Phase B: Wash trading detection
        self.detect_wash_round_trips(trades)

        # Retain trades with at least one triggered SEC flag
        return [t for t in trades if len(t.flags) > 0]

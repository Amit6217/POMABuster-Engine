"""
Stage 3: Multi-Transaction Linking Engine

Correlates Price Oracle Manipulation (POM) transactions with Arbitrage (ARB)
transactions that exploit resulting price disparities across block windows.
"""

from typing import List, Dict, Set
from .models import Trade, ArbitrageEvent, POMAlert, RiskLevel


class MultiTxLinkingEngine:
    """Engine for finding cross-transaction attack-arbitrage linkages."""

    def __init__(self, max_block_window: int = 2):
        self.max_block_window = max_block_window

    def detect_arbitrage_events(self, trades: List[Trade]) -> List[ArbitrageEvent]:
        """
        Identifies arbitrage events: trader buys token low in Pool 1 and sells high in Pool 2.
        """
        arb_events = []
        trades_by_operator: Dict[str, List[Trade]] = {}

        for t in trades:
            trades_by_operator.setdefault(t.operator.lower(), []).append(t)

        for operator, op_trades in trades_by_operator.items():
            for i, t1 in enumerate(op_trades):
                for t2 in op_trades[i + 1:]:
                    same_token = t1.asset_out.lower() == t2.asset_in.lower()
                    diff_pools = t1.pool_address.lower() != t2.pool_address.lower()
                    net_positive = t2.amount_out > t1.amount_in

                    if same_token and diff_pools and net_positive:
                        arb_events.append(ArbitrageEvent(
                            operator=operator,
                            buy_pool=t1.pool_address,
                            sell_pool=t2.pool_address,
                            token=t1.asset_out,
                            profit_amount=t2.amount_out - t1.amount_in,
                            buy_tx_hash=t1.transaction_hash,
                            sell_tx_hash=t2.transaction_hash,
                            block_number=t1.block_number
                        ))

        return arb_events

    def correlate_manipulation_and_arbitrage(self,
                                              suspicious_trades: List[Trade],
                                              arbitrage_events: List[ArbitrageEvent]) -> List[POMAlert]:
        """
        Links suspicious price manipulation transactions with arbitrage events within block window.
        """
        alerts = []
        alert_counter = 1

        for pom in suspicious_trades:
            pom_block = pom.block_number
            pom_tokens = {pom.asset_in.lower(), pom.asset_out.lower()}

            for arb in arbitrage_events:
                arb_block = arb.block_number
                block_dist = abs(arb_block - pom_block)

                if block_dist <= self.max_block_window:
                    arb_token = arb.token.lower()
                    if arb_token in pom_tokens:
                        # POMA Alert Verified!
                        risk = RiskLevel.CRITICAL if block_dist == 0 else RiskLevel.HIGH
                        
                        alert = POMAlert(
                            alert_id=f"POMA-ALERT-{alert_counter:04d}",
                            poma_tx_hash=pom.transaction_hash,
                            arbitrage_tx_hash=arb.sell_tx_hash,
                            target_protocol=pom.pool_address,
                            manipulated_token=arb.token,
                            block_distance=block_dist,
                            risk_level=risk,
                            sec_rules_triggered=pom.flags,
                            description=(
                                f"Price Oracle Manipulation detected! Trade in block {pom_block} "
                                f"manipulated {arb.token} price on pool {pom.pool_address}. "
                                f"Exploited by arbitrage in block {arb_block} (distance: {block_dist} blocks)."
                            )
                        )
                        alerts.append(alert)
                        alert_counter += 1

        return alerts

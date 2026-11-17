"""
Algorithm 2: Price Oracle Manipulation (POM) Detection.
Implements Definition 2, Definition 3, Definition 4, Definition 5 & Algorithm 2
from the POMABuster research paper.

Detects:
1. Market Domination Trades (t_DOM):
   A trade where min(t) >= sigma * sup(addr(kin(t))) or
                 mout(t) >= sigma * sup(addr(kout(t)))
   where sup(a) is the total supply of the token, and sigma is the configurable threshold (default: 0.01%).

2. Wash Sale Trades (T_WASH):
   Where trading volume is repeatedly inflated across trades:
   sum(min(t)) >= sigma * sup(addr(kin(t))) or
   sum(mout(t)) >= sigma * sup(addr(kout(t)))
"""

from typing import List, Dict, Optional, Tuple
from collections import defaultdict
from backend.models.schema import Trade, POMCandidate, POMType, TokenInfo

class POMDetector:
    def __init__(self, token_registry: Dict[str, TokenInfo]):
        self.token_registry = token_registry

    def get_token_supply(self, token_address: str) -> float:
        token_address = token_address.lower()
        if token_address in self.token_registry:
            return self.token_registry[token_address].total_supply
        return 100_000_000.0

    def get_token_symbol(self, token_address: str) -> str:
        token_address = token_address.lower()
        if token_address in self.token_registry:
            return self.token_registry[token_address].symbol
        return "UNKNOWN"

    def detect_pom(self, trades: List[Trade], sigma: float) -> List[POMCandidate]:
        tx_trades_map: Dict[str, List[Trade]] = defaultdict(list)
        for t in trades:
            tx_trades_map[t.tx_hash].append(t)

        candidates: List[POMCandidate] = []

        for tx_hash, tx_trades in tx_trades_map.items():
            # 1. Check Market Domination (Algorithm 2: ISMARKETDOMINATION)
            dom_candidate = self.is_market_domination(tx_trades, sigma)
            if dom_candidate:
                candidates.append(dom_candidate)
                continue

            # 2. Check Wash Sale (Algorithm 2: ISWASHSALE)
            wash_candidate = self.is_wash_sale(tx_trades, sigma)
            if wash_candidate:
                candidates.append(wash_candidate)

        return candidates

    def is_market_domination(self, tx_trades: List[Trade], sigma: float) -> Optional[POMCandidate]:
        """
        Algorithm 2: ISMARKETDOMINATION(T, sigma)
        Identifies trades where input or output amount exceeds sigma * total_supply.
        Selects the dominant token (highest fraction of total supply).
        """
        best_candidate: Optional[POMCandidate] = None
        highest_pct = 0.0

        for t in tx_trades:
            sup_in = self.get_token_supply(t.token_in)
            pct_in = (t.amount_in / sup_in) if sup_in > 0 else 0.0

            sup_out = self.get_token_supply(t.token_out)
            pct_out = (t.amount_out / sup_out) if sup_out > 0 else 0.0

            # Determine dominant side
            if pct_out >= pct_in and pct_out >= sigma and pct_out > highest_pct:
                highest_pct = pct_out
                sym_out = self.get_token_symbol(t.token_out)
                explanation = (
                    f"Market Domination detected: Trade output {t.amount_out:,.2f} {sym_out} "
                    f"represents {pct_out * 100:.4f}% of total supply ({sup_out:,.0f} {sym_out}), "
                    f"exceeding threshold sigma = {sigma * 100:.4f}%."
                )
                best_candidate = POMCandidate(
                    pom_id=f"pom_dom_{t.tx_hash[:10]}_{sym_out}",
                    pom_type=POMType.MARKET_DOMINATION,
                    tx_hash=t.tx_hash,
                    block_number=t.block_number,
                    operator=t.operator,
                    pool_address=t.pool_address,
                    token_address=t.token_out,
                    token_symbol=sym_out if sym_out != "UNKNOWN" else t.token_out_symbol,
                    trade_amount=t.amount_out,
                    total_supply=sup_out,
                    supply_percentage=pct_out,
                    threshold_sigma=sigma,
                    explanation=explanation,
                    trades=[t],
                )
            elif pct_in > pct_out and pct_in >= sigma and pct_in > highest_pct:
                highest_pct = pct_in
                sym_in = self.get_token_symbol(t.token_in)
                explanation = (
                    f"Market Domination detected: Trade input {t.amount_in:,.2f} {sym_in} "
                    f"represents {pct_in * 100:.4f}% of total supply ({sup_in:,.0f} {sym_in}), "
                    f"exceeding threshold sigma = {sigma * 100:.4f}%."
                )
                best_candidate = POMCandidate(
                    pom_id=f"pom_dom_{t.tx_hash[:10]}_{sym_in}",
                    pom_type=POMType.MARKET_DOMINATION,
                    tx_hash=t.tx_hash,
                    block_number=t.block_number,
                    operator=t.operator,
                    pool_address=t.pool_address,
                    token_address=t.token_in,
                    token_symbol=sym_in if sym_in != "UNKNOWN" else t.token_in_symbol,
                    trade_amount=t.amount_in,
                    total_supply=sup_in,
                    supply_percentage=pct_in,
                    threshold_sigma=sigma,
                    explanation=explanation,
                    trades=[t],
                )

        return best_candidate

    def is_wash_sale(self, tx_trades: List[Trade], sigma: float) -> Optional[POMCandidate]:
        """
        Algorithm 2: ISWASHSALE(T, sigma)
        Aggregates volume per token across multiple trades in a transaction.
        """
        if len(tx_trades) < 2:
            return None

        amounts_in = defaultdict(float)
        amounts_out = defaultdict(float)
        symbols = {}

        for t in tx_trades:
            amounts_in[t.token_in.lower()] += t.amount_in
            amounts_out[t.token_out.lower()] += t.amount_out
            symbols[t.token_in.lower()] = t.token_in_symbol
            symbols[t.token_out.lower()] = t.token_out_symbol

        all_tokens = set(amounts_in.keys()).union(set(amounts_out.keys()))
        for token in all_tokens:
            sup = self.get_token_supply(token)
            if sup <= 0:
                continue

            total_token_vol = amounts_in[token] + amounts_out[token]
            pct = total_token_vol / sup

            if pct >= sigma:
                sym = self.get_token_symbol(token)
                if sym == "UNKNOWN":
                    sym = symbols.get(token, "TOKEN")

                explanation = (
                    f"Wash Sale detected: Aggregate volume across {len(tx_trades)} trades reached "
                    f"{total_token_vol:,.2f} {sym} ({pct * 100:.4f}% of supply {sup:,.0f} {sym}), "
                    f"exceeding wash threshold sigma = {sigma * 100:.4f}%."
                )
                first_trade = tx_trades[0]
                return POMCandidate(
                    pom_id=f"pom_wash_{first_trade.tx_hash[:10]}_{sym}",
                    pom_type=POMType.WASH_SALE,
                    tx_hash=first_trade.tx_hash,
                    block_number=first_trade.block_number,
                    operator=first_trade.operator,
                    pool_address=first_trade.pool_address,
                    token_address=token,
                    token_symbol=sym,
                    trade_amount=total_token_vol,
                    total_supply=sup,
                    supply_percentage=pct,
                    threshold_sigma=sigma,
                    explanation=explanation,
                    trades=tx_trades,
                )

        return None

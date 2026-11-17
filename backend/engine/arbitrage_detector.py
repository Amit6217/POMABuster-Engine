"""
Definition 6: Arbitrage Trade Detection.
Implements Definition 6 from the POMABuster research paper.

An arbitrage trade T_ARB is defined as a vector of trades (t_0, t_1, ..., t_{N-1}) if and only if:
  1. Transfer Loop / Chained Swaps:
     kout(t_{j-1}) == kin(t_j) for all j in {1, ..., N-1}
  2. Non-negative token outcome for each token k in K:
     sum(tokens_received) - sum(tokens_spent) >= 0 (within numeric epsilon)
  3. Positive outcome for the sum of all tokens (arbitrageur realizes net profit):
     profit > 0
"""

from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict
from backend.models.schema import Trade, ArbitrageTrade, TokenInfo

class ArbitrageDetector:
    def __init__(self, token_registry: Dict[str, TokenInfo]):
        self.token_registry = token_registry

    def get_token_price(self, token_symbol: str) -> float:
        for t in self.token_registry.values():
            if t.symbol.upper() == token_symbol.upper():
                return t.price_usd
        # Default fallback prices for common tokens if unlisted
        common = {
            "WETH": 2040.0, "ETH": 2040.0,
            "WBTC": 28500.0, "RENBTC": 28450.0,
            "USDC": 1.0, "USDT": 1.0, "DAI": 1.0
        }
        return common.get(token_symbol.upper(), 1.0)

    def detect_arbitrages(self, trades: List[Trade]) -> List[ArbitrageTrade]:
        """
        Analyzes trades within transactions to detect arbitrage loops and profit outcomes.
        """
        tx_trades_map: Dict[str, List[Trade]] = defaultdict(list)
        for t in trades:
            tx_trades_map[t.tx_hash].append(t)

        arbitrages: List[ArbitrageTrade] = []

        for tx_hash, tx_trades in tx_trades_map.items():
            arb = self._analyze_tx_for_arbitrage(tx_trades)
            if arb:
                arbitrages.append(arb)

        return arbitrages

    def _analyze_tx_for_arbitrage(self, trades: List[Trade]) -> Optional[ArbitrageTrade]:
        if not trades:
            return None

        # Sort trades by log execution order
        sorted_trades = sorted(trades, key=lambda t: t.in_log_index)

        # 1. Build token flow chains (kout(t_{j-1}) == kin(t_j))
        # Find paths through trades
        chains = self._find_trade_chains(sorted_trades)
        if not chains:
            # If no strict chain, check if net token balance across trades yields positive profit with closed flow
            chains = [sorted_trades]

        for chain in chains:
            # Calculate net balance change for the trader/operator for each token
            # In a trade t:
            # Operator/Trader spent amount_in of token_in
            # Operator/Trader received amount_out of token_out
            net_tokens: Dict[str, float] = defaultdict(float)
            tokens_involved: Set[str] = set()

            for t in chain:
                sym_in = t.token_in_symbol.upper()
                sym_out = t.token_out_symbol.upper()
                net_tokens[sym_in] -= t.amount_in
                net_tokens[sym_out] += t.amount_out
                tokens_involved.add(sym_in)
                tokens_involved.add(sym_out)

            # Check Definition 6 conditions:
            # Eq 8: Non-negative outcome for each token k (with tiny floating point tolerance)
            # Eq 9: Sum outcome > 0 (profit > 0)
            
            # Determine intermediate tokens: tokens where net delta is ~0 (exchanged through)
            intermediate_tokens = []
            profit_token = None
            max_profit_usd = 0.0
            profit_amount = 0.0

            # Epsilon for float rounding
            has_negative = False
            total_usd_value = 0.0

            for sym, delta in net_tokens.items():
                price = self.get_token_price(sym)
                usd_val = delta * price
                total_usd_value += usd_val

                # If significantly negative (> 0.001 token and > $1 loss), violates Eq 8
                if delta < -0.0001 and usd_val < -1.0:
                    has_negative = True
                    break

                # Intermediate token check: net delta is near zero (swapped in and swapped out)
                if abs(usd_val) < 2.0 or abs(delta) < 0.001:
                    intermediate_tokens.append(sym)
                elif delta > 0.0001 and usd_val > max_profit_usd:
                    profit_token = sym
                    profit_amount = delta
                    max_profit_usd = usd_val

            # Also, intermediate tokens per Eq 11:
            # tokens appearing in the trade sequence between start and end
            for i, t in enumerate(chain):
                if i < len(chain) - 1:
                    intermediate_tokens.append(t.token_out_symbol.upper())
                if i > 0:
                    intermediate_tokens.append(t.token_in_symbol.upper())

            intermediate_tokens = list(set(intermediate_tokens))

            # If no single dominant profit token identified, pick the token with highest positive delta
            if not profit_token and total_usd_value > 1.0:
                for sym, delta in net_tokens.items():
                    if delta > 0:
                        profit_token = sym
                        profit_amount = delta
                        max_profit_usd = delta * self.get_token_price(sym)
                        break

            # Arbitrage requires non-negative token outcomes and positive net profit
            if not has_negative and total_usd_value > 5.0 and profit_token is not None:
                first_t = chain[0]
                explanation = (
                    f"Arbitrage detected in tx {first_t.tx_hash[:10]}...: "
                    f"Executed loop across {len(chain)} trades ({' -> '.join([t.token_in_symbol for t in chain] + [chain[-1].token_out_symbol])}). "
                    f"Generated net profit of {profit_amount:,.4f} {profit_token} (~${max_profit_usd:,.2f} USD) "
                    f"with intermediate token(s): {', '.join(intermediate_tokens) or 'None'}."
                )

                return ArbitrageTrade(
                    arb_id=f"arb_{first_t.tx_hash[:10]}_{profit_token}",
                    tx_hash=first_t.tx_hash,
                    block_number=first_t.block_number,
                    operator=first_t.operator,
                    recipient=chain[-1].recipient,
                    trades=chain,
                    tokens_involved=list(tokens_involved),
                    intermediate_tokens=intermediate_tokens,
                    net_deltas=dict(net_tokens),
                    profit_token=profit_token,
                    profit_amount=profit_amount,
                    profit_usd=max_profit_usd,
                    explanation=explanation,
                )

        return None

    def _find_trade_chains(self, trades: List[Trade]) -> List[List[Trade]]:
        """
        Extracts contiguous swap chains where kout(t_{j-1}) == kin(t_j).
        """
        if len(trades) <= 1:
            return [trades]

        chains: List[List[Trade]] = []
        current_chain = [trades[0]]

        for i in range(1, len(trades)):
            prev = current_chain[-1]
            curr = trades[i]
            if prev.token_out.lower() == curr.token_in.lower():
                current_chain.append(curr)
            else:
                if len(current_chain) >= 2:
                    chains.append(current_chain)
                current_chain = [curr]

        if len(current_chain) >= 1:
            chains.append(current_chain)

        return chains

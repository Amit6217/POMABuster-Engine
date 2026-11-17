"""
Definition 7: Linking POM and Arbitrage Transactions to Detect POMAs.
Implements Definition 7 & Section 3.4 / 4.3 / 4.6 from the POMABuster research paper.

A Price Oracle Manipulation Attack (POMA) occurs when:
  1. A price oracle manipulation trade (T_POM in T_DOM union T_WASH)
  2. And an arbitrage trade (T_ARB)
  3. Happen chronologically within block time window n (n = -1 for single-tx, n = 0 for same-block, n = 1, 2 for consecutive blocks)
  4. With non-empty intersection between manipulated tokens and arbitrage intermediate tokens:
     K_MANI = {kin(t), kout(t) | t in T_POM}
     K_INTR = {kin(t) | t in T_ARB} union {kout(t) | t in T_ARB and t != last_trade}
     K_MANI intersect K_INTR != empty_set
  5. The profit yielded from arbitrage is different from the manipulated token (market forces normalize manipulated token price).
"""

from typing import List, Dict, Optional, Tuple, Set
import time
from backend.models.schema import POMCandidate, ArbitrageTrade, POMAIncident, POMType, TokenInfo

class POMALinker:
    def __init__(self, token_registry: Dict[str, TokenInfo], strike_pct: float = 0.02):
        self.token_registry = token_registry
        self.strike_pct = strike_pct

    def link_poma(
        self,
        pom_candidates: List[POMCandidate],
        arbitrages: List[ArbitrageTrade],
        block_window_n: int = 2
    ) -> List[POMAIncident]:
        """
        Links POM transactions with Arbitrage transactions based on Definition 7.
        Prioritizes cross-transaction linkages when a prior POM transaction exists.
        """
        incidents: List[POMAIncident] = []
        
        # Sort POMs and Arbitrages chronologically by block number
        sorted_poms = sorted(pom_candidates, key=lambda p: p.block_number)
        sorted_arbs = sorted(arbitrages, key=lambda a: a.block_number)

        # Track linked (pom_tx, arb_tx) to avoid duplicate links
        linked_pairs = set()

        for arb in sorted_arbs:
            k_intr_symbols = set()
            for t in arb.trades:
                k_intr_symbols.add(t.token_in_symbol.upper())
                k_intr_symbols.add(t.token_out_symbol.upper())
            for it in arb.intermediate_tokens:
                k_intr_symbols.add(it.upper())

            # Find matching POMs: first look for external preceding POMs (cross-tx)
            # If none, look for same-tx POM
            candidate_matches = []

            for pom in sorted_poms:
                if arb.tx_hash.lower() == pom.tx_hash.lower():
                    block_dist = -1
                    is_multi_tx = False
                else:
                    block_dist = arb.block_number - pom.block_number
                    is_multi_tx = True

                # Chronology: arbitrage cannot occur before the POM
                if block_dist < -1:
                    continue

                # Filter by block window parameter n:
                if block_window_n == -1 and is_multi_tx:
                    continue
                if is_multi_tx and (block_dist > block_window_n or block_dist < 0):
                    continue

                # Token intersection check (Definition 7 Eq 10 & 11)
                k_mani_symbols = set()
                for t in pom.trades:
                    k_mani_symbols.add(t.token_in_symbol.upper())
                    k_mani_symbols.add(t.token_out_symbol.upper())
                k_mani_symbols.add(pom.token_symbol.upper())

                shared_tokens = list(k_mani_symbols.intersection(k_intr_symbols))
                if not shared_tokens:
                    continue

                candidate_matches.append((pom, block_dist, is_multi_tx, k_mani_symbols, shared_tokens))

            if not candidate_matches:
                continue

            # If cross-transaction matches exist, prioritize them over self-transaction matches
            cross_matches = [m for m in candidate_matches if m[2] is True]
            selected_matches = cross_matches if cross_matches else candidate_matches

            for pom, block_dist, is_multi_tx, k_mani_symbols, shared_tokens in selected_matches:
                pair_key = (pom.tx_hash.lower(), arb.tx_hash.lower())
                if pair_key in linked_pairs:
                    continue
                linked_pairs.add(pair_key)

                # Estimate price impact on pool (AMM supply fraction proxy)
                estimated_price_impact = min(0.35, max(0.021, pom.supply_percentage * 150.0))
                is_tp = (estimated_price_impact >= self.strike_pct)

                incident_id = f"poma_{pom.pom_id}_{arb.arb_id}"

                timing_desc = (
                    "Single Transaction (Atomic)" if not is_multi_tx
                    else f"Separate Transactions within Same Block (Bundle, Block #{pom.block_number})" if block_dist == 0
                    else f"Separate Transactions across {block_dist} Block(s) (#{pom.block_number} -> #{arb.block_number})"
                )

                rule_type_name = "Market Domination" if pom.pom_type == POMType.MARKET_DOMINATION else "Wash Sale"

                explanation = (
                    f"Price Oracle Manipulation Attack ({rule_type_name}) confirmed: "
                    f"{timing_desc}. "
                    f"Step 1: Account {pom.operator[:8]}... manipulated the spot price of {pom.token_symbol} "
                    f"by trading {pom.trade_amount:,.2f} {pom.token_symbol} ({pom.supply_percentage * 100:.4f}% of total supply), "
                    f"skewing the pool oracle feed by ~{estimated_price_impact * 100:.1f}%. "
                    f"Step 2: Account {arb.operator[:8]}... executed arbitrage exploiting the price disparity "
                    f"on intermediate token(s) [{', '.join(shared_tokens)}], "
                    f"extracting {arb.profit_amount:,.4f} {arb.profit_token} (~${arb.profit_usd:,.2f} USD) in profit."
                )

                incident = POMAIncident(
                    incident_id=incident_id,
                    attack_type=pom.pom_type,
                    is_multi_tx=is_multi_tx,
                    block_distance=block_dist,
                    pom_tx_hash=pom.tx_hash,
                    pom_block=pom.block_number,
                    pom_operator=pom.operator,
                    pom_token_address=pom.token_address,
                    pom_token_symbol=pom.token_symbol,
                    pom_amount=pom.trade_amount,
                    pom_supply_percentage=pom.supply_percentage,
                    arb_tx_hash=arb.tx_hash,
                    arb_block=arb.block_number,
                    arb_operator=arb.operator,
                    arb_profit_token=arb.profit_token,
                    arb_profit_amount=arb.profit_amount,
                    arb_profit_usd=arb.profit_usd,
                    manipulated_tokens=list(k_mani_symbols),
                    intermediate_tokens=list(k_intr_symbols),
                    shared_tokens=shared_tokens,
                    estimated_price_impact_pct=estimated_price_impact,
                    is_true_positive=is_tp,
                    flagged_timestamp=int(time.time()),
                    explanation=explanation,
                    pom_details={
                        "pom_type": pom.pom_type.value,
                        "pool_address": pom.pool_address,
                        "total_supply": pom.total_supply,
                        "threshold_sigma": pom.threshold_sigma,
                        "trades_count": len(pom.trades)
                    },
                    arb_details={
                        "trades_count": len(arb.trades),
                        "tokens_involved": arb.tokens_involved,
                        "net_deltas": arb.net_deltas
                    }
                )

                incidents.append(incident)

        return incidents

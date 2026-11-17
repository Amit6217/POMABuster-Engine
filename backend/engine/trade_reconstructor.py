"""
Algorithm 1: Reconstructing trades from ERC-20 transfer logs.
Implements Definition 1 & Algorithm 1 from the POMABuster research paper.

A trade t ~ (l1, l2) exists if and only if:
  addr(r(l1)) == addr(s(l2)) and addr(k(l1)) != addr(k(l2))

Where:
  - o(t) = s(l1): operator (trade issuer or router)
  - e(t) = r(l2): recipient of traded asset
  - ain(t) = k(l1): token transferred in
  - aout(t) = k(l2): token received out
  - min(t) = m(l1): amount transferred in
  - mout(t) = m(l2): amount transferred out
  - p(t) = r(l1) = s(l2): liquidity pool (AMM) or counterparty (Orderbook DEX)
"""

from typing import List, Dict, Set
from backend.models.schema import TransferLog, Trade

class TradeReconstructor:
    def __init__(self):
        pass

    def reconstruct_from_logs(self, logs: List[TransferLog]) -> List[Trade]:
        """
        Reconstructs trades from a list of transfer logs.
        Groups logs by transaction hash and reconstructs trades within each transaction.
        """
        tx_logs_map: Dict[str, List[TransferLog]] = {}
        for log in logs:
            tx_logs_map.setdefault(log.tx_hash, []).append(log)

        all_trades: List[Trade] = []
        for tx_hash, tx_logs in tx_logs_map.items():
            sorted_logs = sorted(tx_logs, key=lambda l: l.log_index)
            tx_trades = self._reconstruct_tx_trades(sorted_logs)
            all_trades.extend(tx_trades)

        return all_trades

    def _reconstruct_tx_trades(self, logs: List[TransferLog]) -> List[Trade]:
        """
        Algorithm 1 TOTRADE implementation for a single transaction.
        Finds disjoint transfer pairs (l1, l2) in chronological order i < j
        where tokens flow into pool r(l1) and out of the same pool s(l2).
        """
        trades: List[Trade] = []
        n = len(logs)
        used_indices: Set[int] = set()

        for i in range(n):
            if i in used_indices:
                continue
            l1 = logs[i]

            for j in range(i + 1, n):
                if j in used_indices:
                    continue
                l2 = logs[j]

                # Definition 1: addr(r(l1)) == addr(s(l2)) and addr(k(l1)) != addr(k(l2))
                pool_matches = (l1.receiver.lower() == l2.sender.lower())
                different_tokens = (l1.token_address.lower() != l2.token_address.lower())

                if pool_matches and different_tokens:
                    used_indices.add(i)
                    used_indices.add(j)

                    trade = Trade(
                        trade_id=f"trade_{l1.tx_hash[:10]}_{l1.log_index}_{l2.log_index}",
                        tx_hash=l1.tx_hash,
                        block_number=l1.block_number,
                        operator=l1.sender.lower(),
                        recipient=l2.receiver.lower(),
                        token_in=l1.token_address.lower(),
                        token_in_symbol=l1.token_symbol,
                        token_out=l2.token_address.lower(),
                        token_out_symbol=l2.token_symbol,
                        amount_in=l1.amount,
                        amount_out=l2.amount,
                        pool_address=l1.receiver.lower(),
                        timestamp=l1.timestamp,
                        in_log_index=l1.log_index,
                        out_log_index=l2.log_index,
                    )
                    trades.append(trade)
                    break

        return trades

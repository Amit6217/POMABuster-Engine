"""
Stage 1: Semantic Recovery Engine

Reconstructs high-level financial operations (Swaps, Add/Remove Liquidity)
from low-level EVM transfer event logs.
"""

from typing import List, Dict
from .models import Log, Trade, ActionType


class SemanticRecoveryEngine:
    """Engine responsible for converting raw blockchain log streams into structured trades."""

    def __init__(self):
        pass

    def recover_swaps(self, logs: List[Log]) -> List[Trade]:
        """
        Detects token swaps.
        Pattern: User sends Token A -> Pool, Pool sends Token B -> User (or Recipient).
        """
        trades = []
        normal_logs = [l for l in logs if l.is_normal_transfer]

        for i in range(len(normal_logs) - 1):
            l1 = normal_logs[i]
            l2 = normal_logs[i + 1]

            # Check if l1 is User -> Pool and l2 is Pool -> User/Recipient
            if l1.to_address.lower() == l2.from_address.lower() and l1.token_address.lower() != l2.token_address.lower():
                trades.append(Trade(
                    action_type=ActionType.SWAP,
                    operator=l1.from_address,
                    recipient=l2.to_address,
                    pool_address=l1.to_address,
                    asset_in=l1.token_address,
                    asset_out=l2.token_address,
                    amount_in=l1.value,
                    amount_out=l2.value,
                    block_number=l1.block_number,
                    transaction_hash=l1.transaction_hash,
                    log_index=l1.log_index
                ))
        return trades

    def recover_liquidity_mining(self, logs: List[Log]) -> List[Trade]:
        """
        Detects Liquidity Mining (Adding Liquidity).
        Pattern: User sends Asset -> Pool, Pool mints LP Token -> User.
        """
        trades = []
        for i in range(len(logs) - 1):
            l1 = logs[i]
            l2 = logs[i + 1]

            if l1.is_normal_transfer and l2.is_mint:
                if l1.to_address.lower() == l2.to_address.lower() or l1.from_address.lower() == l2.to_address.lower():
                    trades.append(Trade(
                        action_type=ActionType.LIQUIDITY_MINING,
                        operator=l1.from_address,
                        recipient=l2.to_address,
                        pool_address=l1.to_address,
                        asset_in=l1.token_address,
                        asset_out=l2.token_address,
                        amount_in=l1.value,
                        amount_out=l2.value,
                        block_number=l1.block_number,
                        transaction_hash=l1.transaction_hash,
                        log_index=l1.log_index
                    ))
        return trades

    def recover_liquidity_cancellation(self, logs: List[Log]) -> List[Trade]:
        """
        Detects Liquidity Cancellation (Removing Liquidity).
        Pattern: User burns LP Token -> Pool, Pool returns Asset -> User.
        """
        trades = []
        for i in range(len(logs) - 1):
            l1 = logs[i]
            l2 = logs[i + 1]

            if l1.is_burn and l2.is_normal_transfer:
                trades.append(Trade(
                    action_type=ActionType.LIQUIDITY_CANCEL,
                    operator=l1.from_address,
                    recipient=l2.to_address,
                    pool_address=l2.from_address,
                    asset_in=l1.token_address,
                    asset_out=l2.token_address,
                    amount_in=l1.value,
                    amount_out=l2.value,
                    block_number=l1.block_number,
                    transaction_hash=l1.transaction_hash,
                    log_index=l1.log_index
                ))
        return trades

    def process_transaction(self, logs: List[Log]) -> List[Trade]:
        """Main entry point to extract all semantics from a transaction's logs."""
        sorted_logs = sorted(logs, key=lambda l: l.log_index)
        recovered: List[Trade] = []

        recovered.extend(self.recover_swaps(sorted_logs))
        recovered.extend(self.recover_liquidity_mining(sorted_logs))
        recovered.extend(self.recover_liquidity_cancellation(sorted_logs))

        return sorted(recovered, key=lambda t: t.log_index)

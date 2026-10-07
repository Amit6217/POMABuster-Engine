from typing import List, Dict
from .models import Log, Trade

class TradeReconstructor:
    """
    Responsible for reconstructing logical DeFi trades from atomic token transfer logs.
    """
    
    @staticmethod
    def extract_trades(logs: List[Log]) -> List[Trade]:
        trades = []
        tx_logs: Dict[str, List[Log]] = {}
        
        # Group logs by transaction
        for log in logs:
            if log.transaction_hash not in tx_logs:
                tx_logs[log.transaction_hash] = []
            tx_logs[log.transaction_hash].append(log)
            
        for tx_hash, t_logs in tx_logs.items():
            # Look for pairs where log1.receiver == log2.sender (the pool)
            for i in range(len(t_logs)):
                for j in range(i+1, len(t_logs)):
                    log1 = t_logs[i]
                    log2 = t_logs[j]
                    
                    if log1.receiver == log2.sender and log1.asset != log2.asset:
                        trade = Trade(
                            block_number=log1.block_number,
                            transaction_hash=tx_hash,
                            operator=log1.sender,
                            recipient=log2.receiver,
                            pool=log1.receiver,
                            asset_in=log1.asset,
                            asset_out=log2.asset,
                            amount_in=log1.amount,
                            amount_out=log2.amount,
                            log_indices=[log1.log_index, log2.log_index]
                        )
                        trades.append(trade)
        return trades

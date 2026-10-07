from typing import List, Dict, Any
from core.models import Trade

class AttackLinker:
    """
    Links POM transactions and Arbitrage transactions to confirm a full POMA.
    """
    
    @staticmethod
    def link_attacks(pom_trades: List[Trade], arbitrages: List[List[Trade]], max_block_span: int = 2) -> List[Dict[str, Any]]:
        linked_attacks = []
        
        for pom in pom_trades:
            for arb in arbitrages:
                arb_block = arb[0].block_number
                
                # Verify block proximity
                if pom.block_number <= arb_block <= pom.block_number + max_block_span:
                    
                    # Verify token intersection
                    arb_assets = set([t.asset_in for t in arb] + [t.asset_out for t in arb])
                    if pom.asset_in in arb_assets or pom.asset_out in arb_assets:
                        linked_attacks.append({
                            "pom_tx": pom.transaction_hash,
                            "arb_tx": arb[0].transaction_hash,
                            "block_span": arb_block - pom.block_number
                        })
                        
        return linked_attacks

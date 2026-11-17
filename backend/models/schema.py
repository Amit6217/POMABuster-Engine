"""
Pydantic Schemas for POMABuster entities and analysis results.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum

class POMType(str, Enum):
    MARKET_DOMINATION = "MARKET_DOMINATION"
    WASH_SALE = "WASH_SALE"

class TokenInfo(BaseModel):
    address: str
    symbol: str
    name: str
    decimals: int = 18
    total_supply: float
    price_usd: float = 0.0
    market_cap_usd: float = 0.0
    is_valuable: bool = True

class TransferLog(BaseModel):
    log_id: Optional[str] = None
    tx_hash: str
    block_number: int
    log_index: int
    sender: str
    receiver: str
    token_address: str
    token_symbol: str
    amount: float
    timestamp: int = 0

class Trade(BaseModel):
    trade_id: str
    tx_hash: str
    block_number: int
    operator: str           # o(t) = s(l1)
    recipient: str          # e(t) = r(l2)
    token_in: str           # ain(t) = k(l1)
    token_in_symbol: str
    token_out: str          # aout(t) = k(l2)
    token_out_symbol: str
    amount_in: float        # min(t) = m(l1)
    amount_out: float       # mout(t) = m(l2)
    pool_address: str       # p(t) = r(l1) = s(l2)
    timestamp: int = 0
    in_log_index: int = 0
    out_log_index: int = 0

class POMCandidate(BaseModel):
    pom_id: str
    pom_type: POMType
    tx_hash: str
    block_number: int
    operator: str
    pool_address: str
    token_address: str
    token_symbol: str
    trade_amount: float
    total_supply: float
    supply_percentage: float
    threshold_sigma: float
    explanation: str
    trades: List[Trade] = []

class ArbitrageTrade(BaseModel):
    arb_id: str
    tx_hash: str
    block_number: int
    operator: str
    recipient: str
    trades: List[Trade]
    tokens_involved: List[str]
    intermediate_tokens: List[str]
    net_deltas: Dict[str, float]  # token_symbol -> net amount change
    profit_token: str
    profit_amount: float
    profit_usd: float
    explanation: str

class POMAIncident(BaseModel):
    incident_id: str
    attack_type: POMType
    is_multi_tx: bool
    block_distance: int         # -1 for same-tx, 0 for same-block, 1, 2 for cross-block
    pom_tx_hash: str
    pom_block: int
    pom_operator: str
    pom_token_address: str
    pom_token_symbol: str
    pom_amount: float
    pom_supply_percentage: float
    arb_tx_hash: str
    arb_block: int
    arb_operator: str
    arb_profit_token: str
    arb_profit_amount: float
    arb_profit_usd: float
    manipulated_tokens: List[str]      # K_MANI
    intermediate_tokens: List[str]     # K_INTR
    shared_tokens: List[str]           # K_MANI ∩ K_INTR
    estimated_price_impact_pct: float  # Estimated spot price impact on DEX pool
    is_true_positive: bool             # Evaluated against strike percentage (>= 2%)
    flagged_timestamp: int
    explanation: str
    pom_details: Dict[str, Any]
    arb_details: Dict[str, Any]

class DetectionStats(BaseModel):
    total_logs: int
    total_trades: int
    pom_candidates_found: int
    market_domination_count: int
    wash_sales_count: int
    arbitrages_found: int
    poma_incidents_total: int
    multi_tx_incidents: int
    single_tx_incidents: int
    multi_tx_percentage: float
    total_manipulated_volume_usd: float
    total_extracted_profit_usd: float
    worst_case_fpr: float
    fnr: float
    top_assets_targeted: List[Dict[str, Any]]
    top_operators: List[Dict[str, Any]]
    block_time_distribution: Dict[str, int]

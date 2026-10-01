"""
Data models representing blockchain events, recovered DeFi semantics, and attack alerts.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum


class ActionType(Enum):
    SWAP = "SWAP"
    LIQUIDITY_MINING = "LIQUIDITY_MINING"
    LIQUIDITY_CANCEL = "LIQUIDITY_CANCEL"
    MINT = "MINT"
    BURN = "BURN"
    TRANSFER = "TRANSFER"


class RiskLevel(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


ZERO_ADDRESSES = {
    "0x0000000000000000000000000000000000000000",
    "0x0",
    "0",
    "0x0000000000000000000000000000000000000000000000000000000000000000"
}


@dataclass(frozen=True)
class Log:
    """Represents an EVM event log emitted during transaction execution."""
    block_number: int
    transaction_hash: str
    log_index: int
    token_address: str
    from_address: str
    to_address: str
    value: float

    @property
    def is_mint(self) -> bool:
        return self.from_address.lower() in ZERO_ADDRESSES and self.to_address.lower() not in ZERO_ADDRESSES

    @property
    def is_burn(self) -> bool:
        return self.from_address.lower() not in ZERO_ADDRESSES and self.to_address.lower() in ZERO_ADDRESSES

    @property
    def is_normal_transfer(self) -> bool:
        return self.from_address.lower() not in ZERO_ADDRESSES and self.to_address.lower() not in ZERO_ADDRESSES


@dataclass
class Trade:
    """Represents a high-level recovered DeFi operation."""
    action_type: ActionType
    operator: str          # Transaction initiator
    recipient: str         # Target receiving asset
    pool_address: str      # Liquidity Pool / AMM address
    asset_in: str          # Input token address
    asset_out: str         # Output token address
    amount_in: float       # Quantity in
    amount_out: float      # Quantity out
    block_number: int
    transaction_hash: str
    log_index: int
    flags: List[str] = field(default_factory=list)


@dataclass
class ArbitrageEvent:
    """Represents a detected arbitrage trade taking advantage of price disparities."""
    operator: str
    buy_pool: str
    sell_pool: str
    token: str
    profit_amount: float
    buy_tx_hash: str
    sell_tx_hash: str
    block_number: int


@dataclass
class POMAlert:
    """Represents a detected Price Oracle Manipulation Attack."""
    alert_id: str
    poma_tx_hash: str
    arbitrage_tx_hash: str
    target_protocol: str
    manipulated_token: str
    block_distance: int
    risk_level: RiskLevel
    sec_rules_triggered: List[str]
    description: str


@dataclass
class DetectionReport:
    """Comprehensive summary of detection results across a dataset."""
    total_transactions_analyzed: int
    total_trades_recovered: int
    suspicious_trades_flagged: int
    alerts_generated: List[POMAlert]
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0

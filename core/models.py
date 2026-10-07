from dataclasses import dataclass
from typing import List

@dataclass
class Log:
    block_number: int
    transaction_hash: str
    log_index: int
    asset: str
    sender: str
    receiver: str
    amount: float

@dataclass
class Trade:
    block_number: int
    transaction_hash: str
    operator: str
    recipient: str
    pool: str
    asset_in: str
    asset_out: str
    amount_in: float
    amount_out: float
    log_indices: List[int]

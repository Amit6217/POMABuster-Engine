"""
Configuration parameters for POMABuster detection engine.
Empirically tuned values based on research paper (IEEE S&P 2024):
- Optimal total supply threshold sigma: 0.01% (0.0001)
- Optimal block time span n: 2 blocks (covers 98.7% of multi-tx POMAs)
- Benchmark strike price impact threshold: 2% (0.02)
- Valuable token market cap threshold: $1,000,000 USD
"""

from pydantic import BaseModel, Field
import os

class SystemConfig(BaseModel):
    # Total supply percentage parameter sigma for Market Domination and Wash Sale
    # Default is 0.01% (0.0001) as determined in Section 4.3 of the paper
    sigma: float = Field(default=0.0001, ge=0.000001, le=0.5, description="Total supply fraction threshold (sigma)")
    
    # Block time span parameter n:
    # n = -1: single-transaction only (DeFiRanger baseline)
    # n = 0: same block
    # n = 1, 2: consecutive blocks (n=2 covers 98.7% of multi-tx POMAs per paper)
    block_window_n: int = Field(default=2, ge=-1, le=50, description="Max block difference between POM and Arbitrage")
    
    # Benchmark strike price deviation (for evaluating price impact watermark)
    strike_percentage: float = Field(default=0.02, ge=0.001, le=1.0, description="Strike price impact threshold (2%)")
    
    # Minimum token circulating market cap filter in USD ($1,000,000 default)
    min_market_cap_usd: float = Field(default=1_000_000.0, ge=0.0, description="Min market cap for high-value tokens")
    
    # Database path
    db_path: str = Field(default="pomabuster.db", description="Path to SQLite database")

# Global config instance with defaults
system_config = SystemConfig()

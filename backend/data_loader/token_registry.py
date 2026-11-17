"""
Token Registry containing metadata, contract addresses, total supply, and market data
for high-value ERC20 tokens as described in POMABuster Section 3.3, 4.2 & 4.7.
"""

from typing import Dict
from backend.models.schema import TokenInfo

# Normalized token dictionary (lowercase addresses)
HIGH_VALUE_TOKENS: Dict[str, TokenInfo] = {
    # WETH (Wrapped Ether) - most popular POMA target (11,997 incidents in paper)
    "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2": TokenInfo(
        address="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",
        symbol="WETH",
        name="Wrapped Ether",
        decimals=18,
        total_supply=3_250_000.0,
        price_usd=2040.60,
        market_cap_usd=6_631_950_000.0,
        is_valuable=True
    ),
    # WBTC (Wrapped Bitcoin) - second most targeted volatile asset (4,115 incidents in paper)
    "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599": TokenInfo(
        address="0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",
        symbol="WBTC",
        name="Wrapped BTC",
        decimals=8,
        total_supply=155_000.0,
        price_usd=28_500.0,
        market_cap_usd=4_417_500_000.0,
        is_valuable=True
    ),
    # RenBTC (used in the 2022 Curve/Uniswap exploit described in Section 3.1 & 3.5)
    "0xeb4c2781e4eba804ce9a9803c67d0893436bb27d": TokenInfo(
        address="0xeb4c2781e4eba804ce9a9803c67d0893436bb27d",
        symbol="RenBTC",
        name="renBTC",
        decimals=8,
        total_supply=14_200.0,
        price_usd=28_450.0,
        market_cap_usd=403_990_000.0,
        is_valuable=True
    ),
    # USDC (USD Coin) - popular stable asset (6,023 incidents in paper)
    "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48": TokenInfo(
        address="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        symbol="USDC",
        name="USD Coin",
        decimals=6,
        total_supply=28_000_000_000.0,
        price_usd=1.0,
        market_cap_usd=28_000_000_000.0,
        is_valuable=True
    ),
    # USDT (Tether USD) - 3,350 incidents in paper
    "0xdac17f958d2ee523a2206206994597c13d831ec7": TokenInfo(
        address="0xdac17f958d2ee523a2206206994597c13d831ec7",
        symbol="USDT",
        name="Tether USD",
        decimals=6,
        total_supply=82_000_000_000.0,
        price_usd=1.0,
        market_cap_usd=82_000_000_000.0,
        is_valuable=True
    ),
    # DAI (Dai Stablecoin) - 3,315 incidents in paper
    "0x6b175474e89094c44da98b954eedeac495271d0f": TokenInfo(
        address="0x6b175474e89094c44da98b954eedeac495271d0f",
        symbol="DAI",
        name="Dai Stablecoin",
        decimals=18,
        total_supply=5_100_000_000.0,
        price_usd=1.0,
        market_cap_usd=5_100_000_000.0,
        is_valuable=True
    ),
    # DEI (Deus Finance stable token manipulated in the $3M attack)
    "0xde12c729e25b6a73380e1370e8567e22e3f33334": TokenInfo(
        address="0xde12c729e25b6a73380e1370e8567e22e3f33334",
        symbol="DEI",
        name="DEI Token",
        decimals=18,
        total_supply=80_000_000.0,
        price_usd=1.0,
        market_cap_usd=80_000_000.0,
        is_valuable=True
    ),
    # SAND (Sandclock audit contest token)
    "0x3845badade8e6dff049820680d1f14bd3903a5d0": TokenInfo(
        address="0x3845badade8e6dff049820680d1f14bd3903a5d0",
        symbol="SAND",
        name="SAND Token",
        decimals=18,
        total_supply=3_000_000_000.0,
        price_usd=0.55,
        market_cap_usd=1_650_000_000.0,
        is_valuable=True
    ),
    # TRACER (Tracer orderbook DEX token)
    "0x9c4a4204b79dd2919b1c0d0d5ecfe84618888987": TokenInfo(
        address="0x9c4a4204b79dd2919b1c0d0d5ecfe84618888987",
        symbol="TCR",
        name="Tracer DAO",
        decimals=18,
        total_supply=1_000_000_000.0,
        price_usd=0.22,
        market_cap_usd=220_000_000.0,
        is_valuable=True
    ),
}

def get_token_registry() -> Dict[str, TokenInfo]:
    return HIGH_VALUE_TOKENS

"""
Unit tests for Stage 3 Multi-Transaction Linking Engine.
"""

import pytest
from poma_detector.models import Trade, ActionType, RiskLevel
from poma_detector.linking import MultiTxLinkingEngine


@pytest.fixture
def linking_engine():
    return MultiTxLinkingEngine(max_block_window=2)


def test_arbitrage_detection(linking_engine):
    t1 = Trade(
        action_type=ActionType.SWAP,
        operator="0xArbBot",
        recipient="0xArbBot",
        pool_address="0xUniswap",
        asset_in="0xUSDC",
        asset_out="0xWETH",
        amount_in=1_000.0,
        amount_out=0.6,
        block_number=100,
        transaction_hash="0xbuy",
        log_index=1
    )

    t2 = Trade(
        action_type=ActionType.SWAP,
        operator="0xArbBot",
        recipient="0xArbBot",
        pool_address="0xSushiswap",
        asset_in="0xWETH",
        asset_out="0xUSDC",
        amount_in=0.6,
        amount_out=1_100.0,
        block_number=100,
        transaction_hash="0xsell",
        log_index=2
    )

    arbs = linking_engine.detect_arbitrage_events([t1, t2])
    assert len(arbs) == 1
    assert arbs[0].profit_amount == 100.0
    assert arbs[0].token == "0xWETH"


def test_poma_alert_correlation(linking_engine):
    pom_trade = Trade(
        action_type=ActionType.SWAP,
        operator="0xAttacker",
        recipient="0xAttacker",
        pool_address="0xUniswap",
        asset_in="0xUSDC",
        asset_out="0xWETH",
        amount_in=500_000.0,
        amount_out=250.0,
        block_number=100,
        transaction_hash="0xpom_tx",
        log_index=1,
        flags=["SEC_ANOMALOUS_TRADE_SIZE"]
    )

    t1 = Trade(
        action_type=ActionType.SWAP,
        operator="0xArbBot",
        recipient="0xArbBot",
        pool_address="0xUniswap",
        asset_in="0xUSDC",
        asset_out="0xWETH",
        amount_in=10_000.0,
        amount_out=6.0,
        block_number=101,
        transaction_hash="0xbuy",
        log_index=1
    )

    t2 = Trade(
        action_type=ActionType.SWAP,
        operator="0xArbBot",
        recipient="0xArbBot",
        pool_address="0xSushiswap",
        asset_in="0xWETH",
        asset_out="0xUSDC",
        amount_in=6.0,
        amount_out=12_000.0,
        block_number=101,
        transaction_hash="0xsell",
        log_index=2
    )

    arbs = linking_engine.detect_arbitrage_events([t1, t2])
    alerts = linking_engine.correlate_manipulation_and_arbitrage([pom_trade], arbs)

    assert len(alerts) == 1
    assert alerts[0].poma_tx_hash == "0xpom_tx"
    assert alerts[0].block_distance == 1
    assert alerts[0].risk_level == RiskLevel.HIGH

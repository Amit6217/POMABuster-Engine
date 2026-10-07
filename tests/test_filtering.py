"""
Unit tests for Stage 2 SEC Filtering Gate.
"""

import pytest
from poma_detector.models import Trade, ActionType
from poma_detector.filtering import SECFilteringGate


@pytest.fixture
def gate():
    return SECFilteringGate(trade_size_threshold_pct=0.05)


def test_trade_size_anomaly(gate):
    large_trade = Trade(
        action_type=ActionType.SWAP,
        operator="0xAttacker",
        recipient="0xAttacker",
        pool_address="0xPool",
        asset_in="0xUSDC",
        asset_out="0xWETH",
        amount_in=100_000.0,
        amount_out=50.0,
        block_number=100,
        transaction_hash="0xtx1",
        log_index=1
    )

    pool_depth = 500_000.0  # 100,000 / 500,000 = 20% > 5% threshold
    assert gate.is_trade_size_anomalous(large_trade, pool_depth) is True

    small_trade = Trade(
        action_type=ActionType.SWAP,
        operator="0xUser",
        recipient="0xUser",
        pool_address="0xPool",
        asset_in="0xUSDC",
        asset_out="0xWETH",
        amount_in=1_000.0,
        amount_out=0.5,
        block_number=100,
        transaction_hash="0xtx2",
        log_index=2
    )

    assert gate.is_trade_size_anomalous(small_trade, pool_depth) is False


def test_wash_round_trip_detection(gate):
    t1 = Trade(
        action_type=ActionType.SWAP,
        operator="0xAttacker",
        recipient="0xAttacker",
        pool_address="0xPool",
        asset_in="0xUSDC",
        asset_out="0xWETH",
        amount_in=10_000.0,
        amount_out=5.0,
        block_number=100,
        transaction_hash="0xtx1",
        log_index=1
    )

    t2 = Trade(
        action_type=ActionType.SWAP,
        operator="0xAttacker",
        recipient="0xAttacker",
        pool_address="0xPool",
        asset_in="0xWETH",
        asset_out="0xUSDC",
        amount_in=5.0,
        amount_out=9_950.0,
        block_number=100,
        transaction_hash="0xtx2",
        log_index=2
    )

    suspicious_hashes = gate.detect_wash_round_trips([t1, t2])
    assert "0xtx1" in suspicious_hashes
    assert "0xtx2" in suspicious_hashes
    assert "SEC_WASH_ROUND_TRIP" in t1.flags

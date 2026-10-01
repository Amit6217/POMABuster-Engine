"""
Unit tests for Stage 1 Semantic Recovery Engine.
"""

import pytest
from poma_detector.models import Log, ActionType
from poma_detector.semantics import SemanticRecoveryEngine


@pytest.fixture
def semantics_engine():
    return SemanticRecoveryEngine()


def test_is_mint_and_burn():
    mint_log = Log(1, "tx1", 1, "0xToken", "0x0", "0xAlice", 100)
    burn_log = Log(1, "tx1", 2, "0xToken", "0xAlice", "0x0", 100)
    normal_log = Log(1, "tx1", 3, "0xToken", "0xAlice", "0xBob", 100)

    assert mint_log.is_mint is True
    assert mint_log.is_burn is False

    assert burn_log.is_burn is True
    assert burn_log.is_mint is False

    assert normal_log.is_normal_transfer is True


def test_swap_recovery(semantics_engine):
    logs = [
        Log(1, "tx1", 1, "0xUSDC", "0xUser", "0xUniswapPool", 1000.0),
        Log(1, "tx1", 2, "0xWETH", "0xUniswapPool", "0xUser", 0.5)
    ]

    trades = semantics_engine.process_transaction(logs)
    assert len(trades) == 1
    trade = trades[0]

    assert trade.action_type == ActionType.SWAP
    assert trade.asset_in == "0xUSDC"
    assert trade.asset_out == "0xWETH"
    assert trade.amount_in == 1000.0
    assert trade.amount_out == 0.5


def test_liquidity_mining_recovery(semantics_engine):
    logs = [
        Log(1, "tx1", 1, "0xUSDC", "0xUser", "0xUniswapPool", 1000.0),
        Log(1, "tx1", 2, "0xUNI-V2", "0x0", "0xUser", 10.0)
    ]

    trades = semantics_engine.process_transaction(logs)
    assert len(trades) == 1
    assert trades[0].action_type == ActionType.LIQUIDITY_MINING
    assert trades[0].asset_out == "0xUNI-V2"

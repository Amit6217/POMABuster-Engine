"""
Curated Ethereum Benchmark Transfer Logs for POMABuster.
Includes:
1. Real-world 3-transaction WBTC/WETH/RenBTC exploit on Curve.fi & Uniswap (2022) - Section 3.1 & 3.5
2. Deus Finance $3M POMA Exploit - Section 1
3. Code4rena Audit Contests (Sandclock same-block mutation, Sandclock cross-block mutation, Tracer Orderbook DEX) - Section 4.2 & Appendix C
4. Wash Sale POMA Exploit - Section 3.2 & Appendix B
5. Benign non-attack transactions (Benign swaps, pure DEX arbitrage, and DeFiRanger False Positive flashloan reward) - Appendix D
"""

from typing import List
from backend.models.schema import TransferLog

def get_benchmark_transfer_logs() -> List[TransferLog]:
    logs: List[TransferLog] = []

    # Common token addresses
    weth = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    wbtc = "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599"
    renbtc = "0xeb4c2781e4eba804ce9a9803c67d0893436bb27d"
    usdc = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    dai = "0x6b175474e89094c44da98b954eedeac495271d0f"
    dei = "0xde12c729e25b6a73380e1370e8567e22e3f33334"
    sand = "0x3845badade8e6dff049820680d1f14bd3903a5d0"
    tcr = "0x9c4a4204b79dd2919b1c0d0d5ecfe84618888987"

    # =========================================================================
    # 0. Canonical Single-Transaction Atomic POMA (Supported by DeFiRanger)
    # Serves as the single-transaction baseline (n = -1) per Section 4.5
    # =========================================================================
    atomic_tx = "0x111111000e123456789abcdef0123456789abcdef0123456789abcdef012345"
    atomic_attacker = "0x11111199ab12cd45ef67890123456789abcdef11"
    atomic_pool = "0x10101010109f242643a7008926938c03e9d99999"
    atomic_victim = "0x20202020209f242643a7008926938c03e9d99999"

    # Step 1 (POM): Skew WBTC in pool with 1,200 WETH
    logs.append(TransferLog(
        tx_hash=atomic_tx, block_number=15100000, log_index=0,
        sender=atomic_attacker, receiver=atomic_pool,
        token_address=weth, token_symbol="WETH", amount=1200.0, timestamp=1658000000
    ))
    logs.append(TransferLog(
        tx_hash=atomic_tx, block_number=15100000, log_index=1,
        sender=atomic_pool, receiver=atomic_attacker,
        token_address=wbtc, token_symbol="WBTC", amount=92.5, timestamp=1658000000
    ))
    # Step 2 (Arbitrage in same tx): Swap 92.5 WBTC -> 1207.2 WETH (+7.2 WETH profit)
    logs.append(TransferLog(
        tx_hash=atomic_tx, block_number=15100000, log_index=2,
        sender=atomic_attacker, receiver=atomic_victim,
        token_address=wbtc, token_symbol="WBTC", amount=92.5, timestamp=1658000000
    ))
    logs.append(TransferLog(
        tx_hash=atomic_tx, block_number=15100000, log_index=3,
        sender=atomic_victim, receiver=atomic_attacker,
        token_address=weth, token_symbol="WETH", amount=1207.2, timestamp=1658000000
    ))

    # =========================================================================
    # 1. Real-World WBTC 3-Transaction Exploit (Curve.fi + Uniswap, 2022)
    # Described in Section 3.1 & Section 3.5 & Figure 2
    # =========================================================================
    
    # --- Transaction 1: POM (Market Domination) by Trader 1 ---
    # Tx Hash: 0xbe703f0e1e8b7fee37e22a5acb413ce13270611dc7c03e9f9885d55aea30553c
    # Trader 1 swaps 1,049.9 WETH for 81.39 WBTC on Curve.fi
    # WBTC total supply = 155,000 -> 81.39 / 155,000 = 0.0525% >= 0.01% sigma!
    tx1_hash = "0xbe703f0e1e8b7fee37e22a5acb413ce13270611dc7c03e9f9885d55aea30553c"
    trader1 = "0x11111171a5e9ef37f66d700ee06b0bba35a73a11"
    curve_wbtc_weth = "0xc3d688b66703497daa19211eedff47f25384cdc3"

    logs.append(TransferLog(
        tx_hash=tx1_hash, block_number=15300120, log_index=0,
        sender=trader1, receiver=curve_wbtc_weth,
        token_address=weth, token_symbol="WETH", amount=1049.9, timestamp=1660000000
    ))
    logs.append(TransferLog(
        tx_hash=tx1_hash, block_number=15300120, log_index=1,
        sender=curve_wbtc_weth, receiver=trader1,
        token_address=wbtc, token_symbol="WBTC", amount=81.39, timestamp=1660000000
    ))

    # --- Transaction 2: Arbitrage by Trader 2 (Multi-transaction via Flashbots, Same Block!) ---
    # Tx Hash: 0x0f1758027c2e65699897d22cdfee171e0e33a80b186e460f14d594ba143846b0
    # Trader 2 sells 61.7 RenBTC for 796.7 WETH, routing through Uniswap & Curve
    # Net profit: 5.03 WETH, with intermediate token WBTC!
    tx2_hash = "0x0f1758027c2e65699897d22cdfee171e0e33a80b186e460f14d594ba143846b0"
    trader2 = "0x22222289ab12cd45ef67890123456789abcdef01"
    uniswap_weth_wbtc = "0x00cef44b9a9f242643a7008926938c03e9d99999"
    curve_renbtc_wbtc = "0x7b65b69c47e8ab0634149fa8d18356f913d88888"
    victim_derivative = "0x888888889a9f242643a7008926938c03e9d99999"

    # Hop 1: 796.7 WETH -> 61.9 WBTC (Uniswap)
    logs.append(TransferLog(
        tx_hash=tx2_hash, block_number=15300120, log_index=0,
        sender=trader2, receiver=uniswap_weth_wbtc,
        token_address=weth, token_symbol="WETH", amount=796.7, timestamp=1660000000
    ))
    logs.append(TransferLog(
        tx_hash=tx2_hash, block_number=15300120, log_index=1,
        sender=uniswap_weth_wbtc, receiver=trader2,
        token_address=wbtc, token_symbol="WBTC", amount=61.9, timestamp=1660000000
    ))
    # Hop 2: 61.7 WBTC -> 61.6 RenBTC (Curve)
    logs.append(TransferLog(
        tx_hash=tx2_hash, block_number=15300120, log_index=2,
        sender=trader2, receiver=curve_renbtc_wbtc,
        token_address=wbtc, token_symbol="WBTC", amount=61.7, timestamp=1660000000
    ))
    logs.append(TransferLog(
        tx_hash=tx2_hash, block_number=15300120, log_index=3,
        sender=curve_renbtc_wbtc, receiver=trader2,
        token_address=renbtc, token_symbol="RenBTC", amount=61.6, timestamp=1660000000
    ))
    # Hop 3: 61.6 RenBTC -> 801.73 WETH (Victim Derivative)
    # Net profit: 801.73 - 796.7 = +5.03 WETH
    logs.append(TransferLog(
        tx_hash=tx2_hash, block_number=15300120, log_index=4,
        sender=trader2, receiver=victim_derivative,
        token_address=renbtc, token_symbol="RenBTC", amount=61.6, timestamp=1660000000
    ))
    logs.append(TransferLog(
        tx_hash=tx2_hash, block_number=15300120, log_index=5,
        sender=victim_derivative, receiver=trader2,
        token_address=weth, token_symbol="WETH", amount=801.73, timestamp=1660000000
    ))

    # --- Transaction 3: Reversal / Benign trade by Trader 1 ---
    # Tx Hash: 0x22016bcf480bb296d07e27557451a02fa27657810a8be584a10293887ef999db
    # Trader 1 sells 81.39 WBTC back to Curve for 1,054.9 WETH to cancel disparity
    # Marked as benign by POMABuster because no arbitrage follows!
    tx3_hash = "0x22016bcf480bb296d07e27557451a02fa27657810a8be584a10293887ef999db"
    logs.append(TransferLog(
        tx_hash=tx3_hash, block_number=15300120, log_index=0,
        sender=trader1, receiver=curve_wbtc_weth,
        token_address=wbtc, token_symbol="WBTC", amount=81.39, timestamp=1660000000
    ))
    logs.append(TransferLog(
        tx_hash=tx3_hash, block_number=15300120, log_index=1,
        sender=curve_wbtc_weth, receiver=trader1,
        token_address=weth, token_symbol="WETH", amount=1054.9, timestamp=1660000000
    ))

    # =========================================================================
    # 2. Deus Finance $3M POMA Exploit (Consecutive Blocks, n = 1)
    # Section 1 of the paper
    # =========================================================================
    deus_tx1 = "0xde05fa110e123456789abcdef0123456789abcdef0123456789abcdef012345"
    deus_tx2 = "0xde05fa120e123456789abcdef0123456789abcdef0123456789abcdef012346"
    deus_attacker = "0x33333399ab12cd45ef67890123456789abcdef33"
    deus_pool = "0x999999999a9f242643a7008926938c03e9d99999"
    deus_lending = "0xaaaaaaaaaa9f242643a7008926938c03e9d99999"
    deus_sec_dex = "0x91919191919f242643a7008926938c03e9d99999"

    # Tx 1: Block 14682410 - Attacker sells 15,000,000 DEI for USDC (18.75% of DEI supply!)
    logs.append(TransferLog(
        tx_hash=deus_tx1, block_number=14682410, log_index=0,
        sender=deus_attacker, receiver=deus_pool,
        token_address=dei, token_symbol="DEI", amount=15000000.0, timestamp=1651000000
    ))
    logs.append(TransferLog(
        tx_hash=deus_tx1, block_number=14682410, log_index=1,
        sender=deus_pool, receiver=deus_attacker,
        token_address=usdc, token_symbol="USDC", amount=14200000.0, timestamp=1651000000
    ))

    # Tx 2: Block 14682411 (Block distance n = 1) - Arbitrageur swaps USDC -> DEI -> liquidates lending for USDC
    # Hop 1: 5,000,000 USDC -> 5,000,000 DEI
    logs.append(TransferLog(
        tx_hash=deus_tx2, block_number=14682411, log_index=0,
        sender=deus_attacker, receiver=deus_sec_dex,
        token_address=usdc, token_symbol="USDC", amount=5000000.0, timestamp=1651000012
    ))
    logs.append(TransferLog(
        tx_hash=deus_tx2, block_number=14682411, log_index=1,
        sender=deus_sec_dex, receiver=deus_attacker,
        token_address=dei, token_symbol="DEI", amount=5000000.0, timestamp=1651000012
    ))
    # Hop 2: 5,000,000 DEI -> 8,150,000 USDC from victim lending
    # Net profit: +3,150,000 USDC
    logs.append(TransferLog(
        tx_hash=deus_tx2, block_number=14682411, log_index=2,
        sender=deus_attacker, receiver=deus_lending,
        token_address=dei, token_symbol="DEI", amount=5000000.0, timestamp=1651000012
    ))
    logs.append(TransferLog(
        tx_hash=deus_tx2, block_number=14682411, log_index=3,
        sender=deus_lending, receiver=deus_attacker,
        token_address=usdc, token_symbol="USDC", amount=8150000.0, timestamp=1651000012
    ))

    # =========================================================================
    # 3. Code4rena Benchmark Cases (Sandclock & Tracer)
    # Section 4.2 & Appendix C
    # =========================================================================
    
    # --- Sandclock Mutation 1: Same Block Flashbots Bundle (n = 0) ---
    sand_tx1 = "0x555555110e123456789abcdef0123456789abcdef0123456789abcdef012345"
    sand_tx2 = "0x555555220e123456789abcdef0123456789abcdef0123456789abcdef012346"
    sand_attacker1 = "0x44444499ab12cd45ef67890123456789abcdef44"
    sand_attacker2 = "0x55555599ab12cd45ef67890123456789abcdef55"
    sand_pool = "0xbbbbbbbbbb9f242643a7008926938c03e9d99999"
    sand_sec_pool = "0xb2b2b2b2b29f242643a7008926938c03e9d99999"
    sand_vault = "0xcccccccccc9f242643a7008926938c03e9d99999"

    # Step 1: Pump SAND token in pool (3,500,000 SAND, 0.116% of supply)
    logs.append(TransferLog(
        tx_hash=sand_tx1, block_number=16100100, log_index=0,
        sender=sand_attacker1, receiver=sand_pool,
        token_address=weth, token_symbol="WETH", amount=500.0, timestamp=1672000000
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx1, block_number=16100100, log_index=1,
        sender=sand_pool, receiver=sand_attacker1,
        token_address=sand, token_symbol="SAND", amount=3500000.0, timestamp=1672000000
    ))
    # Step 2: Arbitrage in same block: 500 WETH -> 3,400,000 SAND -> 518.5 WETH (+18.5 WETH profit)
    logs.append(TransferLog(
        tx_hash=sand_tx2, block_number=16100100, log_index=0,
        sender=sand_attacker2, receiver=sand_sec_pool,
        token_address=weth, token_symbol="WETH", amount=500.0, timestamp=1672000000
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx2, block_number=16100100, log_index=1,
        sender=sand_sec_pool, receiver=sand_attacker2,
        token_address=sand, token_symbol="SAND", amount=3400000.0, timestamp=1672000000
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx2, block_number=16100100, log_index=2,
        sender=sand_attacker2, receiver=sand_vault,
        token_address=sand, token_symbol="SAND", amount=3400000.0, timestamp=1672000000
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx2, block_number=16100100, log_index=3,
        sender=sand_vault, receiver=sand_attacker2,
        token_address=weth, token_symbol="WETH", amount=518.5, timestamp=1672000000
    ))

    # --- Sandclock Mutation 2: Consecutive Blocks (n = 2) ---
    sand_tx3 = "0x555555330e123456789abcdef0123456789abcdef0123456789abcdef012347"
    sand_tx4 = "0x555555440e123456789abcdef0123456789abcdef0123456789abcdef012348"
    logs.append(TransferLog(
        tx_hash=sand_tx3, block_number=16100200, log_index=0,
        sender=sand_attacker1, receiver=sand_pool,
        token_address=weth, token_symbol="WETH", amount=450.0, timestamp=1672001000
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx3, block_number=16100200, log_index=1,
        sender=sand_pool, receiver=sand_attacker1,
        token_address=sand, token_symbol="SAND", amount=3100000.0, timestamp=1672001000
    ))
    # Arbitrage in block + 2: 450 WETH -> 3,050,000 SAND -> 464.2 WETH (+14.2 WETH profit)
    logs.append(TransferLog(
        tx_hash=sand_tx4, block_number=16100202, log_index=0,
        sender=sand_attacker2, receiver=sand_sec_pool,
        token_address=weth, token_symbol="WETH", amount=450.0, timestamp=1672001024
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx4, block_number=16100202, log_index=1,
        sender=sand_sec_pool, receiver=sand_attacker2,
        token_address=sand, token_symbol="SAND", amount=3050000.0, timestamp=1672001024
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx4, block_number=16100202, log_index=2,
        sender=sand_attacker2, receiver=sand_vault,
        token_address=sand, token_symbol="SAND", amount=3050000.0, timestamp=1672001024
    ))
    logs.append(TransferLog(
        tx_hash=sand_tx4, block_number=16100202, log_index=3,
        sender=sand_vault, receiver=sand_attacker2,
        token_address=weth, token_symbol="WETH", amount=464.2, timestamp=1672001024
    ))

    # --- Tracer Orderbook DEX Exploit (Appendix D, missed by DeFiRanger) ---
    tracer_tx1 = "0x666666110e123456789abcdef0123456789abcdef0123456789abcdef012345"
    tracer_tx2 = "0x666666220e123456789abcdef0123456789abcdef0123456789abcdef012346"
    tcr_user1 = "0x66666699ab12cd45ef67890123456789abcdef66"
    tcr_user2 = "0x77777799ab12cd45ef67890123456789abcdef77"
    tracer_orderbook = "0xdddddddddd9f242643a7008926938c03e9d99999"
    tracer_sec_dex = "0xd3d3d3d3d39f242643a7008926938c03e9d99999"

    # Counterparty trade between user a1 and a2 skewing Tracer oracle
    logs.append(TransferLog(
        tx_hash=tracer_tx1, block_number=16200050, log_index=0,
        sender=tcr_user1, receiver=tracer_orderbook,
        token_address=weth, token_symbol="WETH", amount=250.0, timestamp=1673000000
    ))
    logs.append(TransferLog(
        tx_hash=tracer_tx1, block_number=16200050, log_index=1,
        sender=tracer_orderbook, receiver=tcr_user2,
        token_address=tcr, token_symbol="TCR", amount=1200000.0, timestamp=1673000000
    ))
    # Arbitrage trade: 250 WETH -> 1,190,000 TCR -> 258.4 WETH (+8.4 WETH profit)
    logs.append(TransferLog(
        tx_hash=tracer_tx2, block_number=16200050, log_index=0,
        sender=tcr_user2, receiver=tracer_sec_dex,
        token_address=weth, token_symbol="WETH", amount=250.0, timestamp=1673000000
    ))
    logs.append(TransferLog(
        tx_hash=tracer_tx2, block_number=16200050, log_index=1,
        sender=tracer_sec_dex, receiver=tcr_user2,
        token_address=tcr, token_symbol="TCR", amount=1190000.0, timestamp=1673000000
    ))
    logs.append(TransferLog(
        tx_hash=tracer_tx2, block_number=16200050, log_index=2,
        sender=tcr_user2, receiver=tracer_orderbook,
        token_address=tcr, token_symbol="TCR", amount=1190000.0, timestamp=1673000000
    ))
    logs.append(TransferLog(
        tx_hash=tracer_tx2, block_number=16200050, log_index=3,
        sender=tracer_orderbook, receiver=tcr_user2,
        token_address=weth, token_symbol="WETH", amount=258.4, timestamp=1673000000
    ))

    # =========================================================================
    # 4. Wash Sale POMA Attack (Section 3.2, Table 3 & Eq. 5)
    # =========================================================================
    wash_tx1 = "0x777777110e123456789abcdef0123456789abcdef0123456789abcdef012345"
    wash_tx2 = "0x777777220e123456789abcdef0123456789abcdef0123456789abcdef012346"
    wash_trader = "0x88888899ab12cd45ef67890123456789abcdef88"
    wash_pool_a = "0xeeeeeeeeee9f242643a7008926938c03e9d99999"
    wash_pool_b = "0xffffffffff9f242643a7008926938c03e9d99999"
    wash_sec_pool = "0xf5f5f5f5f59f242643a7008926938c03e9d99999"
    lending_wash = "0x12121212129f242643a7008926938c03e9d99999"

    # In Tx 1: Trader rapidly churns WETH and WBTC back and forth (wash sale volume pumping)
    # 380 WETH -> 27.2 WBTC, then 27.2 WBTC -> 380 WETH (churned volume = 760 WETH)
    logs.append(TransferLog(
        tx_hash=wash_tx1, block_number=16300010, log_index=0,
        sender=wash_trader, receiver=wash_pool_a,
        token_address=weth, token_symbol="WETH", amount=380.0, timestamp=1674000000
    ))
    logs.append(TransferLog(
        tx_hash=wash_tx1, block_number=16300010, log_index=1,
        sender=wash_pool_a, receiver=wash_trader,
        token_address=wbtc, token_symbol="WBTC", amount=27.2, timestamp=1674000000
    ))
    logs.append(TransferLog(
        tx_hash=wash_tx1, block_number=16300010, log_index=2,
        sender=wash_trader, receiver=wash_pool_b,
        token_address=wbtc, token_symbol="WBTC", amount=27.2, timestamp=1674000000
    ))
    logs.append(TransferLog(
        tx_hash=wash_tx1, block_number=16300010, log_index=3,
        sender=wash_pool_b, receiver=wash_trader,
        token_address=weth, token_symbol="WETH", amount=380.0, timestamp=1674000000
    ))

    # Tx 2: In block 16300011 (consecutive block n = 1), extracts profit via secondary lending protocol
    # Hop 1: 200 WETH -> 15 WBTC on secondary pool
    logs.append(TransferLog(
        tx_hash=wash_tx2, block_number=16300011, log_index=0,
        sender=wash_trader, receiver=wash_sec_pool,
        token_address=weth, token_symbol="WETH", amount=200.0, timestamp=1674000012
    ))
    logs.append(TransferLog(
        tx_hash=wash_tx2, block_number=16300011, log_index=1,
        sender=wash_sec_pool, receiver=wash_trader,
        token_address=wbtc, token_symbol="WBTC", amount=15.0, timestamp=1674000012
    ))
    # Hop 2: 15 WBTC -> 221.8 WETH from lending protocol (+21.8 WETH profit)
    logs.append(TransferLog(
        tx_hash=wash_tx2, block_number=16300011, log_index=2,
        sender=wash_trader, receiver=lending_wash,
        token_address=wbtc, token_symbol="WBTC", amount=15.0, timestamp=1674000012
    ))
    logs.append(TransferLog(
        tx_hash=wash_tx2, block_number=16300011, log_index=3,
        sender=lending_wash, receiver=wash_trader,
        token_address=weth, token_symbol="WETH", amount=221.8, timestamp=1674000012
    ))

    # =========================================================================
    # 5. Benign Non-Attack Transactions (Verified Negative Controls)
    # =========================================================================
    
    # --- Benign Case 1: Normal DEX Swap (Under threshold sigma) ---
    normal_tx = "0x888888000e123456789abcdef0123456789abcdef0123456789abcdef012345"
    normal_user = "0x99999999ab12cd45ef67890123456789abcdef99"
    uni_usdc_pool = "0x7bea39867e4169dbe237d55c8242a8f2fcdcc387"
    # 15 WETH is well below sigma = 0.01% of 3,250,000 supply (325 WETH)
    logs.append(TransferLog(
        tx_hash=normal_tx, block_number=16400000, log_index=0,
        sender=normal_user, receiver=uni_usdc_pool,
        token_address=weth, token_symbol="WETH", amount=15.0, timestamp=1675000000
    ))
    logs.append(TransferLog(
        tx_hash=normal_tx, block_number=16400000, log_index=1,
        sender=uni_usdc_pool, receiver=normal_user,
        token_address=usdc, token_symbol="USDC", amount=30600.0, timestamp=1675000000
    ))

    # --- Benign Case 2: Pure Triangular Arbitrage without Oracle Manipulation ---
    pure_arb_tx = "0x999999000e123456789abcdef0123456789abcdef0123456789abcdef012345"
    arb_bot = "0xaaaaaa99ab12cd45ef67890123456789abcdefaa"
    sushi_pool = "0x333333333a9f242643a7008926938c03e9d99999"
    # Routine benign triangular arbitrage: 5 WETH -> DAI -> USDC -> 5.08 WETH (+0.08 WETH profit)
    # No POM manipulation occurred before this trade!
    logs.append(TransferLog(
        tx_hash=pure_arb_tx, block_number=16400100, log_index=0,
        sender=arb_bot, receiver=sushi_pool,
        token_address=weth, token_symbol="WETH", amount=5.0, timestamp=1675001000
    ))
    logs.append(TransferLog(
        tx_hash=pure_arb_tx, block_number=16400100, log_index=1,
        sender=sushi_pool, receiver=arb_bot,
        token_address=dai, token_symbol="DAI", amount=10200.0, timestamp=1675001000
    ))
    logs.append(TransferLog(
        tx_hash=pure_arb_tx, block_number=16400100, log_index=2,
        sender=arb_bot, receiver=uni_usdc_pool,
        token_address=dai, token_symbol="DAI", amount=10200.0, timestamp=1675001000
    ))
    logs.append(TransferLog(
        tx_hash=pure_arb_tx, block_number=16400100, log_index=3,
        sender=uni_usdc_pool, receiver=arb_bot,
        token_address=weth, token_symbol="WETH", amount=5.08, timestamp=1675001000
    ))

    # --- Benign Case 3: Flashloan Platform Reward (Appendix D - DeFiRanger False Positive!) ---
    # In Appendix D, DeFiRanger misclassifies this as a POMA because of borrowing + repaying.
    # POMABuster correctly recognizes that this does NOT manipulate any price oracle!
    fl_tx = "0xaaaaaa000e123456789abcdef0123456789abcdef0123456789abcdef012345"
    fl_user = "0xbbbbbb99ab12cd45ef67890123456789abcdefbb"
    lending_reward_pool = "0x444444444a9f242643a7008926938c03e9d99999"
    logs.append(TransferLog(
        tx_hash=fl_tx, block_number=16400200, log_index=0,
        sender=lending_reward_pool, receiver=fl_user,
        token_address=usdc, token_symbol="USDC", amount=10000.0, timestamp=1675002000
    ))
    logs.append(TransferLog(
        tx_hash=fl_tx, block_number=16400200, log_index=1,
        sender=fl_user, receiver=lending_reward_pool,
        token_address=usdc, token_symbol="USDC", amount=10000.0, timestamp=1675002000
    ))

    return logs

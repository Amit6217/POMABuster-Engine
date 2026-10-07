import unittest
from core.models import Log, Trade
from core.trade_reconstructor import TradeReconstructor
from detectors.market_domination import MarketDominationDetector
from engine.linker import AttackLinker

class TestPOMABuster(unittest.TestCase):
    
    def setUp(self):
        self.logs = [
            Log(1000, "tx1", 0, "WBTC", "attacker", "pool1", 50000),
            Log(1000, "tx1", 1, "WETH", "pool1", "attacker", 1000000)
        ]
        self.supplies = {"WBTC": 150000, "WETH": 100000000}
        
    def test_trade_reconstruction(self):
        trades = TradeReconstructor.extract_trades(self.logs)
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].asset_in, "WBTC")
        self.assertEqual(trades[0].asset_out, "WETH")
        
    def test_market_domination(self):
        trades = TradeReconstructor.extract_trades(self.logs)
        detector = MarketDominationDetector(self.supplies, threshold=0.0001)
        pom_trades = detector.detect(trades)
        
        self.assertEqual(len(pom_trades), 1)
        self.assertEqual(pom_trades[0].transaction_hash, "tx1")
        
    def test_linking(self):
        # Create mock trades
        pom_trade = Trade(1000, "tx1", "att", "pool", "pool", "WBTC", "WETH", 50000, 1000000, [0, 1])
        arb_trade1 = Trade(1001, "tx2", "att2", "p2", "p2", "WETH", "USDC", 500, 1000000, [0,1])
        arb_trade2 = Trade(1001, "tx2", "att2", "p3", "p3", "USDC", "WETH", 1000000, 550, [2,3])
        
        # Link
        links = AttackLinker.link_attacks([pom_trade], [[arb_trade1, arb_trade2]], max_block_span=2)
        
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0]["pom_tx"], "tx1")
        self.assertEqual(links[0]["arb_tx"], "tx2")
        self.assertEqual(links[0]["block_span"], 1)

if __name__ == "__main__":
    unittest.main()

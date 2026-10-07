import os
from utils.data_loader import DataLoader
from core.trade_reconstructor import TradeReconstructor
from detectors.market_domination import MarketDominationDetector
from detectors.arbitrage import ArbitrageDetector
from engine.linker import AttackLinker

def main():
    print("Initializing POMABuster Engine...")
    
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    logs_path = os.path.join(data_dir, "test_data.json")
    supplies_path = os.path.join(data_dir, "token_supplies.json")
    
    # 1. Load Data
    logs = DataLoader.load_logs(logs_path)
    token_supplies = DataLoader.load_token_supplies(supplies_path)
    print(f"[+] Loaded {len(logs)} transfer logs.")
    
    # 2. Reconstruct Trades
    trades = TradeReconstructor.extract_trades(logs)
    print(f"[+] Reconstructed {len(trades)} logical trades.")
    
    # 3. Detect POM
    pom_detector = MarketDominationDetector(token_supplies, threshold=0.0001)
    pom_trades = pom_detector.detect(trades)
    print(f"[+] Detected {len(pom_trades)} Price Oracle Manipulation (POM) trades.")
    
    # 4. Detect Arbitrage
    arbitrages = ArbitrageDetector.detect(trades)
    print(f"[+] Detected {len(arbitrages)} Arbitrage transactions.")
    
    # 5. Link Attacks
    attacks = AttackLinker.link_attacks(pom_trades, arbitrages, max_block_span=2)
    
    print("\n================ FINAL REPORT ================")
    if attacks:
        print(f"Successfully detected {len(attacks)} complete POMA(s)!")
        for i, attack in enumerate(attacks):
            print(f"  [{i+1}] POM Tx: {attack['pom_tx']} | Arb Tx: {attack['arb_tx']} | Block Span: {attack['block_span']}")
    else:
        print("No complete POMAs detected.")
    print("==============================================")

if __name__ == "__main__":
    main()

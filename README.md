# POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance

[![Paper](https://img.shields.io/badge/IEEE%20S%26P-2024-rose.svg)](https://doi.org/10.1109/SP54263.2024.00182)
[![Backend](https://img.shields.io/badge/FastAPI-Python%203.11%2B-blue.svg)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/React-19%20%2B%20Tailwind%20CSS-teal.svg)](https://react.dev/)
[![Tests](https://img.shields.io/badge/Tests-10%2F10%20Passing-brightgreen.svg)]()

A complete, production-grade recreation of the research paper:
> **"POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance"**  
> *Rui Xi, Zehua Wang, Karthik Pattabiraman*  
> **2024 IEEE Symposium on Security and Privacy (SP)**, San Francisco, CA, USA  
> DOI: [10.1109/SP54263.2024.00182](https://doi.org/10.1109/SP54263.2024.00182)

---

## 1. Overview & Key Insights

Price Oracle Manipulation Attacks (POMAs) constitute over **15% of all DeFi protocol attacks**, resulting in billions in financial losses. A POMA is a protocol-layer exploit that does not exploit smart contract code bugs, but rather manipulates on-chain spot price oracles (such as AMM liquidity pools):
1. **Price Oracle Manipulation (POM):** The attacker executes massive trades in a DEX pool to artificially tilt the spot price ratio.
2. **Arbitrage Execution:** The attacker (or collaborating bot) exploits a victim protocol (lending platform, derivative platform, or secondary DEX) referencing the skewed pool, extracting profit through an arbitrage loop.

### Key Discoveries from the Research Paper
- **Multi-Transaction Dominance:** Prior state-of-the-art tools (e.g., DeFiRanger) assumed the entire attack occurs atomically within a single transaction. With the advent of **Flashbots** transaction bundles, **over 74% of POMAs are split across multiple transactions** (separate POM transaction and Arbitrage transaction). Single-transaction detectors have a **74.1% False Negative Rate (FNR)**.
- **Time Proximity:** Attackers execute the arbitrage transaction within a very tight time window—**98.7% of all multi-transaction POMAs occur within $n \le 2$ blocks** (92.1% in the same block via Flashbots bundles, 2.5% in the next block).
- **First-Principles Rules from SEC Policies:** Adapts SEC stock market manipulation definitions to the DeFi ecosystem:
  - **Market Domination ($T^{DOM}$):** Trading volume exceeding a fraction $\sigma$ of the token's circulating total supply $\sup(k)$.
  - **Wash Sales ($T^{WASH}$):** Repeatedly churning tokens within a transaction to artificially inflate trading volume beyond $\sigma \times \sup(k)$.
- **Accuracy:** POMABuster achieves a worst-case **False Positive Rate (FPR) of 0.95%** (vs DeFiRanger's 28.58%) and **0% False Negative Rate (FNR)**.

---

## 2. Mathematical Algorithms Implemented

### Algorithm 1: Reconstructing Trades from Transfer Logs (Definition 1)
Given ERC-20 transfer logs $\mathcal{L}$, two logs $(l_1, l_2)$ in the same transaction form a trade $t \sim (l_1, l_2)$ if and only if:
$$\text{addr}(r(l_1)) = \text{addr}(s(l_2)) \quad \text{and} \quad \text{addr}(k(l_1)) \neq \text{addr}(k(l_2))$$
where $r(l_1) = s(l_2) = p(t)$ is the liquidity pool (AMM) or counterparty (orderbook DEX), $s(l_1)$ is the trader operator, and $r(l_2)$ is the recipient.

### Algorithm 2: Market Domination Detection (Definition 3)
A trade $t \in T$ is a market domination trade if:
$$m_{in}(t) \ge \sigma \times \sup(\text{addr}(k_{in}(t))) \quad \text{or} \quad m_{out}(t) \ge \sigma \times \sup(\text{addr}(k_{out}(t)))$$
Default empirical optimal threshold: $\sigma = 0.01\%$ ($0.0001$).

### Algorithm 2: Wash Sale Detection (Definition 5)
Detects artificial volume inflation through circular or churn trading across trades in transaction $T$:
$$\sum_{t \in T} m_{in}(t) \ge \tilde{\sigma} \times \sup(\text{addr}(k_{in}(t))) \quad \text{or} \quad \sum_{t \in T} m_{out}(t) \ge \tilde{\sigma} \times \sup(\text{addr}(k_{out}(t)))$$

### Arbitrage Detection (Definition 6)
An arbitrage trade $T^{ARB}$ is a vector of trades $(t_0, t_1, \dots, t_{N-1})$ where:
1. $k_{out}(t_{j-1}) = k_{in}(t_j)$ for all $j \in \{1, \dots, N-1\}$ (chained transfer loop).
2. Non-negative outcome across all tokens ($\Delta_k \ge 0$).
3. Strictly positive net economic profit ($\sum \Delta > 0$).

### Multi-Transaction POMA Linking (Definition 7)
A complete POMA is identified when:
1. A POM trade $T^{POM} \in T^{DOM} \cup T^{WASH}$ and an arbitrage $T^{ARB}$ occur within block time window $n \in [-1, 2]$.
2. Non-empty intersection between manipulated tokens and arbitrage intermediate tokens:
   $$K^{MANI} \cap K^{INTR} \neq \emptyset$$
3. Arbitrage profit is extracted in an asset distinct from the manipulated token.

---

## 3. Project Architecture

```
POMABuster/
├── backend/
│   ├── config.py                 # Configuration (sigma, n, strike_pct, min_market_cap)
│   ├── models/
│   │   ├── schema.py             # Pydantic models (TransferLog, Trade, Incident, Stats)
│   │   └── database.py           # SQLite storage layer & query helpers
│   ├── engine/
│   │   ├── trade_reconstructor.py# Algorithm 1: Reconstruct trades from logs
│   │   ├── pom_detector.py       # Algorithm 2: Market Domination & Wash Sale
│   │   ├── arbitrage_detector.py # Definition 6: Swap loop, net deltas & profit
│   │   ├── poma_linker.py        # Definition 7: Multi-tx cross-block linker
│   │   └── pipeline.py           # End-to-end detection orchestrator
│   ├── data_loader/
│   │   ├── token_registry.py     # High-value ERC-20 token directory & total supplies
│   │   └── benchmark_data.py     # Real-world exploit logs & benign controls
│   └── api/
│       ├── routes.py             # REST endpoints (health, detect, incidents, config)
│       └── server.py             # FastAPI app with SPA static mount
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.tsx        # Top navigation, status indicator & trigger buttons
│   │   │   ├── KPICards.tsx      # Top metric cards (attacks, multi-tx %, profit)
│   │   │   ├── ConfigPanel.tsx   # Interactive slider controls for sigma and window n
│   │   │   ├── AttackTable.tsx   # Filterable incident list with deep-trace buttons
│   │   │   ├── AttackDetailModal.tsx # Visual attack flowchart & "Why Flagged" breakdown
│   │   │   ├── AnalyticsCharts.tsx   # Recharts reproducing paper figures & tables
│   │   │   ├── TradesTable.tsx   # Browse reconstructed trades and raw transfer logs
│   │   │   └── TokenList.tsx     # High-value token tracker & threshold calculations
│   │   ├── App.tsx               # Main full-stack coordinator
│   │   └── main.tsx              # React DOM entry
│   ├── dist/                     # Pre-built production bundle
│   └── package.json
├── tests/
│   ├── test_detection_engine.py  # Unit tests for Algorithms 1 & 2, Def 6 & 7
│   └── test_api.py               # REST API integration tests
├── run.py                        # Unified CLI runner script
└── requirements.txt              # Backend dependencies
```

---

## 4. Quick Start & Local Execution

### Prerequisites
- Python 3.10+ (Python 3.11 - 3.14 recommended)
- Node.js 18+ and npm (only needed if modifying frontend; pre-built bundle is included!)

### Step 1: Set Up Python Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Verification Test Suite
Verify that all mathematical algorithms and paper benchmarks pass:
```bash
python run.py --test
```
*Expected result: 10/10 tests pass in ~1 second.*

### Step 3: Launch Full-Stack Application
```bash
python run.py
```
Open your browser and navigate to:
- **Interactive Dashboard:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **REST API Documentation (Swagger):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Engine Health Endpoint:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

---

## 5. Included Real-World Datasets

The project includes canonical real-world benchmark datasets to allow testing without needing a 12TB Ethereum archive node:

1. **The 2022 Curve.fi + Uniswap WBTC Exploit (Section 3.1 & 3.5 & Figure 2):**
   - **Tx 1 (POM / Market Domination):** Trader 1 swaps 1,049.9 WETH for 81.39 WBTC on Curve.fi pool ($0.0525\% \ge 0.01\%$ total supply). WBTC spot price is skewed.
   - **Tx 2 (Arbitrage via Flashbots Bundle, Same Block):** Trader 2 routes 796.7 WETH $\rightarrow$ 61.9 WBTC $\rightarrow$ 61.6 RenBTC $\rightarrow$ 801.73 WETH on victim venue, netting **+5.03 WETH profit** (~$10,264 USD).
   - **Tx 3 (Benign Reversal):** Trader 1 sells 81.39 WBTC back to Curve for 1,054.9 WETH to cancel disparity. Correctly marked benign because no subsequent arbitrage exploits it.
2. **Deus Finance Exploit ($3.1M Losses, Section 1):**
   - Tx 1: Attacker dumps 15,000,000 DEI in Solidly/Uniswap pool (18.75% of supply!).
   - Tx 2: Attacker liquidates lending market in consecutive block ($n=1$), capturing **+$3,150,000 USDC**.
3. **Code4rena Benchmark Mutations (Sandclock & Tracer, Section 4.2 & Appendix C):**
   - Sandclock Mutation 1 (Same-block Flashbots bundle, $n=0$): Pump SAND in pool, withdraw from vault (+18.5 WETH profit).
   - Sandclock Mutation 2 (Consecutive blocks, $n=2$): Pump in block $B$, withdraw in block $B+2$ (+14.2 WETH profit).
   - Tracer Orderbook DEX Exploit (Appendix D): Exploits orderbook DEX peer-to-peer trade; missed by DeFiRanger, captured by POMABuster.
4. **Wash Sale POMA Exploit (Section 3.2 & Table 3):**
   - Circular churn trade pumping WETH volume, followed by secondary liquidation in block $n=1$ (+21.8 WETH profit).
5. **Benign Non-Attack Controls (FPR $\le 0.95\%$ Verification):**
   - Large routine swap below $\sigma$.
   - Standalone triangular arbitrage with no preceding oracle manipulation.
   - Flashloan lending reward (the classic DeFiRanger false positive from Appendix D).

---

## 6. Configurable Thresholds & Analysis

The dashboard includes interactive sliders and selector pills to observe detection sensitivity:
- **Total Supply Threshold ($\sigma$):**
  - Range: `0.001%` (Aggressive, captures minor price anomalies) to `0.050%` (Conservative).
  - Default: `0.010%` ($0.0001$), optimal value established in Section 4.3 (Figure 4).
- **Block Window ($n$):**
  - `n = -1`: Single-Transaction Only mode (replicates DeFiRanger baseline; misses all multi-tx attacks).
  - `n = 0`: Same-Block Flashbots Bundle mode.
  - `n = 2`: Multi-Block Optimal mode (captures 98.7% of all real-world attacks per Table 1).
- **Strike Price Impact Watermark:**
  - Default: `2.0%`, industry standard benchmark used for evaluating True Positives (Section 4.6).

---

## 7. Frontend Development (Optional)

If modifying the React frontend:
```bash
cd frontend
npm install
npm run dev    # Starts Vite dev server with proxy to backend at localhost:5173
npm run build  # Rebuilds production bundle into frontend/dist
```

---

## 8. License

This project is created for research and educational purposes, implementing the algorithms published in the IEEE Symposium on Security and Privacy 2024.

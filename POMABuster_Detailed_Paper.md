# POMABuster: A Complete Guide to Detecting Price Oracle Manipulation Attacks in DeFi

## Everything You Need to Know — From Zero to Expert

---

> **Original Paper:** *"POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance"*
> **Authors:** Rui Xi, Zehua (David) Wang, and Karthik Pattabiraman
> **Institution:** Dependable Systems Lab, University of British Columbia (UBC), Canada
> **Venue:** 2024 IEEE Symposium on Security and Privacy (IEEE S&P 2024)
> **Repository:** [github.com/DependableSystemsLab/POMABuster](https://github.com/DependableSystemsLab/POMABuster)

---

## Table of Contents

1. [Part 1: Background — Understanding the World Before the Research](#part-1-background)
   - [What is Blockchain?](#what-is-blockchain)
   - [What are Smart Contracts?](#what-are-smart-contracts)
   - [What is DeFi (Decentralized Finance)?](#what-is-defi)
   - [What are Price Oracles?](#what-are-price-oracles)
   - [What are Flash Loans?](#what-are-flash-loans)
   - [What are AMMs (Automated Market Makers)?](#what-are-amms)
2. [Part 2: The Problem — Why This Research Exists](#part-2-the-problem)
   - [What is a Price Oracle Manipulation Attack (POMA)?](#what-is-poma)
   - [How Does a POMA Actually Work? (Step-by-Step)](#how-does-poma-work)
   - [Real-World Impact and Financial Losses](#real-world-impact)
   - [Why Were Existing Tools Not Enough?](#why-existing-tools-fail)
3. [Part 3: The Solution — POMABuster](#part-3-the-solution)
   - [Core Idea and Philosophy](#core-idea)
   - [Inspiration from the SEC (U.S. Securities Law)](#sec-inspiration)
   - [The Three-Stage Pipeline](#three-stage-pipeline)
   - [Stage 1: Semantic Recovery](#stage-1-semantic-recovery)
   - [Stage 2: Filtering Gate](#stage-2-filtering-gate)
   - [Stage 3: Arbitrage Detection & Linking](#stage-3-arbitrage-detection)
4. [Part 4: The Codebase — How It's Built](#part-4-the-codebase)
   - [Repository Structure](#repository-structure)
   - [Data Collection: Scrapy Spiders](#data-collection)
   - [Core Detection: Jupyter Notebooks](#core-detection)
   - [The Linking Engine](#linking-engine)
   - [Comparison Tool: DeFiRanger](#comparison-tool)
   - [Ablation Study](#ablation-study)
5. [Part 5: Datasets](#part-5-datasets)
   - [Transaction Dataset (Zenodo)](#transaction-dataset)
   - [External Audit Dataset (Code4rena)](#external-audit-dataset)
   - [ICSE'23 Reference Dataset](#icse-reference)
6. [Part 6: Evaluation Results](#part-6-evaluation)
   - [Detection Performance](#detection-performance)
   - [Comparison with Prior Work](#comparison-prior-work)
   - [False Positives and False Negatives](#fp-fn)
7. [Part 7: Limitations and Future Directions](#part-7-limitations)
8. [Part 8: Key Terminology Glossary](#part-8-glossary)

---

## Part 1: Background — Understanding the World Before the Research {#part-1-background}

### What is Blockchain? {#what-is-blockchain}

Imagine a notebook that everyone in the world can read, but nobody can erase or change what's already written. That's essentially a blockchain.

**In technical terms:** A blockchain is a distributed, immutable ledger. It's a database that is:
- **Distributed**: Copies exist on thousands of computers worldwide (no single point of failure)
- **Immutable**: Once data is written, it cannot be changed or deleted
- **Transparent**: Anyone can read every transaction ever made
- **Decentralized**: No single company, bank, or government controls it

**Ethereum** is the blockchain that POMABuster focuses on. Unlike Bitcoin (which is mainly for sending/receiving digital money), Ethereum supports *programmable* transactions through something called "smart contracts."

### What are Smart Contracts? {#what-are-smart-contracts}

A smart contract is a computer program that lives on the blockchain. Think of it like a vending machine:
- You put in money → select your item → the machine gives it to you automatically
- No human needed. The rules are coded in. Once deployed, the code runs exactly as written.

**Key properties:**
- **Self-executing**: They run automatically when conditions are met
- **Trustless**: You don't need to trust anyone — the code is the law
- **Permanent**: Once deployed on Ethereum, the contract exists forever
- **Transparent**: Anyone can read the contract's code and verify what it does

**Example:** A lending smart contract might say: *"If you deposit 100 ETH as collateral, I'll lend you 50,000 USDC. If the value of your ETH drops below 60,000 USDC, I'll automatically liquidate your collateral."*

### What is DeFi (Decentralized Finance)? {#what-is-defi}

DeFi is the recreation of traditional financial services (banking, lending, trading, insurance) using smart contracts instead of banks and financial institutions.

| Traditional Finance | DeFi Equivalent |
|---|---|
| Bank savings account | Lending protocols (Aave, Compound) |
| Stock exchange (NYSE) | Decentralized exchanges / DEXs (Uniswap, SushiSwap) |
| Broker | No broker needed — trade directly |
| Loan officer | Smart contract auto-approves loans |
| Clearing house | Blockchain settles everything instantly |

**Why does DeFi matter?**
- Open to anyone with internet access (no bank account needed)
- Operates 24/7 (no "market closed" hours)
- Transparent (all code and transactions are public)
- Composable (different DeFi protocols can be combined like LEGO blocks)

**Scale:** As of 2024, DeFi protocols collectively hold tens of billions of dollars in user funds.

### What are Price Oracles? {#what-are-price-oracles}

This is the CRITICAL concept for understanding POMABuster.

**The Problem:** Smart contracts live on the blockchain. The blockchain only knows about data *on* the blockchain. But DeFi protocols need to know things like: *"What is the current price of ETH in USD?"* — this information exists in the real world (exchanges like Coinbase, Binance), not on the blockchain.

**The Solution:** A **price oracle** is a mechanism that feeds external price data into a smart contract.

**Types of price oracles:**

1. **On-chain oracles (AMM-based):** The protocol reads the current price directly from a decentralized exchange (DEX) pool on the blockchain.
   - ⚠️ **DANGEROUS** — This is what attackers exploit! The price can be temporarily manipulated.

2. **Off-chain oracles (e.g., Chainlink):** External services aggregate prices from many sources and push them to the blockchain.
   - ✅ **Safer** — Much harder to manipulate because they aggregate from multiple sources.

3. **Time-Weighted Average Price (TWAP):** Uses an average price over a time period instead of a single snapshot.
   - ✅ **Safer** — Smooths out temporary price spikes.

**The vulnerability:** When a DeFi protocol uses a *single DEX pool* as its price oracle (Type 1), an attacker can temporarily change the price in that pool and trick the protocol.

### What are Flash Loans? {#what-are-flash-loans}

Flash loans are one of the most revolutionary — and dangerous — innovations in DeFi.

**Concept:** You can borrow **any amount** of cryptocurrency (potentially millions of dollars) with:
- ❌ No collateral
- ❌ No credit check
- ❌ No identity verification

**The catch:** You MUST repay the entire loan **within the same transaction**. If the blockchain detects that the loan isn't repaid by the end of the transaction, the entire transaction is reversed as if nothing happened.

**Why do they exist?** On a blockchain, a "transaction" is atomic — it either fully succeeds or fully fails. This means flash loans are risk-free for the lender. If the borrower can't repay, everything is undone.

**Why are they dangerous?** They give anyone access to massive capital, enabling market manipulation that would otherwise require millions of dollars in personal funds.

### What are AMMs (Automated Market Makers)? {#what-are-amms}

In traditional stock exchanges, buyers and sellers submit orders, and a matching engine pairs them. AMMs do something fundamentally different.

**How AMMs work:**
1. People (called Liquidity Providers / LPs) deposit pairs of tokens into a "pool" (e.g., ETH + USDC)
2. The smart contract uses a mathematical formula to determine the price based on the ratio of tokens in the pool
3. The most common formula is: **x × y = k** (constant product formula)

**Example with Uniswap's x × y = k:**
- Pool has: 100 ETH and 200,000 USDC
- k = 100 × 200,000 = 20,000,000
- Current price: 200,000 / 100 = 2,000 USDC per ETH

**What happens when someone buys 10 ETH:**
- They add USDC to the pool, remove ETH
- Pool becomes: 90 ETH and ~222,222 USDC (to maintain k = 20,000,000)
- New price: 222,222 / 90 ≈ 2,469 USDC per ETH
- The price moved UP because ETH became scarcer in the pool

> **Key insight:** Large trades significantly move the price in an AMM pool. This is called "slippage," and it's the foundation of oracle manipulation attacks.

---

## Part 2: The Problem — Why This Research Exists {#part-2-the-problem}

### What is a Price Oracle Manipulation Attack (POMA)? {#what-is-poma}

A **Price Oracle Manipulation Attack (POMA)** is a type of exploit where an attacker artificially distorts the price of a cryptocurrency asset on a DEX that a victim smart contract uses as its price oracle, and then profits from the resulting price discrepancy.

**In simple terms:** The attacker lies about the price → the victim protocol believes the lie → the attacker steals money.

### How Does a POMA Actually Work? (Step-by-Step) {#how-does-poma-work}

Here's a concrete example of a POMA attack:

```
🎯 Target: A lending protocol that uses Uniswap's ETH/USDC pool as its price oracle
💰 Real ETH price: $2,000

STEP 1: FLASH LOAN
├── Attacker borrows 10,000,000 USDC via flash loan (free!)
├── Cost: $0 upfront

STEP 2: MANIPULATE THE ORACLE
├── Attacker dumps 10,000,000 USDC into the Uniswap ETH/USDC pool
├── Buys massive amount of ETH
├── The pool now thinks ETH = $50,000 (artificially inflated!)
├── The lending protocol reads this pool and believes ETH = $50,000

STEP 3: EXPLOIT THE VICTIM
├── Attacker deposits 100 ETH into the lending protocol
├── Protocol thinks: 100 ETH × $50,000 = $5,000,000 collateral
├── Protocol lends attacker $4,000,000 in stablecoins
├── (Real value of 100 ETH is only $200,000!)

STEP 4: REVERSE THE MANIPULATION
├── Attacker sells back the ETH in the Uniswap pool
├── Pool price returns to normal (~$2,000)

STEP 5: REPAY AND PROFIT
├── Attacker repays the flash loan ($10,000,000 + small fee)
├── Attacker keeps $4,000,000 from the lending protocol
├── Attacker's 100 ETH collateral gets liquidated ($200,000 loss)
├── NET PROFIT: ~$3,800,000 💰
```

**Key characteristics of POMAs:**
1. **Targets high-value tokens** (ETH, WBTC, USDC) — more liquidity to exploit
2. **Rapid execution** — transactions happen within seconds/minutes
3. **Often uses flash loans** — zero capital requirement
4. **Can be single-transaction OR multi-transaction** — this is important!

### Real-World Impact and Financial Losses {#real-world-impact}

POMAs have caused hundreds of millions of dollars in losses:

| Protocol | Year | Loss | Attack Type |
|---|---|---|---|
| bZx | 2020 | $8M | Flash loan + oracle manipulation |
| Harvest Finance | 2020 | $34M | Price manipulation via Curve pools |
| Cream Finance | 2021 | $130M | Oracle manipulation |
| Mango Markets | 2022 | $114M | Oracle manipulation (Solana) |
| Many others... | 2020-2024 | Hundreds of millions | Various POMA variants |

### Why Were Existing Tools Not Enough? {#why-existing-tools-fail}

Before POMABuster, the main tools for detecting these attacks were:

**1. DeFiRanger (ICSE 2023)**
- ❌ Only detected **single-transaction** attacks
- ❌ Could not detect attacks spanning multiple transactions
- ❌ Relied on predefined patterns of known attacks
- ❌ Missed sophisticated multi-step attacks

**2. Static Analysis Tools (Slither, Mythril, etc.)**
- ❌ Analyze smart contract *code*, not *transactions*
- ❌ Can find potential vulnerabilities but can't detect actual attacks
- ❌ Don't understand DeFi-specific semantics

**3. Manual Audit (Code4rena, Sherlock)**
- ✅ High quality
- ❌ Extremely slow (weeks per audit)
- ❌ Expensive ($50K-$500K per audit)
- ❌ Reactive, not proactive

**The gap POMABuster fills:**
- ✅ Detects **both** single-transaction AND multi-transaction attacks
- ✅ Doesn't rely on known attack patterns (works on novel attacks)
- ✅ Automated and scalable
- ✅ Low false positive rate

---

## Part 3: The Solution — POMABuster {#part-3-the-solution}

### Core Idea and Philosophy {#core-idea}

POMABuster takes a fundamentally different approach from prior work. Instead of trying to match against known attack patterns (which fails against new attacks), it works from **first principles**:

> **Key insight:** A POMA is essentially a form of market manipulation. Market manipulation in traditional finance has been studied for decades. The U.S. Securities and Exchange Commission (SEC) has well-defined rules for identifying suspicious trading behavior. We can adapt these rules for DeFi.

The system doesn't need to know *how* an attack was carried out. It only needs to detect the *effects*:
1. Someone traded in a way that looks like market manipulation
2. Someone else (or the same person) profited from the resulting price change

### Inspiration from the SEC (U.S. Securities Law) {#sec-inspiration}

The SEC defines several types of market manipulation in traditional stock markets. POMABuster adapts these concepts for blockchain:

| SEC Manipulation Type | Traditional Finance | DeFi Equivalent |
|---|---|---|
| **Wash Trading** | Buying & selling the same stock to inflate volume | Trading tokens back and forth between your own wallets |
| **Pump and Dump** | Artificially inflating price, then selling | Flash-loan buying → exploit → dump |
| **Spoofing** | Placing fake orders to mislead | Creating deceptive on-chain transactions |
| **Market Cornering** | Controlling a large portion of supply | Controlling most of a token's liquidity |

POMABuster specifically looks for:
- **Abnormal trade sizes** relative to the pool's liquidity
- **Rapid round-trip trades** (buy → do something → sell) within a short block window
- **Connected parties** (same operator or coordinated wallets)

### The Three-Stage Pipeline {#three-stage-pipeline}

POMABuster's detection engine works in three sequential stages:

```
┌─────────────────────────────────────────────────────────────────┐
│                      RAW BLOCKCHAIN DATA                        │
│         (Transfer logs from Ethereum-ETL / BigQuery)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STAGE 1: SEMANTIC RECOVERY                      │
│    ┌─────────────────────────────────────────────────────┐      │
│    │  Raw transfer logs → High-level DeFi actions        │      │
│    │  • Normal trades (swap)                             │      │
│    │  • Liquidity mining (adding liquidity)              │      │
│    │  • Liquidity cancellation (removing liquidity)      │      │
│    │  • Token minting / burning                          │      │
│    └─────────────────────────────────────────────────────┘      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                 STAGE 2: FILTERING GATE                         │
│    ┌─────────────────────────────────────────────────────┐      │
│    │  Apply SEC-inspired rules to flag suspicious trades │      │
│    │  • Abnormal trade sizes                             │      │
│    │  • Round-trip patterns                              │      │
│    │  • Suspicious timing / block proximity              │      │
│    │  • Concentrated token holdings                      │      │
│    └─────────────────────────────────────────────────────┘      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│           STAGE 3: ARBITRAGE DETECTION & LINKING                │
│    ┌─────────────────────────────────────────────────────┐      │
│    │  Link suspicious price manipulation (POM)           │      │
│    │  transactions with arbitrage (ARB) transactions     │      │
│    │  • Same tokens involved?                            │      │
│    │  • Within 0-2 blocks of each other?                 │      │
│    │  • Did someone profit?                              │      │
│    └─────────────────────────────────────────────────────┘      │
│                                                                 │
│    Output: POMA DETECTED or BENIGN                              │
└─────────────────────────────────────────────────────────────────┘
```

### Stage 1: Semantic Recovery {#stage-1-semantic-recovery}

**What it does:** Converts raw, low-level blockchain data into meaningful DeFi actions.

**The challenge:** The Ethereum blockchain doesn't store "Alice swapped ETH for USDC on Uniswap." It stores something like:

```
Transfer(from=0xAlice, to=0xUniswapPool, token=WETH, amount=1000000000000000000)
Transfer(from=0xUniswapPool, to=0xAlice, token=USDC, amount=2000000000)
Mint(from=0x000, to=0xAlice, token=UNI-V2, amount=500000000)
```

POMABuster reconstructs meaning from these raw logs using pattern matching:

**Data classes used:**
```python
@dataclass
class Log:
    sender: str      # Who sent the tokens
    receiver: str    # Who received them
    amount: int      # How many tokens
    asset: str       # Which token (contract address)
    idx: int         # Position in the transaction

@dataclass
class Trade:
    operator: str    # Who initiated the action
    recipient: str   # Who benefited
    pool: str        # Which DEX pool was used
    asset_in: str    # Token sent to pool
    asset_out: str   # Token received from pool
    amount_in: int   # Amount sent
    amount_out: int  # Amount received
    log_idx: int     # Position for ordering
```

**Detection patterns:**

| Pattern | What It Means | How It's Detected |
|---|---|---|
| Transfer A→Pool + Transfer Pool→A | **Normal trade (swap)** | Two transfers to/from the same pool, different tokens |
| Transfer A→Pool + Mint(0x0→A) | **Liquidity mining** | User sends tokens to pool, receives LP tokens (minted) |
| Burn(A→0x0) + Transfer Pool→A | **Liquidity cancellation** | User burns LP tokens, receives underlying tokens back |
| Transfer(0x0→A) | **Token minting** | Sender is the zero address |
| Transfer(A→0x0) | **Token burning** | Receiver is the zero address |

**Key functions in the code:**
- `is_transfer_normal(log)` — Checks if both sender and receiver are real addresses (non-zero) and amount > 0
- `is_transfer_minting(log)` — Sender is the zero address (0x000...000)
- `is_transfer_burning(log)` — Receiver is the zero address
- `has_liquidity_mining(logs)` — Pairs normal transfers with minting events
- `has_liquidity_cancel(logs)` — Pairs burning events with normal transfers

### Stage 2: Filtering Gate {#stage-2-filtering-gate}

**What it does:** Applies SEC-inspired rules to separate normal trading from suspicious manipulation.

After Stage 1 reconstructs all the DeFi actions in a transaction, Stage 2 applies filters to find potentially manipulative behavior. The key principle is: **manipulation leaves measurable footprints**.

**Filters applied:**

1. **Trade Size Anomaly**: Is the trade size disproportionately large relative to the pool's liquidity? A legitimate trader rarely moves more than a small percentage of a pool.

2. **Round-Trip Detection**: Did the same operator buy and sell the same token within a very short time window? This is a hallmark of manipulation — buy to inflate price, exploit, then sell to recover funds.

3. **Token Holder Concentration Analysis**: The `analyze_token_holder.ipynb` notebook analyzes how concentrated token holdings are. Highly concentrated tokens (where top holders own most of the supply) are more susceptible to manipulation.

4. **Block Window Proximity**: Suspicious transactions that occur within 0-2 blocks of each other (roughly 0-30 seconds) are flagged. Legitimate trading rarely requires such precise timing.

### Stage 3: Arbitrage Detection & Linking {#stage-3-arbitrage-detection}

**What it does:** This is the final and most important stage. It answers the question: *"Did someone profit from a price manipulation?"*

**The logic (from `linking.ipynb`):**

```
For each suspected Price Oracle Manipulation (POM) transaction:
    1. Get the block number of the POM transaction
    2. Find all Arbitrage (ARB) transactions within 0-2 blocks
    3. Check if any ARB transaction interacts with the SAME tokens
    4. If YES → The POM and ARB are LINKED → POMA DETECTED!
```

**In code terms:**
```python
# Pseudocode from linking.ipynb
for pom in pom_transactions:
    pom_block = pom.block_number
    pom_assets = set(pom.tokens_involved)
    
    # Look for arbitrage within 2 blocks
    nearby_arbs = arb_df[arb_df.block_number - pom_block <= 2]
    
    for arb in nearby_arbs:
        arb_assets = set(arb.tokens_involved)
        
        # Do they share tokens?
        if arb_assets.intersection(pom_assets):
            # POMA DETECTED!
            linked_attacks.append((pom.tx_hash, arb.tx_hash))
```

**Why 2 blocks?** On Ethereum, a new block is produced approximately every 12 seconds. An attacker needs to:
1. Manipulate the price (block N)
2. Exploit the manipulated price (block N, N+1, or N+2)
3. Reverse the manipulation (within the same window)

A window of 2 blocks (~24 seconds) captures the vast majority of attacks while minimizing false positives.

---

## Part 4: The Codebase — How It's Built {#part-4-the-codebase}

### Repository Structure {#repository-structure}

```
POMABuster/
├── README.md                          # Project overview and setup instructions
├── LICENSE                            # MIT License
├── dataset/
│   ├── readme.txt                     # Points to Zenodo for transaction data
│   └── external_dataset/
│       ├── 03.md                      # Code4rena audit: PriceAware.sol manipulation
│       ├── 16.md                      # Code4rena audit: Wrong trading pricing
│       ├── 20.md                      # Code4rena audit: Flash loan on Synth
│       ├── 23.md                      # Code4rena audit: Liquidity token manipulation
│       ├── 42.md                      # Code4rena audit: Treasury sandwich attack
│       ├── 52.md                      # Code4rena audit: Minting/burning slippage
│       ├── 67.md                      # Code4rena audit report
│       ├── 70.md                      # Code4rena audit report
│       ├── 78.md                      # Code4rena audit report
│       ├── 83.md                      # NOT a POMA (manually corrected)
│       ├── 193.md                     # NOT a POMA (manually corrected)
│       ├── icse.md                    # Reference from ICSE'23 paper dataset
│       └── sample                     # Sample transfer event format
├── src/
│   ├── sec/                           # Main analysis code (SEC-inspired)
│   │   ├── pomabuster.ipynb           # 🔑 MAIN DETECTION ENGINE
│   │   ├── arbitrage_filter.ipynb     # Arbitrage identification logic
│   │   ├── linking.ipynb              # POM↔ARB transaction linking
│   │   ├── defiranger.ipynb           # DeFiRanger comparison baseline
│   │   ├── ablate.ipynb               # Ablation study experiments
│   │   ├── analyze_token_holder.ipynb # Token holder concentration analysis
│   │   ├── pm_number.pkl              # Serialized data (pickle file)
│   │   └── drf_000                    # DeFiRanger output/reference data
│   └── tokens/
│       └── scrape_erc20/
│           ├── scrapy.cfg             # Scrapy framework configuration
│           └── scrape_erc20/
│               └── spiders/
│                   ├── ERC20.py       # Spider: scrape token metadata
│                   └── holder.py      # Spider: scrape token holder data
```

### Data Collection: Scrapy Spiders {#data-collection}

POMABuster uses [Scrapy](https://scrapy.org/), a Python web scraping framework, to collect token data from Etherscan.

**Spider 1: `ERC20.py` — Token Metadata Scraper**

This spider crawls Etherscan's ERC-20 token listing page to collect information about tokens:

```python
class EtherscanERC20Spider(scrapy.Spider):
    name = "erc20"
    start_urls = ["https://etherscan.io/tokens"]
    
    def parse(self, response):
        # Iterates through each row in the ERC-20 token table
        # Extracts for each token:
        #   - index: Ranking position
        #   - name: Token name (e.g., "Tether USD")
        #   - address: Contract address (e.g., "0xdac17f...")
        #   - price_in_usd: Current price
        #   - volume: 24h trading volume
        #   - market_cap: Market capitalization
        #   - holders: Number of unique addresses holding the token
        
    def parse_overview(self, response):
        # Follows each token's link to get additional data:
        #   - fully_diluted_market_cap: Total potential market cap
```

**Spider 2: `holder.py` — Token Holder Distribution Scraper**

This spider collects who holds how much of each token:

```python
class EtherscanERC20HolderSpider(scrapy.Spider):
    name = "holder"
    
    def start_requests(self):
        # Reads the output of the ERC20 spider (erc20.jsonlines)
        # For each token, requests the holder chart page
        
    def parse(self, response):
        # Extracts top token holders:
        #   - holder_address: Wallet/contract address
        #   - token_amount: How many tokens they hold
        #   - percentage: What % of total supply they own
```

**Why is holder data important?** If a single entity controls 30%+ of a token's supply, they can much more easily manipulate its price. This is one of the filtering criteria in Stage 2.

### Core Detection: Jupyter Notebooks {#core-detection}

The main analysis is implemented in Jupyter notebooks (`.ipynb` files), which allow interactive data exploration and visualization.

**`pomabuster.ipynb` — The Main Engine**
- Loads transaction data from BigQuery/Zenodo
- Applies semantic recovery to parse transfer logs
- Runs the SEC-inspired filtering rules
- Identifies potential Price Oracle Manipulation transactions
- Outputs suspected POM transaction hashes

**`arbitrage_filter.ipynb` — Arbitrage Identification**
- Contains the `Log` and `Trade` dataclass definitions
- Implements all the semantic recovery helper functions
- Identifies arbitrage transactions (someone buying low, selling high)
- Distinguishes between:
  - Normal trades (swaps)
  - Liquidity providing (mining)
  - Liquidity removal (cancellation)
  - Minting and burning

### The Linking Engine {#linking-engine}

**`linking.ipynb` — The Correlation Engine**

This is arguably the most important notebook. It takes:
- **Input 1:** List of suspected POM (manipulation) transactions
- **Input 2:** List of identified ARB (arbitrage) transactions
- **Output:** Pairs of (POM_tx, ARB_tx) that form a complete POMA

The linking algorithm:
1. Loads POM and ARB transactions from `.jsonl` files
2. For each POM transaction, gets its block number
3. Searches for ARB transactions within a 2-block window
4. Checks if the ARB transaction touches the same token assets
5. If both conditions are met (proximity + shared assets), they are linked

### Comparison Tool: DeFiRanger {#comparison-tool}

**`defiranger.ipynb` — Baseline Comparison**

DeFiRanger is a prior tool (ICSE 2023) for detecting DeFi attacks. POMABuster implements a comparison against it to demonstrate superior performance. Key differences:

| Feature | DeFiRanger | POMABuster |
|---|---|---|
| Transaction scope | Single-transaction only | Multi-transaction support |
| Detection approach | Pattern matching | First-principle rules |
| Oracle types | Limited | Comprehensive |
| False negatives | Higher | 0% (in evaluation) |

### Ablation Study {#ablation-study}

**`ablate.ipynb` — Component Contribution Analysis**

An ablation study tests what happens when you *remove* one component at a time. This proves that each part of POMABuster contributes to its effectiveness:

- Remove semantic recovery → Detection drops significantly
- Remove SEC filters → False positives increase dramatically
- Remove linking → Can't connect manipulation to profit
- Remove holder analysis → Misses concentration-based attacks

---

## Part 5: Datasets {#part-5-datasets}

### Transaction Dataset (Zenodo) {#transaction-dataset}

**Location:** [Zenodo Record 10359283](https://zenodo.org/records/10359283)

This is the primary dataset containing actual Ethereum blockchain transaction data. The data was obtained from:

1. **Google BigQuery's Ethereum Dataset**: Google maintains a public dataset of all Ethereum transactions, queryable via SQL
2. **Ethereum-ETL**: An open-source tool that extracts and transforms Ethereum data into analysis-friendly formats

**Data format:** Each record contains:
```
block_hash, transaction_hash, log_index, token_address, from_address, to_address, value
```

**Coverage:** Approximately 2.5 years of Ethereum transaction data.

### External Audit Dataset (Code4rena) {#external-audit-dataset}

**Location:** `dataset/external_dataset/*.md`

These are manually curated reports from [Code4rena](https://code4rena.com/), a competitive audit platform where security researchers find vulnerabilities in smart contracts.

Each `.md` file documents a specific vulnerability finding:
- **Source Code**: Link to the vulnerable Solidity code on GitHub
- **POMA Description**: How the oracle can be manipulated
- **Attack Transaction**: Step-by-step attack scenario with specific addresses and amounts

**Example (from `03.md`):**
> *"Anyone can trigger an update to the price feed by calling `PriceAware.getCurrentPriceInPeg()`. If the update window has passed, the price will be computed by simulating a Uniswap-like trade with the amounts. This simulation uses the reserves of the Uniswap pairs which can be changed drastically using flash loans."*

**Important corrections:** The authors manually vetted this dataset. Files `83.md` and `193.md` contain notes like:
> *"NOTE: this is not a POMA. The ICSE'23 paper put it into the wrong hole."*

This shows rigorous data quality control.

### ICSE'23 Reference Dataset {#icse-reference}

**Location:** `dataset/external_dataset/icse.md`

This file maps vulnerability IDs to their descriptions from a prior ICSE 2023 paper. It serves as:
1. A ground truth reference for known POMA vulnerabilities
2. A comparison baseline (POMABuster found additional attacks that this dataset missed)

Contents include known vulnerabilities like:
- "Price feed can be manipulated"
- "Synth realise is vulnerable to flash loan attacks"
- "Liquidity token value can be manipulated"
- "Treasury is vulnerable to sandwich attack"

---

## Part 6: Evaluation Results {#part-6-evaluation}

### Detection Performance {#detection-performance}

POMABuster was evaluated on 2.5 years of historical Ethereum blockchain data:

| Metric | POMABuster | DeFiRanger (Prior Art) |
|---|---|---|
| POMAs detected | **~6.5× more** | Baseline |
| False negatives | **0%** | Higher |
| Worst-case false positives | **~1%** | Not reported |
| Multi-transaction attacks | ✅ Detected | ❌ Missed |
| Performance overhead | Low | N/A |

### Comparison with Prior Work {#comparison-prior-work}

POMABuster's key advantage over DeFiRanger:

1. **Multi-transaction detection**: DeFiRanger can only detect attacks that happen within a single blockchain transaction. POMABuster's linking engine can connect manipulation across multiple transactions.

2. **Pattern independence**: DeFiRanger requires known attack patterns. POMABuster's SEC-inspired rules detect novel attacks.

3. **Broader oracle coverage**: POMABuster works across different types of on-chain price oracles, not just specific DEX implementations.

### False Positives and False Negatives {#fp-fn}

- **False Negatives (missed attacks): 0%** — In their evaluation dataset, POMABuster detected every known POMA.
- **False Positives (false alarms): ~1% worst case** — Very few legitimate transactions were incorrectly flagged as attacks.

This is significant because security tools face a constant tradeoff: cast a wider net (catch more attacks but more false alarms) vs. be more selective (fewer false alarms but miss some attacks). POMABuster achieves both low false positives AND zero false negatives.

---

## Part 7: Limitations and Future Directions {#part-7-limitations}

### Current Limitations

1. **POMA-specific focus**: POMABuster only detects price oracle manipulation attacks. It doesn't detect other DeFi exploits like reentrancy attacks, governance attacks, or flash loan arbitrage without oracle manipulation.

2. **Ethereum-centric**: The current implementation is designed for Ethereum. Other blockchains (Solana, BSC, Avalanche, etc.) have different architectures and would require adaptation.

3. **Noise potential**: The rule-based approach may flag "any suspicious transactions" matching its rules, even if they aren't actually malicious.

4. **Research vs. Production**: The current implementation exists as Jupyter notebooks for research purposes. A production deployment would require significant engineering work.

5. **Post-hoc detection**: POMABuster analyzes historical data. It doesn't prevent attacks in real-time (though it could be adapted for near-real-time monitoring).

### Future Directions

1. **Real-time monitoring**: Integrate POMABuster into blockchain monitoring infrastructure for live detection and alerting.

2. **Cross-chain support**: Extend to other EVM-compatible chains (BSC, Polygon, Arbitrum, Optimism).

3. **Automated response**: Couple detection with automated defense mechanisms (e.g., pausing vulnerable contracts).

4. **LLM-assisted repair**: Use Large Language Models to automatically suggest patches for vulnerable oracle implementations.

5. **Multi-layered security**: Integrate POMABuster into broader DeFi security frameworks alongside static analysis tools and formal verification.

---

## Part 8: Key Terminology Glossary {#part-8-glossary}

| Term | Definition |
|---|---|
| **AMM** | Automated Market Maker — A DEX that uses mathematical formulas instead of order books to set prices |
| **Arbitrage** | Profiting from price differences of the same asset across markets |
| **Block** | A batch of transactions confirmed together on the blockchain (~12 sec on Ethereum) |
| **Code4rena** | A competitive smart contract auditing platform |
| **Collateral** | Assets deposited as security for a loan |
| **DEX** | Decentralized Exchange — A trading platform run by smart contracts |
| **DeFi** | Decentralized Finance — Financial services built on blockchain |
| **ERC-20** | The standard interface for fungible tokens on Ethereum |
| **Ethereum-ETL** | Tool for extracting and transforming Ethereum blockchain data |
| **Flash Loan** | An uncollateralized loan that must be repaid in the same transaction |
| **Gas** | The fee paid to execute operations on Ethereum |
| **Immutable** | Cannot be changed once deployed |
| **Liquidation** | Forced sale of collateral when its value drops below a threshold |
| **Liquidity Pool** | A smart contract holding paired tokens for trading |
| **LP Token** | A receipt token given to liquidity providers |
| **Oracle** | A data feed that provides external information to smart contracts |
| **POMA** | Price Oracle Manipulation Attack |
| **Sandwich Attack** | Front-running and back-running a victim's transaction |
| **SEC** | U.S. Securities and Exchange Commission |
| **Slippage** | The difference between expected and actual trade execution price |
| **Smart Contract** | Self-executing code deployed on a blockchain |
| **Token** | A digital asset on the blockchain |
| **Transaction Hash** | A unique identifier for a blockchain transaction |
| **TWAP** | Time-Weighted Average Price — an oracle that averages price over time |
| **WETH** | Wrapped Ether — An ERC-20 compatible version of ETH |

---

> **Summary:** POMABuster is a pioneering research tool that detects price oracle manipulation attacks in DeFi by applying U.S. securities law principles to blockchain transaction analysis. It operates through a three-stage pipeline: semantic recovery (understanding what transactions mean), filtering (applying SEC-inspired manipulation rules), and linking (connecting manipulation events to profit-taking). It detected 6.5× more attacks than prior work with zero false negatives and ~1% false positives.

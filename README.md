# POMABuster - Custom Enterprise Implementation

**Reference Paper Details:**
- **Paper Name:** POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance
- **Authors:** Rui Xi, Zehua Wang, Karthik Pattabiraman
- **Conference:** 2024 IEEE Symposium on Security and Privacy (SP)
- **Year of Publish:** 2024
- **Conference Rating:** Core Rank A* (Top-tier Security Conference)




![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

This repository contains a structured, enterprise-grade Python package implementation of **POMABuster**, an automated engine designed to detect Price Oracle Manipulation Attacks (POMAs) on blockchain systems like Ethereum.

This version is built from scratch based on the first-principles methodology outlined in the original research paper. It successfully detects both single and multi-transaction attacks without relying on brittle, predefined patterns.

## 📖 Architecture & How It Works

The codebase is organized into a modular Python package structure:

```text
POMABuster/
├── core/                   # Contains data models and Trade Reconstructor
├── detectors/              # SEC-inspired rules (Market Domination, Arbitrage)
├── engine/                 # Cross-transaction Attack Linker
├── utils/                  # JSON Data loaders
├── tests/                  # Unit test suite
├── data/                   # Datasets
│   ├── test_data.json      # Synthetic transaction logs
│   └── token_supplies.json # Token market capabilities
└── main.py                 # Entry point for execution
```

### Detection Phases:
1. **Trade Reconstruction:** Parses raw atomic token transfer logs and reconstructs logical DeFi trades (e.g., swapping Token A for Token B at a Liquidity Pool).
2. **Market Domination Detection:** Uses SEC-inspired rules to flag trades where the exchanged amount exceeds a critical threshold of the token's total circulating supply (default: `0.01%`). These are flagged as potential Price Oracle Manipulations (POM).
3. **Arbitrage Detection:** Identifies cycles of trades where the final output token matches the initial input token, and the final amount is greater than the starting amount (Profit > 0).
4. **Linking:** Links POM trades with Arbitrage trades if they share manipulated/intermediate tokens and occur within a close block proximity (e.g., within 2 blocks). When linked, a full POMA attack is declared.

## 🚀 How to Execute and Test

We have provided a synthetic dataset (`data/test_data.json`) that simulates real Ethereum transfer logs. It contains:
- A malicious **POM transaction** (Market Domination).
- A subsequent **Arbitrage transaction** exploiting the manipulated price within 1 block.
- A **Benign trade** that operates normally and should be ignored by the detector.

### Prerequisites
- Python 3.x (No external dependencies required for the core engine!)

### Execution
Simply run the detection engine from your terminal:

```bash
python main.py
```

### Expected Output
When you run the script, you will see the engine parse the logs, execute the pipeline modules, and flag the complete attack:

```text
Initializing POMABuster Engine...
[+] Loaded 8 transfer logs.
[+] Reconstructed 4 logical trades.
[+] Detected 1 Price Oracle Manipulation (POM) trades.
[+] Detected 1 Arbitrage transactions.

================ FINAL REPORT ================
Successfully detected 1 complete POMA(s)!
  [1] POM Tx: 0x_attack_pom | Arb Tx: 0x_attack_arb | Block Span: 1
==============================================
```

### Running the Test Suite
To ensure the modular components function correctly, you can run the unit test suite:
```bash
python -m unittest discover tests
```

## 📚 References
- Based on the methodology from the paper: *"POMABuster: Detecting Price Oracle Manipulation Attacks in Decentralized Finance"*.

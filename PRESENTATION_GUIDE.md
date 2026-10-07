# Presentation Guide for Professor

This guide contains the key talking points for presenting the POMABuster project to your professor. It breaks down the narrative into a clear, logical flow: explaining the background, the core problem, and the solution implemented in this codebase.

## 1. Introduction (The Background)
**What to say:**
- "My project focuses on the security of Decentralized Finance (DeFi) on the blockchain."
- "Specifically, I am looking at a severe type of exploit called a **Price Oracle Manipulation Attack (POMA)**."
- "In a typical POMA, an attacker performs two steps:
  1. **Manipulation:** They execute massive trades on a decentralized exchange (like Uniswap) to artificially pump or dump the price of a token (manipulating the 'price oracle').
  2. **Arbitrage:** They immediately exploit this fake price in another smart contract (e.g., a lending protocol) to steal funds or liquidate users, making a massive profit."

## 2. The Core Problem (Why existing tools fail)
**What to say:**
- "Historically, tools like *DeFiRanger* tried to detect these attacks by looking for specific attack patterns happening within a **single transaction**."
- "However, attackers evolved. They started using a mechanism called **Flashbots**. Flashbots allow attackers to split their attack into **multiple separate transactions** (one transaction for the manipulation, and a completely separate transaction for the arbitrage) and guarantee they get executed together in the same block."
- "Because the attack is now split up, older tools that only look at single transactions completely miss them. In fact, over 74% of modern POMAs span multiple transactions."
- "Additionally, older tools rely on brittle pattern-matching, which means they can't detect new, unseen methods of attack."

## 3. Our Solution: POMABuster (How we solve it)
**What to say:**
- "To solve this, I reproduced **POMABuster**. Instead of memorizing attack patterns, POMABuster uses a **First-Principles Approach**."
- "It borrows rules directly from the U.S. Securities and Exchange Commission (SEC) for traditional stock market manipulation:
  1. **Market Domination:** It flags any trade that moves a massive percentage of a token's total circulating supply (e.g., > 0.01%).
  2. **Wash Sales:** It flags repeated cyclical trading."
- "Next, instead of looking at just one transaction, it looks at a **2-block time window**. It searches for any 'Arbitrage' transactions that happen immediately after a 'Market Domination' transaction and checks if they share the same manipulated tokens."
- "By doing this, it successfully links the split transactions back together and detects the full attack."

## 4. The Codebase Implementation (Showcasing your work)
**What to say:**
- "I have built a custom, enterprise-grade Python detection engine from scratch to implement this logic."
- **Show the directory structure:** Explain how it is modularized into `core/`, `detectors/`, and `engine/`.
- **Show `test_data.json`:** Explain that you created a synthetic blockchain dataset that contains raw token transfer logs, including a hidden multi-transaction attack and some benign trades.
- **Run the code:** Execute `python main.py` in front of the professor. 
- **Explain the output:** Show how the engine successfully parses the raw logs, flags the Market Domination trade, flags the Arbitrage trade, and finally *links* them together to expose the attack, while completely ignoring the benign trades.

## 5. Key Research Findings (To wrap up)
**What to say:**
- "Based on the research, this method detects **6.5X more attacks** than older tools."
- "It has a worst-case False Positive Rate of only 0.95%."
- "Interestingly, it revealed that attackers generated over **$77.8 Billion** in revenue over 2.5 years, and surprisingly, they rarely use privacy mixers (like Tornado Cash) to hide their tracks—they just reuse the same wallets."

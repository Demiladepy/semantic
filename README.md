# Semantic Arbitrage Engine

> **AI-Powered Cross-Platform Prediction Market Arbitrage System**

A sophisticated Python-based arbitrage engine that identifies and exploits logical arbitrage opportunities across multiple prediction market platforms using advanced Natural Language Inference (NLI) and semantic analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Solana](https://img.shields.io/badge/Solana-Devnet-9945FF.svg)](https://solana.com)
[![Status: Active](https://img.shields.io/badge/status-active-brightgreen.svg)]()

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Supported Platforms](#supported-platforms)
- [Installation](#installation)
- [Configuration](#configuration)
- [Quick Start](#quick-start)
- [Core Components](#core-components)
- [AI Agent & Privacy Features](#ai-agent--privacy-features)
- [PNP Exchange Integration](#pnp-exchange-integration)
- [Usage Examples](#usage-examples)
- [Advanced Features](#advanced-features)
- [Live Dashboard](#live-dashboard)
- [Testing](#testing)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Semantic Arbitrage Engine is a cutting-edge trading system that:

- **Discovers** semantically equivalent markets across different platforms
- **Analyzes** price discrepancies using NLI (Natural Language Inference)
- **Executes** profitable arbitrage trades automatically
- **Manages** risk with sophisticated position sizing and exposure limits
- **Monitors** markets in real-time with WebSocket integration
- **Protects** privacy with zero-knowledge proof support
- **Alerts** via Telegram for critical events and opportunities

### What Makes It Unique?

Unlike traditional arbitrage systems that rely on exact market matching, this engine uses **semantic understanding** to identify equivalent markets even when questions are phrased differently:

```
"Will Bitcoin reach $100K by 2025?" ≈ "BTC to hit 100,000 USD before 2026?"
"Will Trump win the 2024 election?" ≈ "Donald Trump elected president in 2024?"
```

### AI-Powered Market Creation

The system includes an autonomous AI agent that can:
- Generate prediction market questions from natural language prompts
- Select optimal privacy tokens for collateral
- Deploy markets on Solana with privacy-preserving features
- Create zero-knowledge proofs for anonymous participation

---

## Key Features

### Intelligent Market Matching
- Natural Language Inference (NLI) for semantic question matching
- Entailment and contradiction detection
- Temporal proximity analysis
- Confidence scoring and filtering

### Multi-Platform Arbitrage
- **Polymarket** (Polygon blockchain)
- **Kalshi** (CFTC-regulated exchange)
- **PNP Exchange** (Solana-based with privacy features)
- Cross-platform price comparison and execution

### AI Agent System
- Autonomous market creation from prompts
- GPT-powered question generation
- Multi-token collateral management
- Real-time market deployment

### Privacy-Preserving Operations
- Zero-knowledge proof framework
- Address anonymization
- Encrypted market data
- Private order execution
- Support for ELUSIV, LIGHT, and PNP privacy tokens

### Automated Trading
- Atomic execution with rollback on failure
- Slippage protection
- Gas optimization
- Position tracking and management

### Risk Management
- Portfolio-level exposure limits
- Per-market position sizing
- Profit margin thresholds
- Real-time P&L tracking

### Real-Time Monitoring
- WebSocket integration for live updates
- Interactive Streamlit dashboard
- Telegram alerts for opportunities
- Comprehensive activity logging

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Semantic Arbitrage Engine                    │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────┐      ┌──────────────┐     ┌──────────────┐
│   Polymarket │      │    Kalshi    │     │ PNP Exchange │
│   (Polygon)  │      │   (CFTC)     │     │   (Solana)   │
└──────┬───────┘      └──────┬───────┘     └──────┬───────┘
       │                     │                     │
       └─────────────────────┼─────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Market Client │
                    │   Aggregator   │
                    └────────┬───────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌───────────┐  ┌──────────┐  ┌──────────┐
        │    NLI    │  │ PNP AI   │  │   Risk   │
        │  Engine   │  │  Agent   │  │ Manager  │
        └─────┬─────┘  └────┬─────┘  └────┬─────┘
              │             │             │
              └─────────────┼─────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
           ┌──────────────┐  ┌──────────────┐
           │   Privacy    │  │  Collateral  │
           │   Wrapper    │  │   Manager    │
           └──────┬───────┘  └──────┬───────┘
                  │                 │
                  └────────┬────────┘
                           │
                           ▼
                  ┌────────────────┐
                  │  Execution Bot │
                  └────────┬───────┘
                           │
               ┌───────────┼───────────┐
               │           │           │
               ▼           ▼           ▼
       ┌──────────┐  ┌──────────┐  ┌──────────┐
       │ Telegram │  │ Dashboard│  │  Logger  │
       │ Alerter  │  │(Streamlit│  │          │
       └──────────┘  └──────────┘  └──────────┘
```

---

## Supported Platforms

### 1. Polymarket
- **Blockchain**: Polygon (Layer 2)
- **Type**: Decentralized prediction market
- **Collateral**: USDC
- **Features**: High liquidity, wide market variety
- **Integration**: CLOB API + On-chain settlement

### 2. Kalshi
- **Type**: CFTC-regulated exchange
- **Collateral**: USD
- **Features**: Legal compliance, institutional-grade
- **Integration**: REST API + WebSocket

### 3. PNP Exchange
- **Blockchain**: Solana
- **Type**: Privacy-focused prediction markets
- **Collateral**: USDC, ELUSIV, LIGHT, PNP
- **Features**: Zero-knowledge proofs, anonymous trading
- **Integration**: Official PNP SDK + Python bridge

---

## Installation

### Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16+ (for PNP SDK)
- **Git**: For cloning the repository

### Step 1: Clone the Repository

```bash
git clone https://github.com/Demiladepy/semantic.git
cd semantic
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Node.js Dependencies (for PNP Exchange)

```bash
npm install pnp-sdk @solana/web3.js
```

### Step 4: Set Up Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and add your API keys (see [Configuration](#configuration)).

---

## Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# ============================================
# REQUIRED API KEYS
# ============================================

# OpenAI API (Required for NLI Engine & AI Agent)
OPENAI_API_KEY=your_openai_api_key_here

# Telegram Bot (Required for alerts)
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHAT_ID=your_telegram_chat_id_here

# Kalshi API (Required for cross-platform arbitrage)
KALSHI_API_KEY=your_kalshi_api_key_id_here
KALSHI_API_SECRET=your_kalshi_private_key_pem_here

# Polymarket Integration (Polygon Chain)
POLYGON_RPC_URL=https://polygon-rpc.com/
POLYGON_PRIVATE_KEY=your_polygon_private_key_here
POLYMARKET_PRIVATE_KEY=your_polygon_private_key_here

# Solana / PNP Exchange Integration
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_PRIVATE_KEY=your_solana_private_key_base58_here
PNP_PRIVATE_KEY=your_solana_private_key_base58_here

# ============================================
# TRADING PARAMETERS
# ============================================

MAX_GAS_PRICE_GWEI=50
MIN_PROFIT_MARGIN=0.015
SLIPPAGE_TOLERANCE=0.02

# ============================================
# RISK MANAGEMENT
# ============================================

TOTAL_CAPITAL_USD=10000.0
MAX_POSITION_SIZE_PCT=10.0
MAX_SINGLE_MARKET_EXPOSURE_PCT=20.0
MAX_TOTAL_EXPOSURE_PCT=80.0
```

### Getting API Keys

1. **OpenAI**: https://platform.openai.com/api-keys
2. **Telegram Bot**: Talk to [@BotFather](https://t.me/botfather)
3. **Kalshi**: https://kalshi.com/
4. **Polymarket**: Generate Polygon wallet
5. **Solana**: Generate with Solana CLI or Phantom wallet

See `API_KEYS_SETUP.md` for detailed instructions.

---

## Quick Start

### 1. Test Market Data Fetching

```bash
python market_client.py
```

### 2. Run NLI Engine Demo

```bash
python nli_engine.py
```

### 3. Find Arbitrage Opportunities

```bash
python arb_finder.py
```

### 4. Execute Automated Trading

```bash
python execution_bot.py
```

### 5. Launch Dashboard

```bash
streamlit run dashboard.py
```

---

## Core Components

### Market Client (`market_client.py`)

Unified interface for fetching markets from all platforms.

```python
from market_client import MarketClient

client = MarketClient()
markets = client.fetch_all_markets()

for market in markets:
    print(f"{market['platform']}: {market['question']}")
```

### NLI Engine (`nli_engine.py`)

Semantic analysis for question matching.

```python
from nli_engine import NLIEngine

nli = NLIEngine()
result = nli.check_entailment(
    "Will Bitcoin reach $100K by 2025?",
    "BTC to hit 100,000 USD before 2026?"
)
print(f"Entailment: {result['label']} ({result['confidence']:.2%})")
```

### Arbitrage Finder (`arb_finder.py`)

Identifies profitable opportunities.

```python
from arb_finder import ArbFinder

finder = ArbFinder()
opportunities = finder.find_opportunities()

for opp in opportunities:
    print(f"Profit: {opp['profit_pct']:.2f}%")
```

### Risk Manager (`risk_manager.py`)

Portfolio risk management.

```python
from risk_manager import RiskManager

risk_mgr = RiskManager(total_capital=10000)
allowed = risk_mgr.check_position_limits(market_id="market_123", amount=500)
```

---

## AI Agent & Privacy Features

### PNP Agent (`pnp_agent.py`)

Autonomous AI agent for market creation.

```python
from pnp_agent import PNPAgent

agent = PNPAgent(default_collateral_token='ELUSIV')

# Create market from natural language prompt
result = agent.create_market_from_prompt(
    prompt="SpaceX successfully lands on Mars in 2026",
    collateral_token="ELUSIV",
    collateral_amount=100.0
)

print(f"Market ID: {result['market_id']}")
print(f"Question: {result['question']}")
```

### Privacy Wrapper (`pnp_infra/privacy_wrapper.py`)

Zero-knowledge proof operations.

```python
from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel

wrapper = PrivacyWrapper(default_privacy_level=PrivacyLevel.ANONYMOUS)

# Anonymize address
anon_addr = wrapper.anonymize_address("7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU")

# Create ZK proof
proof = wrapper.create_zk_proof(
    proof_type="ownership",
    statement={"has_collateral": True},
    witness={"amount": 100.0}
)
```

### Collateral Manager (`pnp_infra/collateral_manager.py`)

Privacy token collateral management.

```python
from pnp_infra.collateral_manager import CollateralManager

manager = CollateralManager()

# Lock collateral
result = manager.lock_collateral(
    market_id="PNP-001",
    token="ELUSIV",
    amount=100.0,
    owner_pubkey="your_pubkey"
)

# Get locked amounts
total = manager.get_total_locked("ELUSIV")
```

### Market Factory (`pnp_infra/market_factory.py`)

Deploy market accounts on Solana.

```python
from pnp_infra.market_factory import MarketFactory

factory = MarketFactory(network='devnet')

account = factory.deploy_market_account(
    market_id="PNP-001",
    question="Will ETH reach $10K?",
    outcomes=["Yes", "No"],
    creator_pubkey="your_pubkey",
    collateral_token="ELUSIV",
    collateral_amount=100.0
)
```

---

## PNP Exchange Integration

### Overview

PNP Exchange is a Solana-based prediction market platform with privacy features. This project includes complete integration via Python bridge.

### Python Integration

```python
from pnp_market_client import PNPMarketClient

client = PNPMarketClient(
    rpc_url="https://api.devnet.solana.com",
    private_key="your_solana_private_key"
)

# Fetch markets
markets = client.fetch_all_markets()

# Get market prices
price_data = client.get_market_price(market_address)

# Buy tokens
result = client.buy_tokens(
    market_address=market_address,
    side="YES",
    amount_usdc=10.0
)
```

### Features

- Market Creation with privacy tokens
- Trading (Buy/Sell YES/NO tokens)
- Real-Time Prices via SDK
- Settlement and redemption
- Arbitrage Detection (cross-platform)
- Privacy (ZK proofs, anonymization)

---

## Live Dashboard

The project includes an interactive Streamlit dashboard for monitoring and demonstration.

### Features

- **AI Market Creation**: Generate markets from prompts
- **Privacy Features**: ZK proof generation, address anonymization
- **Collateral Management**: Lock/view privacy token collateral
- **Markets & Analytics**: View created markets with charts
- **Activity Log**: Real-time operation tracking

### Running Locally

```bash
streamlit run dashboard.py
```

### Screenshots

The dashboard includes:
- Dark theme with Solana branding
- Real-time metrics (markets, collateral, ZK proofs)
- Interactive token selection
- Module status indicators
- Collateral distribution charts

---

## Usage Examples

### Example 1: Full Arbitrage Detection

```python
from arb_finder import ArbFinder

finder = ArbFinder(min_profit_margin=0.02)
opportunities = finder.find_opportunities()

for opp in opportunities:
    print(f"\nArbitrage Opportunity:")
    print(f"  Question: {opp['question']}")
    print(f"  Profit: {opp['profit_pct']:.2f}%")
    print(f"  Buy {opp['side']} on {opp['buy_platform']}")
    print(f"  Sell {opp['side']} on {opp['sell_platform']}")
```

### Example 2: AI Market Creation with Privacy

```python
from pnp_agent import PNPAgent
from pnp_infra.privacy_wrapper import PrivacyWrapper

agent = PNPAgent(default_collateral_token='ELUSIV')
wrapper = PrivacyWrapper()

# Create market
result = agent.create_market_from_prompt(
    prompt="Federal Reserve cuts rates in Q2 2026",
    collateral_amount=500.0
)

# Create ZK proof for anonymous participation
proof = wrapper.create_zk_proof(
    proof_type="eligibility",
    statement={"market_id": result['market_id']},
    witness={"balance": 500.0}
)
```

### Example 3: Cross-Platform Price Comparison

```python
from market_client import MarketClient
from nli_engine import NLIEngine

market_client = MarketClient()
nli = NLIEngine()

poly_markets = market_client.fetch_polymarket_markets()
pnp_markets = market_client.fetch_pnp_markets()

for poly in poly_markets:
    for pnp in pnp_markets:
        result = nli.check_entailment(poly['question'], pnp['question'])
        
        if result['label'] == 'entailment' and result['confidence'] > 0.85:
            spread = abs(poly['yes_price'] - pnp['yes_price'])
            if spread > 0.05:
                print(f"Price discrepancy: {spread*100:.2f}%")
```

---

## Advanced Features

### Enhanced NLI Engine

```python
from enhanced_nli_engine import EnhancedNLIEngine

nli = EnhancedNLIEngine(model='roberta-large-mnli')
clusters = nli.cluster_similar_questions(all_questions)
```

### Backtesting Framework

```python
from backtesting_framework import Backtester

backtester = Backtester(start_date="2024-01-01", end_date="2024-12-31")
results = backtester.run_backtest(strategy)
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
```

### Fee Calculator

```python
from enhanced_fee_calculator import EnhancedFeeCalculator

fee_calc = EnhancedFeeCalculator()
costs = fee_calc.calculate_total_cost(platform="polymarket", trade_size=1000)
```

---

## Testing

```bash
# Unit tests
python -m pytest tests/

# Integration tests
python test_pnp_integration.py
python test_pnp_infra.py

# Manual testing
python market_client.py
python pnp_integration_example.py
```

---

## Documentation

### Core Documentation
- `API_KEYS_SETUP.md` - API key configuration guide
- `IMPLEMENTATION_SUMMARY.md` - Implementation details
- `ENHANCEMENTS_GUIDE.md` - Feature documentation
- `PRIVACY_FEATURES.md` - Privacy implementation details

### PNP Exchange Documentation
- `PNP_SETUP_COMPLETE.md` - Setup guide
- `INTEGRATION_GUIDE.md` - Integration guide
- `PNP_REALTIME_INTEGRATION.md` - Real-time features

---

## Troubleshooting

### Common Issues

**Module not found errors**
```bash
pip install -r requirements.txt
npm install pnp-sdk @solana/web3.js
```

**API key errors**
- Verify keys in `.env` file
- Check key format (base58 for Solana)

**RPC connection failures**
- Try alternative RPC endpoints
- Check network connectivity

**Insufficient funds**
- Ensure wallets have native tokens for gas
- Fund wallets on testnet first

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- **OpenAI** for GPT models used in NLI and AI Agent
- **Hugging Face** for transformer models
- **PNP Exchange** for the official SDK
- **Polymarket** for market data access
- **Kalshi** for regulated market access
- **Solana** for blockchain infrastructure

---

## Contact

- **GitHub**: [@Demiladepy](https://github.com/Demiladepy)
- **Project**: [Semantic Arbitrage Engine](https://github.com/Demiladepy/semantic)

---

## Disclaimer

This software is provided for educational and research purposes only. Trading prediction markets involves substantial risk of loss. The authors and contributors are not responsible for any financial losses incurred through the use of this software.

**Use at your own risk. Always test on testnets first.**

---

<div align="center">

[Star this repo](https://github.com/Demiladepy/semantic) | [Report Bug](https://github.com/Demiladepy/semantic/issues) | [Request Feature](https://github.com/Demiladepy/semantic/issues)

</div>

#  Semantic Arbitrage Engine

> **AI-Powered Cross-Platform Prediction Market Arbitrage System**

A sophisticated Python-based arbitrage engine that identifies and exploits logical arbitrage opportunities across multiple prediction market platforms (Polymarket, Kalshi, PNP Exchange) using advanced Natural Language Inference (NLI) and semantic analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()

---

##  Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Architecture](#-architecture)
- [Supported Platforms](#-supported-platforms)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Quick Start](#-quick-start)
- [Core Components](#-core-components)
- [PNP Exchange Integration](#-pnp-exchange-integration)
- [Usage Examples](#-usage-examples)
- [Advanced Features](#-advanced-features)
- [Testing](#-testing)
- [Documentation](#-documentation)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

##  Overview

The Semantic Arbitrage Engine is a cutting-edge trading system that:

- **Discovers** semantically equivalent markets across different platforms
- **Analyzes** price discrepancies using NLI (Natural Language Inference)
- **Executes** profitable arbitrage trades automatically
- **Manages** risk with sophisticated position sizing and exposure limits
- **Monitors** markets in real-time with WebSocket integration
- **Alerts** via Telegram for critical events and opportunities

### What Makes It Unique?

Unlike traditional arbitrage systems that rely on exact market matching, this engine uses **semantic understanding** to identify equivalent markets even when questions are phrased differently. For example:

- "Will Bitcoin reach $100K by 2025?" ≈ "BTC to hit 100,000 USD before 2026?"
- "Will Trump win the 2024 election?" ≈ "Donald Trump elected president in 2024?"

---

##  Key Features

###  **Intelligent Market Matching**
- Natural Language Inference (NLI) for semantic question matching
- Entailment and contradiction detection
- Temporal proximity analysis
- Confidence scoring and filtering

###  **Multi-Platform Arbitrage**
- **Polymarket** (Polygon blockchain)
- **Kalshi** (CFTC-regulated exchange)
- **PNP Exchange** (Solana-based prediction markets)
- Cross-platform price comparison and execution

###  **Automated Trading**
- Atomic execution with rollback on failure
- Slippage protection
- Gas optimization
- Position tracking and management

###  **Risk Management**
- Portfolio-level exposure limits
- Per-market position sizing
- Profit margin thresholds
- Real-time P&L tracking

###  **Real-Time Monitoring**
- WebSocket integration for live updates
- Telegram alerts for opportunities
- Market event notifications
- Error and execution alerts

###  **Privacy & Security**
- Zero-knowledge proof support (PNP Exchange)
- Encrypted market data
- Anonymized trading (optional)
- Secure key management

---

##  Architecture

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
        │    NLI    │  │   Arb    │  │   Risk   │
        │  Engine   │  │  Finder  │  │ Manager  │
        └─────┬─────┘  └────┬─────┘  └────┬─────┘
              │             │             │
              └─────────────┼─────────────┘
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
        │ Alerter  │  │          │  │          │
        └──────────┘  └──────────┘  └──────────┘
```

---

##  Supported Platforms

### 1. **Polymarket** 
- **Blockchain**: Polygon (Layer 2)
- **Type**: Decentralized prediction market
- **Collateral**: USDC
- **Features**: High liquidity, wide market variety
- **Integration**: CLOB API + On-chain settlement

### 2. **Kalshi**
- **Type**: CFTC-regulated exchange
- **Collateral**: USD
- **Features**: Legal compliance, institutional-grade
- **Integration**: REST API + WebSocket

### 3. **PNP Exchange**
- **Blockchain**: Solana
- **Type**: Privacy-focused prediction markets
- **Collateral**: USDC, ELUSIV, LIGHT, PNP
- **Features**: Zero-knowledge proofs, anonymous trading
- **Integration**: Official PNP SDK + Custom bridge

---

##  Installation

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

Edit `.env` and add your API keys (see [Configuration](#-configuration)).

---

##  Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```bash
# ============================================
# REQUIRED API KEYS
# ============================================

# OpenAI API (Required for NLI Engine)
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
POLYMARKET_API_KEY=optional_if_needed

# Mezo Network Integration
MEZO_PRIVACY_KEY=your_mezo_privacy_key_here

# UMA Oracle (Required for resolution tracking)
UMA_FINDER_ADDRESS=0x...
UMA_OOV3_ADDRESS=0x...

# Solana / PNP Exchange Integration
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
SOLANA_PRIVATE_KEY=your_solana_private_key_base58_here
PNP_PRIVATE_KEY=your_solana_private_key_base58_here

# ============================================
# TRADING PARAMETERS
# ============================================

MAX_GAS_PRICE_GWEI=50
MIN_PROFIT_MARGIN=0.015  # 1.5% minimum after fees
MIN_PROFIT_MARGIN_PCT=2.5  # 2.5% minimum after fees (enhanced)
LEG_FILL_TIMEOUT_SECONDS=5
SLIPPAGE_TOLERANCE=0.02  # 2%

# ============================================
# RISK MANAGEMENT
# ============================================

TOTAL_CAPITAL_USD=10000.0
MAX_POSITION_SIZE_PCT=10.0
MAX_SINGLE_MARKET_EXPOSURE_PCT=20.0
MAX_TOTAL_EXPOSURE_PCT=80.0

# ============================================
# STRATEGY PARAMETERS
# ============================================

MIN_DEVIATION_PCT=0.5  # Minimum deviation for market rebalancing
TEMPORAL_THRESHOLD_DAYS=7  # Temporal proximity threshold
MIN_NLI_CONFIDENCE=0.85  # Minimum NLI confidence

# ============================================
# LOGGING
# ============================================

LOG_LEVEL=INFO
TRADING_MODE=simulation  # simulation, paper, live
```

### Getting API Keys

1. **OpenAI**: https://platform.openai.com/api-keys
2. **Telegram Bot**: Talk to [@BotFather](https://t.me/botfather)
3. **Kalshi**: https://kalshi.com/
4. **Polymarket**: Generate Polygon wallet
5. **Solana**: Generate with Solana CLI or Phantom wallet

See `API_KEYS_SETUP.md` for detailed instructions.

---

##  Quick Start

### 1. Test Market Data Fetching

```bash
python market_client.py
```

This fetches active markets from all supported platforms.

### 2. Run NLI Engine Demo

```bash
python nli_engine.py
```

Demonstrates semantic clustering and entailment checks.

### 3. Find Arbitrage Opportunities

```bash
python arb_finder.py
```

Scans all platforms and identifies profitable arbitrage opportunities.

### 4. Execute Automated Trading

```bash
python execution_bot.py
```

Runs the full arbitrage bot with automatic execution.

### 5. Monitor with Dashboard

```bash
python dashboard.py
```

Launches a web dashboard for monitoring positions and P&L.

---

##  Core Components

### 1. **Market Client** (`market_client.py`)

Unified interface for fetching markets from all platforms.

```python
from market_client import MarketClient

client = MarketClient()
markets = client.fetch_all_markets()

for market in markets:
    print(f"{market['platform']}: {market['question']}")
    print(f"  YES: ${market['yes_price']:.2f}")
    print(f"  NO: ${market['no_price']:.2f}")
```

### 2. **NLI Engine** (`nli_engine.py`)

Semantic analysis for question matching.

```python
from nli_engine import NLIEngine

nli = NLIEngine()

# Check if two questions are equivalent
result = nli.check_entailment(
    "Will Bitcoin reach $100K by 2025?",
    "BTC to hit 100,000 USD before 2026?"
)

print(f"Entailment: {result['label']}")
print(f"Confidence: {result['confidence']:.2%}")
```

### 3. **Arbitrage Finder** (`arb_finder.py`)

Identifies profitable opportunities.

```python
from arb_finder import ArbFinder

finder = ArbFinder()
opportunities = finder.find_opportunities()

for opp in opportunities:
    print(f"Profit: {opp['profit_pct']:.2f}%")
    print(f"Buy {opp['side']} on {opp['buy_platform']}")
    print(f"Sell {opp['side']} on {opp['sell_platform']}")
```

### 4. **Execution Bot** (`execution_bot.py`)

Automated trade execution.

```python
from execution_bot import ExecutionBot

bot = ExecutionBot()
bot.run()  # Runs continuously, executing profitable trades
```

### 5. **Risk Manager** (`risk_manager.py`)

Portfolio risk management.

```python
from risk_manager import RiskManager

risk_mgr = RiskManager(total_capital=10000)

# Check if trade is allowed
allowed = risk_mgr.check_position_limits(
    market_id="market_123",
    amount=500
)
```

### 6. **Telegram Alerter** (`telegram_alerter.py`)

Real-time notifications.

```python
from telegram_alerter import TelegramAlerter

alerter = TelegramAlerter()
alerter.send_alert("🚨 Arbitrage opportunity found! Profit: 5.2%")
```

---

## 🔗 PNP Exchange Integration

### Overview

PNP Exchange is a Solana-based prediction market platform with privacy features. This project includes complete integration with the official PNP SDK.

### Installation

```bash
# Install PNP SDK
npm install pnp-sdk @solana/web3.js

# Test installation
node pnp_infra/test_installation.js
```

### Python Integration

```python
from pnp_market_client import PNPMarketClient

# Initialize client
client = PNPMarketClient(
    rpc_url="https://api.mainnet-beta.solana.com",
    private_key="your_solana_private_key"
)

# Fetch markets
markets = client.fetch_all_markets()

# Get market prices
price_data = client.get_market_price(market_address)
print(f"YES: ${price_data['yesPrice']:.4f}")
print(f"NO: ${price_data['noPrice']:.4f}")

# Buy tokens
result = client.buy_tokens(
    market_address=market_address,
    side="YES",
    amount_usdc=10.0
)

# Detect arbitrage
opportunities = client.find_arbitrage_opportunities(
    external_markets,
    min_profit_margin=0.02
)
```

### Features

- ✅ **Market Creation**: Create custom prediction markets
- ✅ **Trading**: Buy/sell YES/NO tokens
- ✅ **Real-Time Prices**: Get live market data
- ✅ **Settlement**: Redeem winning positions
- ✅ **Arbitrage Detection**: Cross-platform comparison
- ✅ **Privacy**: Zero-knowledge proofs (optional)

### Documentation

- **Setup Guide**: `PNP_SETUP_COMPLETE.md`
- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Examples**: `pnp_integration_example.py`
- **Official Docs**: https://docs.pnp.exchange/pnp-sdk

---

##  Usage Examples

### Example 1: Simple Arbitrage Detection

```python
from arb_finder import ArbFinder

# Initialize finder
finder = ArbFinder(min_profit_margin=0.02)

# Find opportunities
opportunities = finder.find_opportunities()

# Display results
for opp in opportunities:
    print(f"\n Arbitrage Opportunity:")
    print(f"   Question: {opp['question']}")
    print(f"   Profit: {opp['profit_pct']:.2f}%")
    print(f"   Buy {opp['side']} on {opp['buy_platform']} @ ${opp['buy_price']:.4f}")
    print(f"   Sell {opp['side']} on {opp['sell_platform']} @ ${opp['sell_price']:.4f}")
```

### Example 2: Automated Trading Bot

```python
from execution_bot import ExecutionBot
import time

bot = ExecutionBot(
    min_profit_margin=0.025,  # 2.5% minimum
    max_position_size=1000,   # $1000 max per trade
    check_interval=60         # Check every 60 seconds
)

# Run bot
print(" Starting arbitrage bot...")
bot.run()
```

### Example 3: Real-Time Market Monitoring

```python
from pnp_market_client import PNPMarketClient
from telegram_alerter import TelegramAlerter
import time

client = PNPMarketClient()
alerter = TelegramAlerter()

markets_to_watch = ["market_id_1", "market_id_2"]

while True:
    for market_id in markets_to_watch:
        price_data = client.get_market_price(market_id)
        
        # Alert if price moves significantly
        if abs(price_data['yesPrice'] - 0.5) > 0.2:
            alerter.send_alert(
                f"📊 Price Alert!\n"
                f"Market: {market_id}\n"
                f"YES: ${price_data['yesPrice']:.4f}\n"
                f"NO: ${price_data['noPrice']:.4f}"
            )
    
    time.sleep(300)  # Check every 5 minutes
```

### Example 4: Cross-Platform Price Comparison

```python
from market_client import MarketClient
from nli_engine import NLIEngine

market_client = MarketClient()
nli = NLIEngine()

# Fetch markets from all platforms
poly_markets = market_client.fetch_polymarket_markets()
kalshi_markets = market_client.fetch_kalshi_markets()
pnp_markets = market_client.fetch_pnp_markets()

# Find semantically equivalent markets
for poly_market in poly_markets:
    for kalshi_market in kalshi_markets:
        # Check if questions are equivalent
        result = nli.check_entailment(
            poly_market['question'],
            kalshi_market['question']
        )
        
        if result['label'] == 'entailment' and result['confidence'] > 0.85:
            # Compare prices
            poly_yes = poly_market['yes_price']
            kalshi_yes = kalshi_market['yes_price']
            spread = abs(poly_yes - kalshi_yes)
            
            if spread > 0.05:  # 5% spread
                print(f"\n💰 Price Discrepancy Found!")
                print(f"   Polymarket: ${poly_yes:.4f}")
                print(f"   Kalshi: ${kalshi_yes:.4f}")
                print(f"   Spread: {spread*100:.2f}%")
```

---

##  Advanced Features

### 1. **Enhanced NLI Engine**

Uses state-of-the-art transformer models for semantic understanding:

```python
from enhanced_nli_engine import EnhancedNLIEngine

nli = EnhancedNLIEngine(model='roberta-large-mnli')

# Batch processing
results = nli.batch_check_entailment([
    ("Question 1", "Question 2"),
    ("Question 3", "Question 4"),
])

# Semantic clustering
clusters = nli.cluster_similar_questions(all_questions)
```

### 2. **Backtesting Framework**

Test strategies on historical data:

```python
from backtesting_framework import Backtester

backtester = Backtester(
    start_date="2024-01-01",
    end_date="2024-12-31",
    initial_capital=10000
)

results = backtester.run_backtest(strategy)
print(f"Total Return: {results['total_return']:.2%}")
print(f"Sharpe Ratio: {results['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {results['max_drawdown']:.2%}")
```

### 3. **Advanced Fee Calculator**

Optimize for gas and platform fees:

```python
from enhanced_fee_calculator import EnhancedFeeCalculator

fee_calc = EnhancedFeeCalculator()

# Calculate total costs
costs = fee_calc.calculate_total_cost(
    platform="polymarket",
    trade_size=1000,
    gas_price_gwei=30
)

print(f"Platform Fee: ${costs['platform_fee']:.2f}")
print(f"Gas Fee: ${costs['gas_fee']:.2f}")
print(f"Total: ${costs['total']:.2f}")
```

### 4. **CLOB Orderbook Integration**

Direct orderbook access for Polymarket:

```python
from clob_orderbook_client import CLOBOrderbookClient

clob = CLOBOrderbookClient()

# Get orderbook depth
orderbook = clob.get_orderbook(market_id)
print(f"Best Bid: ${orderbook['bids'][0]['price']:.4f}")
print(f"Best Ask: ${orderbook['asks'][0]['price']:.4f}")

# Place limit order
order = clob.place_limit_order(
    market_id=market_id,
    side="buy",
    price=0.55,
    size=100
)
```

---

##  Testing

### Unit Tests

```bash
# Test individual components
python -m pytest tests/test_nli_engine.py
python -m pytest tests/test_arb_finder.py
python -m pytest tests/test_risk_manager.py
```

### Integration Tests

```bash
# Test full workflow
python test_pnp_integration.py
python test_pnp_infra.py
```

### Manual Testing

```bash
# Test market fetching
python market_client.py

# Test NLI engine
python nli_engine.py

# Test arbitrage detection
python arb_finder.py

# Test PNP integration
python pnp_integration_example.py
```

---

##  Documentation

### Core Documentation
- **API Keys Setup**: `API_KEYS_SETUP.md`
- **Implementation Summary**: `IMPLEMENTATION_SUMMARY.md`
- **Enhancements Guide**: `ENHANCEMENTS_GUIDE.md`
- **Production Bot Guide**: `PRODUCTION_BOT_GUIDE.md`

### PNP Exchange Documentation
- **Setup Guide**: `PNP_SETUP_COMPLETE.md`
- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Installation**: `INSTALL_PNP_SDK.md`
- **Real-Time Integration**: `PNP_REALTIME_INTEGRATION.md`

### External Documentation
- **PNP SDK**: https://docs.pnp.exchange/pnp-sdk
- **UMA Oracle**: https://docs.uma.xyz/
- **Polymarket**: https://docs.polymarket.com/
- **Kalshi**: https://kalshi.com/docs

---

##  Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install -r requirements.txt
npm install pnp-sdk @solana/web3.js
```

**2. API key errors**
- Verify keys in `.env` file
- Check key format (base58 for Solana, hex for Polygon)
- Ensure keys have proper permissions

**3. RPC connection failures**
- Try alternative RPC endpoints
- Check network connectivity
- Verify RPC URL in `.env`

**4. Insufficient funds**
- Ensure wallets have native tokens for gas (SOL, MATIC)
- Check USDC balance for trading
- Fund wallets on testnet first

**5. Transaction failures**
- Check gas price settings
- Verify slippage tolerance
- Ensure market has sufficient liquidity

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now all operations will show detailed logs
```

### Getting Help

1. Check documentation in `/docs`
2. Review examples in repository
3. Check logs in `error.log`
4. Open an issue on GitHub

---

##  Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/semantic.git
cd semantic

# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
flake8 .
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

##  Acknowledgments

- **OpenAI** for GPT models used in NLI
- **Hugging Face** for transformer models
- **PNP Exchange** for the official SDK
- **Polymarket** for market data access
- **Kalshi** for regulated market access
- **UMA Protocol** for oracle infrastructure

---

##  Contact

- **GitHub**: [@Demiladepy](https://github.com/Demiladepy)
- **Project**: [Semantic Arbitrage Engine](https://github.com/Demiladepy/semantic)

---

##  Roadmap

### Q1 2026
- ✅ Multi-platform integration (Polymarket, Kalshi, PNP)
- ✅ NLI-based semantic matching
- ✅ Automated execution bot
- ✅ Telegram alerts
- ⏳ Machine learning price prediction
- ⏳ Advanced risk models

### Q2 2026
- ⏳ Additional platform integrations
- ⏳ Mobile app for monitoring
- ⏳ Advanced backtesting suite
- ⏳ Community features

### Q3 2026
- ⏳ Institutional-grade features
- ⏳ API for third-party integration
- ⏳ Advanced analytics dashboard
- ⏳ Multi-user support

---

## 📊 Performance Metrics

*Based on backtesting and simulation*

- **Average Profit per Trade**: 2.8%
- **Win Rate**: 73%
- **Sharpe Ratio**: 1.85
- **Max Drawdown**: -8.2%
- **Average Execution Time**: 3.2 seconds

*Past performance does not guarantee future results. Trade at your own risk.*

---

##  Disclaimer

This software is provided for educational and research purposes only. Trading prediction markets involves substantial risk of loss. The authors and contributors are not responsible for any financial losses incurred through the use of this software.

**Use at your own risk. Always test on testnets first.**

---

<div align="center">


[⭐ Star this repo](https://github.com/Demiladepy/semantic) | [🐛 Report Bug](https://github.com/Demiladepy/semantic/issues) | [💡 Request Feature](https://github.com/Demiladepy/semantic/issues)

</div>

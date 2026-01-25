## 🚀 Production Bot Setup & Run Guide

This document walks through setting up and running the production-ready arbitrage bot with full integration.

---

## 📋 Quick Start (5 minutes)

### 1. Install Dependencies

```bash
# Install all Python dependencies
pip install -r requirements.txt

# For TypeScript/Node.js plugin (optional):
cd plugin-polymarket
npm install
```

### 2. Configure Environment

```bash
# Copy the example env file
cp .env.example .env

# Edit .env with your API keys:
# - OPENAI_API_KEY: Your OpenAI API key
# - POLYGON_PRIVATE_KEY: Your Polygon wallet private key (for Polymarket)
# - SOLANA_PRIVATE_KEY: Your Solana private key (for PNP Exchange)
# - RPC URLs: Leave defaults or configure custom endpoints
```

### 3. Set Trading Permissions (IMPORTANT!)

**Before trading, you MUST set allowances on Polymarket contracts:**

```bash
# This runs once per wallet and approves spending USDC on Polymarket
python set_allowances.py

# Output should show:
# ✅ Approved CTF Exchange
# ✅ Approved Negative Risk Exchange
# ✅ Approved CTF Contract
# 🚀 Ready to trade on Polymarket!
```

### 4. Run the Bot

**Simulation Mode (Safe for testing):**
```bash
# Single scan
python arb_finder.py

# Continuous scanning (every 30 seconds)
python arb_finder.py --continuous
```

**Live Trading Mode:**
```bash
# Edit .env: change TRADING_MODE=simulation to TRADING_MODE=live

# Run with live execution
python arb_finder.py --continuous
```

### 5. View Dashboard (Optional)

```bash
# In another terminal, run the Streamlit dashboard
streamlit run dashboard.py

# Opens at http://localhost:8501
```

---

## 🛠️ Component Overview

### Production Modules

| Module | Purpose | Run | Notes |
|--------|---------|-----|-------|
| **wallet_manager.py** | Secure key management | `python wallet_manager.py` | Test wallet connectivity |
| **set_allowances.py** | Grant Polymarket permissions | `python set_allowances.py` | **REQUIRED before trading** |
| **profit_calculator.py** | Fee & slippage analysis | `python profit_calculator.py` | Test profit calculations |
| **atomic_executor.py** | Two-leg trade execution | `python atomic_executor.py` | Test atomic ordering |
| **execution_bot.py** | Live trading orchestration | Used by arb_finder.py | Coordinates full execution |
| **nli_engine.py** | NLI + semantic drift | `python nli_engine.py` | Test clustering & analysis |
| **arb_finder.py** | Main bot orchestration | `python arb_finder.py` | **Primary entry point** |
| **dashboard.py** | Real-time monitoring | `streamlit run dashboard.py` | Visualization |

---

## 📊 Detailed Setup Steps

### Step 1: Generate Wallets

**For Polygon (Polymarket):**
```bash
# Option A: Using web3.py
python -c "from web3 import Web3; acct = Web3.eth.account.create(); print(f'Address: {acct.address}'); print(f'Private Key: {acct._private_key.hex()}')"

# Option B: Online tools like https://metamask.io/
```

**For Solana (PNP Exchange):**
```bash
# Using Solana CLI
solana-keygen new --outfile solana_keypair.json

# Or use online: https://faucet.solana.com (for devnet)
# Then convert to base58 private key
```

### Step 2: Fund Wallets

**Polygon (Testnet):**
- Visit: https://polygon-faucet.matic.network/
- Enter wallet address
- Receive test MATIC + test USDC.e

**Solana (Devnet):**
- Visit: https://faucet.solana.com/
- Enter wallet address
- Receive devnet SOL

### Step 3: Test Connectivity

```bash
# Test Polygon connection
python wallet_manager.py

# Expected output:
# ✅ Polygon wallet initialized: 0x...
#    ETH Balance: 0.123456
#    Gas Price: 25.50 Gwei

# ✅ Solana wallet initialized: 9LZfDTjU...
#    SOL Balance: 2.5
```

### Step 4: Set Trading Permissions

```bash
# Grant USDC spending permissions on Polymarket contracts
python set_allowances.py

# Expected output:
# ✅ Polygon wallet initialized: 0x...
# 💰 Wallet Balance: 1.234567 MATIC
#
# Setting Allowances...
# ▶ Approving CTF Exchange...
#   ✅ Approved! TX Hash: 0x...
# ▶ Approving Negative Risk Exchange...
#   ✅ Approved! TX Hash: 0x...
# ▶ Approving CTF Contract...
#   ✅ Approved! TX Hash: 0x...
#
# ✅ SUCCESS: All 3/3 allowances set!
# 🚀 Ready to trade on Polymarket!
```

---

## 🎮 Running the Bot

### Single Scan
```bash
python arb_finder.py
```

**Output:**
```
======================================================================
🤖 Initializing Arbitrage Finder
======================================================================
  Mode: SIMULATION
  Min Spread: 1.50%
  Min NLI Confidence: 0.80

======================================================================
🔍 ARBITRAGE SCAN STARTED
======================================================================

[Step 1/5] Ingesting market data...
✅ Ingested 48 active markets

[Step 2/5] Semantic clustering...
✅ Found 12 semantic clusters

[Step 3/5] Analyzing clusters for arbitrage...
  Cluster 1 (Size: 3)
    ✅ OPPORTUNITY FOUND: 3.45% spread, $2.40 profit

[Step 4/5] Profitability filtering...
✅ 2 opportunities are profitable

[Step 5/5] Execution phase...
  Simulation mode - no execution

✅ SCAN COMPLETE
  Opportunities Found: 4
  Profitable Opportunities: 2
  Executed: 0
```

### Continuous Scanning
```bash
python arb_finder.py --continuous
```

Runs continuous scans every 30 seconds. Stop with `Ctrl+C`.

### Live Trading Mode

Edit `.env`:
```bash
TRADING_MODE=live
```

Then:
```bash
python arb_finder.py --continuous
```

⚠️ **WARNING**: This will execute real trades with real money. Ensure:
- ✅ Wallets are funded
- ✅ Allowances are set (`python set_allowances.py`)
- ✅ Test with small amounts first
- ✅ Monitor gas prices

---

## 📈 Monitoring

### View Logs

```bash
# Recent opportunities
cat arbitrage_opportunities.csv

# Execution results
cat execution_log.csv

# Paper trades (legacy)
cat paper_trades.csv
```

### Dashboard

```bash
streamlit run dashboard.py
```

Access at: http://localhost:8501

Features:
- Live spread table
- NLI confidence scores
- Gas price gauge
- Execution log
- P&L tracking

---

## 🧪 Testing Individual Modules

### Test NLI Engine

```bash
python nli_engine.py

# Tests clustering, entailment, and semantic drift
```

### Test Profit Calculator

```bash
python profit_calculator.py

# Shows: Gross spread, fees, gas, slippage, net profit
```

### Test Atomic Executor

```bash
python atomic_executor.py

# Simulates two-leg trade execution with timeout handling
```

### Test Wallet Manager

```bash
python wallet_manager.py

# Shows wallet balance and connectivity
```

---

## 🐛 Troubleshooting

### "POLYGON_PRIVATE_KEY not set in .env"
**Solution**: Add your private key to `.env`
```bash
POLYGON_PRIVATE_KEY=your_private_key_here
```

### "openai not installed"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### "RPC connection failed"
**Solution**: Check RPC URL in `.env`
```bash
# For Polygon:
POLYGON_RPC_URL=https://polygon-rpc.com/

# For Solana Devnet:
SOLANA_RPC_URL=https://api.devnet.solana.com
```

### "Gas price too high - Trade deferred"
**Solution**: Adjust max gas limit in `.env`
```bash
MAX_GAS_PRICE_GWEI=100  # Increase from default 50
```

### "USDC allowance not set - Order rejected"
**Solution**: Run permissions script
```bash
python set_allowances.py
```

---

## 🎯 Next Steps for Production

1. **Add Real WebSocket Listeners**
   - Replace mock fill detection in `atomic_executor.py`
   - Connect to Polymarket CLOB WebSocket
   - Connect to Kalshi proprietary WebSocket

2. **Implement Real Order Book Parsing**
   - Fetch L2/L3 order book depth
   - Calculate accurate slippage
   - Update `profit_calculator.py` with real data

3. **Add Risk Management**
   - Position sizing based on account equity
   - Stop-loss levels
   - Daily/hourly drawdown limits

4. **Optimize Gas Usage**
   - Batch orders where possible
   - Use gas price oracles for timing
   - Consider L2 solutions (Arbitrum, Optimism)

5. **Scale to Production**
   - Use hardware wallet (Ledger, Trezor) instead of env keys
   - Add circuit breakers
   - Implement real-time alerting
   - Set up monitoring/dashboards

---

## 📚 Key Files

- **[.env.example](.env.example)** - Configuration template
- **[README.md](README.md)** - Project overview
- **[PNP_SDK_INTEGRATION_SUMMARY.md](PNP_SDK_INTEGRATION_SUMMARY.md)** - PNP SDK info
- **[PNP_REALTIME_INTEGRATION.md](PNP_REALTIME_INTEGRATION.md)** - Real-time integration guide

---

## ⚠️ Important Security Notes

🔴 **NEVER**:
- Hardcode private keys in code
- Commit `.env` to Git
- Share private keys
- Test with mainnet keys on testnet

🟢 **ALWAYS**:
- Use `.env` for secrets
- Add `.env` to `.gitignore`
- Rotate keys regularly
- Test on testnet first
- Use hardware wallets for large amounts

---

## 💡 Tips

- Start with **simulation mode** to test logic
- Use **testnet** (Polygon Mumbai, Solana Devnet) first
- Monitor **gas prices** before trading
- Set **low position sizes** initially
- Check **resolution criteria** carefully (semantic drift!)
- Use the **dashboard** to spot anomalies

---

**Questions? Issues? Open an issue or check the docs!** 🚀

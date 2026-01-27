# Quick API Keys Setup Guide

This guide helps you quickly generate and configure all required API keys for the arbitrage bot.

## 🚀 Quick Setup (5 Minutes)

### 1. Telegram Bot (30 seconds)

**Fastest Method:**
1. Open Telegram app
2. Search for `@BotFather`
3. Send: `/newbot`
4. Follow prompts:
   - Bot name: `Arbitrage Bot`
   - Bot username: `your_arbitrage_bot` (must end in `bot`)
5. **Copy the token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

**Get Your Chat ID:**
1. Search for your bot in Telegram
2. Send any message to it
3. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
4. Find `"chat":{"id":123456789}` - that's your chat ID

**Add to `.env`:**
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

---

### 2. Kalshi API (2 minutes)

**Steps:**
1. Go to https://kalshi.com
2. Sign up / Log in
3. Go to **Settings** → **API Keys**
4. Click **Generate New API Key**
5. **Save both:**
   - API Key ID (looks like: `KALSHI-ABC123...`)
   - Private Key PEM (long text starting with `-----BEGIN PRIVATE KEY-----`)

**Add to `.env`:**
```bash
KALSHI_API_KEY=KALSHI-ABC123...
KALSHI_API_SECRET=-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----
```

**Note:** For testing, use demo environment:
```bash
# In code, set demo=True
client = KalshiAPIClient(api_key=..., api_secret=..., demo=True)
```

---

### 3. Polymarket CLOB (1 minute)

**You Already Have:**
- Private key (for wallet authentication)
- USDC.e on Polygon

**What You Need:**
1. **Set Token Allowances** (one-time):
   ```bash
   python set_allowances.py
   ```

2. **Generate API Credentials** (automatic):
   ```python
   from py_clob_client.client import ClobClient
   
   client = ClobClient(
       "https://clob.polymarket.com",
       key="your-private-key",
       chain_id=137
   )
   
   # This automatically creates/derives API credentials
   client.set_api_creds(client.create_or_derive_api_creds())
   ```

**Add to `.env`:**
```bash
POLYMARKET_PRIVATE_KEY=0x...
POLYGON_RPC_URL=https://polygon-rpc.com
```

---

### 4. UMA Oracle (30 seconds)

**No API Key Needed!** UMA uses on-chain contracts.

**What You Need:**
1. **Contract Addresses** (get from UMA docs or Finder contract):
   ```bash
   # Find these addresses:
   UMA_FINDER_ADDRESS=0x...  # UMA contract registry
   UMA_OOV3_ADDRESS=0x...    # OptimisticOracleV3 address
   ```

2. **Get from Finder Contract:**
   ```python
   from web3 import Web3
   
   FINDER_ADDRESS = "0x..."  # UMA Finder on Polygon
   w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
   
   finder = w3.eth.contract(
       address=FINDER_ADDRESS,
       abi=[...]  # Finder ABI
   )
   
   # Get OOv3 address
   oov3_address = finder.functions.getImplementationAddress(
       Web3.keccak(text="OptimisticOracleV3")
   ).call()
   ```

**Add to `.env`:**
```bash
UMA_FINDER_ADDRESS=0x...
UMA_OOV3_ADDRESS=0x...
POLYGON_RPC_URL=https://polygon-rpc.com
```

---

### 5. PNP Exchange (Coming Soon)

**Status:** API keys not yet available

**When Available:**
1. Check https://docs.pnp.exchange/api-reference/introduction
2. Look for "API Key Generation" page
3. Generate key and add to `.env`:
   ```bash
   PNP_API_KEY=your-pnp-api-key
   ```

**For Now:**
- Use mock implementation (already in codebase)
- Monitor PNP docs for updates

---

## 📋 Complete `.env` Template

Copy this template and fill in your keys:

```bash
# ============================================
# REQUIRED API KEYS
# ============================================

# Telegram (REQUIRED for alerts)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Kalshi (REQUIRED for cross-platform arbitrage)
KALSHI_API_KEY=your-kalshi-api-key-id
KALSHI_API_SECRET=your-kalshi-private-key-pem

# Polymarket (REQUIRED for CLOB trading)
POLYMARKET_PRIVATE_KEY=0x...
POLYGON_RPC_URL=https://polygon-rpc.com

# UMA Oracle (REQUIRED for resolution tracking)
UMA_FINDER_ADDRESS=0x...
UMA_OOV3_ADDRESS=0x...

# PNP Exchange (OPTIONAL - coming soon)
PNP_API_KEY=your-pnp-key-when-available

# ============================================
# OPTIONAL CONFIGURATION
# ============================================

# OpenAI (for NLI engine)
OPENAI_API_KEY=your-openai-key

# Risk Management
TOTAL_CAPITAL_USD=10000.0
MAX_POSITION_SIZE_PCT=10.0

# Strategy Parameters
MIN_PROFIT_MARGIN_PCT=2.5
MIN_DEVIATION_PCT=0.5
TEMPORAL_THRESHOLD_DAYS=7

# Logging
LOG_LEVEL=INFO
```

---

## ✅ Verification Script

Run this to verify all API keys are set:

```python
# verify_api_keys.py
import os
from dotenv import load_dotenv

load_dotenv()

def verify_keys():
    required = {
        "TELEGRAM_BOT_TOKEN": "Telegram Bot",
        "TELEGRAM_CHAT_ID": "Telegram Chat",
        "KALSHI_API_KEY": "Kalshi API",
        "KALSHI_API_SECRET": "Kalshi Secret",
        "POLYMARKET_PRIVATE_KEY": "Polymarket Wallet",
        "UMA_FINDER_ADDRESS": "UMA Finder",
        "UMA_OOV3_ADDRESS": "UMA OOv3",
    }
    
    optional = {
        "PNP_API_KEY": "PNP Exchange",
        "OPENAI_API_KEY": "OpenAI (for NLI)",
    }
    
    print("🔍 Verifying API Keys...\n")
    
    all_set = True
    for key, name in required.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {name}: Set")
        else:
            print(f"❌ {name}: Missing")
            all_set = False
    
    print("\n📋 Optional Keys:")
    for key, name in optional.items():
        value = os.getenv(key)
        if value:
            print(f"✅ {name}: Set")
        else:
            print(f"⚠️  {name}: Not set (optional)")
    
    if all_set:
        print("\n✅ All required keys are set!")
    else:
        print("\n❌ Some required keys are missing. Please check your .env file.")
    
    return all_set

if __name__ == "__main__":
    verify_keys()
```

---

## 🧪 Test Each Integration

### Test Telegram:
```python
from telegram_alerter import get_telegram_alerter
import asyncio

async def test():
    alerter = get_telegram_alerter()
    await alerter.send_message("✅ Telegram bot is working!")

asyncio.run(test())
```

### Test Kalshi:
```python
from kalshi_api_client import get_kalshi_client

client = get_kalshi_client(demo=True)
markets = client.get_markets(limit=5)
print(f"✅ Kalshi API working: {len(markets)} markets fetched")
```

### Test UMA:
```python
from uma_oracle_client import get_uma_oracle_client

client = get_uma_oracle_client()
print("✅ UMA Oracle client initialized")
```

### Test Polymarket:
```python
from clob_orderbook_client import get_clob_orderbook_client

client = get_clob_orderbook_client()
print("✅ Polymarket CLOB client initialized")
```

---

## 🆘 Troubleshooting

### Telegram Bot Not Responding?
- Check bot token is correct
- Make sure you've started conversation with bot
- Verify chat ID is correct

### Kalshi API Errors?
- Use demo environment first: `demo=True`
- Check API key format (should start with `KALSHI-`)
- Verify private key PEM format is correct

### UMA Contract Not Found?
- Verify contract addresses on Polygonscan
- Check RPC URL is correct
- Ensure contracts are deployed on Polygon mainnet

### Polymarket CLOB Issues?
- Verify wallet has USDC.e
- Run `set_allowances.py` first
- Check private key format (should start with `0x`)

---

## 📞 Support

If you need help:
1. Check the error logs
2. Verify `.env` file format
3. Test each integration individually
4. Check API documentation links in code comments

**Good luck! 🚀**

# Integration Guide - UMA & PNP Exchange

This document provides a comprehensive guide for integrating UMA Oracle and PNP Exchange SDK into the semantic arbitrage engine.

## Table of Contents
- [Environment Configuration](#environment-configuration)
- [UMA Oracle Integration](#uma-oracle-integration)
- [PNP Exchange SDK Integration](#pnp-exchange-sdk-integration)
- [Market Creation Examples](#market-creation-examples)
- [Trading & Execution](#trading--execution)

---

## Environment Configuration

The following environment variables have been configured in `.env`:

```bash
# API Keys
OPENAI_API_KEY=<configured>
POLYMARKET_API_KEY=<to_be_configured>
KALSHI_API_KEY=<to_be_configured>

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=8446774155:AAFSwvgWPixlsPWNjw4tSXMTXK6_nZczAtI
TELEGRAM_CHAT_ID=6513152571

# Blockchain Configuration
MEZO_PRIVACY_KEY=434216380428b117876ebad6c90b4a8f6c843ceb99a82873efa4b88fb14911a0
POLYGON_PRIVATE_KEY=434216380428b117876ebad6c90b4a8f6c843ceb99a82873efa4b88fb14911a0
```

---

## UMA Oracle Integration

### Overview
UMA is an optimistic oracle and dispute arbitration system that securely allows for arbitrary types of data to be brought onchain.

### Key Features
- **Optimistic Oracle V2**: Build prediction markets and insurance protocols
- **Optimistic Oracle V3**: Build data asserters and escalation managers
- **Use Cases**: Cross-chain bridges, prediction markets, insurance protocols, custom derivatives

### Documentation
- Main Docs: https://docs.uma.xyz/
- Finder Address Query: https://docs.uma.xyz/?q=finder+address

### Core Concepts
1. **Optimistic Verification**: Data is assumed to be correct unless disputed
2. **Dispute Resolution**: Economic incentives ensure data accuracy
3. **Flexible Data Types**: Can verify any verifiable truth or data

### Integration Steps
1. Choose between OOv2 (prediction markets) or OOv3 (data assertions)
2. Implement oracle queries for market resolution
3. Set up dispute mechanisms
4. Configure bond requirements

---

## PNP Exchange SDK Integration

### Overview
PNP Exchange is a Solana-based prediction market platform with a TypeScript SDK for creating and trading markets.

### Installation
```bash
npm install pnp-sdk
# or
yarn add pnp-sdk
```

### Prerequisites
- Node.js 16+
- Solana CLI (for local development)
- Basic understanding of Solana and blockchain concepts

### Features
- ✅ Create and manage prediction markets on Solana
- ✅ Trade YES/NO tokens
- ✅ Redeem positions for resolved markets
- ✅ Claim creator refunds for unresolved markets
- ✅ Interact with on-chain market data
- ✅ Fetch real-time market prices & multipliers (no wallet required)
- ✅ Fetch settlement criteria from proxy server
- ✅ TypeScript-first development experience
- ✅ Comprehensive error handling
- ✅ Built on top of @solana/web3.js
- ✅ Supports both SPL Token and Token-2022 programs

### Documentation
- Main SDK Docs: https://docs.pnp.exchange/pnp-sdk

---

## Market Creation Examples

### Market Types
1. **V2 AMM Markets**: Traditional automated market maker (AMM) pools where liquidity is provided upfront
2. **P2P Markets**: Peer-to-peer markets where the creator takes a position on one side

### Creating a V2 AMM Market

```typescript
import { PublicKey } from '@solana/web3.js';
import { PNPClient } from 'pnp-sdk';

// Configuration
const RPC_URL = 'https://api.mainnet-beta.solana.com';
const WALLET_SECRET_ARRAY = [/* Your 64-byte private key array goes here */];

async function createAMMMarket() {
  // Initialize client with private key
  const client = new PNPClient(RPC_URL, Uint8Array.from(WALLET_SECRET_ARRAY));

  // Market parameters
  const question = 'Will Bitcoin reach $100K by end of 2025?';
  const initialLiquidity = 1_000_000n; // 1 USDC (6 decimals)
  const endTime = BigInt(Math.floor(Date.now() / 1000) + 30 * 24 * 60 * 60); // 30 days
  const collateralMint = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'); // USDC

  // Create the market
  const result = await client.market.createMarket({
    question,
    initialLiquidity,
    endTime,
    baseMint: collateralMint,
  });

  console.log('Market created successfully!');
  console.log('Signature:', result.signature);
  console.log('Market Address:', result.market.toBase58());
}

createAMMMarket().catch(console.error);
```

### Key Points for V2 AMM Markets
- Initial liquidity is split equally between YES and NO tokens in the AMM pool
- The creator doesn't take a position; they provide liquidity for others to trade against
- Use `client.market.createMarket()` for V2 markets

### Creating a P2P Market

```typescript
import { PublicKey } from '@solana/web3.js';
import { PNPClient } from 'pnp-sdk';

async function createP2PMarket() {
  const client = new PNPClient(RPC_URL, Uint8Array.from(WALLET_SECRET_ARRAY));

  const question = 'Will Ethereum reach $10K by Q2 2025?';
  const initialLiquidity = 500_000n; // 0.5 USDC
  const endTime = BigInt(Math.floor(Date.now() / 1000) + 60 * 24 * 60 * 60); // 60 days
  const collateralMint = new PublicKey('EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v'); // USDC

  // Create P2P market
  const result = await client.market.createP2PMarket({
    question,
    initialLiquidity,
    endTime,
    baseMint: collateralMint,
  });

  console.log('P2P Market created successfully!');
  console.log('Signature:', result.signature);
  console.log('Market Address:', result.market.toBase58());
}
```

### Creating Markets with Custom Oracles

PNP Exchange supports custom oracle integrations for market resolution. This is particularly useful for:
- Twitter/X metrics (followers, likes, retweets)
- YouTube metrics (views, subscribers)
- Custom data sources

**Example: Twitter Market**
```typescript
const twitterMarket = await client.market.createMarket({
  question: 'Will @elonmusk reach 200M followers by March 2025?',
  initialLiquidity: 1_000_000n,
  endTime: BigInt(Math.floor(new Date('2025-03-31').getTime() / 1000)),
  baseMint: collateralMint,
  oracleType: 'twitter',
  oracleConfig: {
    username: 'elonmusk',
    metric: 'followers',
    threshold: 200_000_000
  }
});
```

---

## Trading & Execution

### Fetching Market Prices

```typescript
// Get market price data (no wallet required)
const priceData = await client.market.getMarketPriceData(marketAddress);

console.log('YES Token Price:', priceData.yesPrice);
console.log('NO Token Price:', priceData.noPrice);
console.log('Total Liquidity:', priceData.totalLiquidity);
```

### Trading on V2 AMM Markets

```typescript
import { PublicKey } from '@solana/web3.js';

async function buyYesTokens() {
  const client = new PNPClient(RPC_URL, Uint8Array.from(WALLET_SECRET_ARRAY));
  
  const marketAddress = new PublicKey('YOUR_MARKET_ADDRESS');
  const amount = 100_000n; // 0.1 USDC worth
  
  const result = await client.market.buy({
    market: marketAddress,
    side: 'YES',
    amount: amount,
    slippage: 0.01 // 1% slippage tolerance
  });
  
  console.log('Trade executed:', result.signature);
}
```

### Redeeming Winnings

```typescript
async function redeemWinnings() {
  const client = new PNPClient(RPC_URL, Uint8Array.from(WALLET_SECRET_ARRAY));
  
  const marketAddress = new PublicKey('RESOLVED_MARKET_ADDRESS');
  
  const result = await client.market.redeem({
    market: marketAddress
  });
  
  console.log('Winnings redeemed:', result.signature);
  console.log('Amount:', result.amount);
}
```

---

## Integration with Semantic Arbitrage Engine

### Recommended Architecture

1. **Market Monitoring**
   - Use PNP SDK to fetch real-time market prices
   - Monitor multiple markets simultaneously
   - Compare with Polymarket and Kalshi prices

2. **Arbitrage Detection**
   - Implement price comparison logic
   - Calculate potential profit after fees
   - Consider slippage and liquidity

3. **Execution Strategy**
   - Use Telegram bot for notifications
   - Implement automatic execution with risk limits
   - Log all trades for analysis

4. **Oracle Integration**
   - Use UMA for custom market resolution
   - Implement dispute monitoring
   - Set up automated settlement

### Next Steps

1. **Install PNP SDK**
   ```bash
   npm install pnp-sdk @solana/web3.js
   ```

2. **Create Market Client Module**
   - Extend `market_client.py` to support PNP Exchange
   - Implement Solana wallet integration
   - Add market creation and trading functions

3. **Integrate with Execution Bot**
   - Update `execution_bot.py` to support Solana transactions
   - Add PNP market execution logic
   - Implement cross-platform arbitrage

4. **Configure UMA Oracle**
   - Set up oracle queries for market resolution
   - Implement dispute handling
   - Configure bond requirements

5. **Testing**
   - Test on Solana devnet first
   - Verify market creation and trading
   - Test arbitrage detection logic

---

## Security Considerations

⚠️ **IMPORTANT**: The private keys in `.env` should be kept secure:
- Never commit `.env` to version control
- Use `.gitignore` to exclude `.env`
- Consider using hardware wallets for production
- Implement key rotation policies
- Use separate keys for testing and production

## Resources

- **UMA Documentation**: https://docs.uma.xyz/
- **PNP Exchange SDK**: https://docs.pnp.exchange/pnp-sdk
- **Solana Documentation**: https://docs.solana.com/
- **Telegram Bot API**: https://core.telegram.org/bots/api

---

*Last Updated: 2026-01-27*

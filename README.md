# Semantic Arbitrage Engine

A Python-based engine to identify logical arbitrage opportunities in prediction markets (Polymarket, Kalshi) using Natural Language Inference (NLI).

## Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Copy `.env.example` to `.env` and add your keys:
   ```bash
   cp .env.example .env
   # Edit .env with your OPENAI_API_KEY
   ```

## Usage

### 1. Test Market Data Fetching
Fetches active markets from Polymarket (Gamma API) and Kalshi (Mock).
```bash
python market_client.py
```

### 2. Run the NLI Engine Demo
Demonstrates Semantic Clustering and Entailment Checks on mock data.
```bash
python nli_engine.py
```

### 3. Run the Arbitrage Finder
Integration of Data Ingestion -> Clustering -> NLI Check -> Opportunity Detection.
```bash
python arb_finder.py
```

## PNP Exchange - Private & Agent-Based Prediction Markets

This project includes a complete implementation of AI agents that autonomously create prediction markets on PNP Exchange using privacy-focused tokens as collateral.

### Components

#### 1. PNP AI Agent (`pnp_agent.py`)
An intelligent agent that:
- Generates market questions using OpenAI based on news headlines or user prompts
- Creates markets via the PNP SDK
- Handles privacy-focused token collateral (ELUSIV, LIGHT, PNP)
- Supports both automated and custom market creation

**Usage:**
```python
from pnp_agent import PNPAgent

# Initialize agent
agent = PNPAgent(default_collateral_token='ELUSIV')

# Create market from news headline
result = agent.create_market_from_prompt(
    "Bitcoin reaches $100,000 by end of 2024",
    collateral_token='ELUSIV',
    collateral_amount=100.0
)

# Create custom market
result = agent.create_custom_market(
    question="Will AI achieve AGI by 2025?",
    outcomes=['Yes', 'No'],
    collateral_token='LIGHT',
    collateral_amount=50.0
)
```

**Run demo:**
```bash
python pnp_agent.py
```

#### 2. PNP SDK Mock (`pnp_sdk_mock.py`)
Mock implementation of the PNP Exchange SDK with:
- `create_market(params)`: Market initialization
- `place_order(params)`: Order placement
- `settle_market(market_id, outcome)`: AI-driven settlement

**Usage:**
```python
from pnp_sdk_mock import get_sdk

sdk = get_sdk()

# Create market
market = sdk.create_market({
    'question': 'Test question?',
    'outcomes': ['Yes', 'No'],
    'collateral_token': 'ELUSIV',
    'collateral_amount': 100.0
})

# Place order
order = sdk.place_order({
    'market_id': market['market_id'],
    'outcome': 'Yes',
    'side': 'buy',
    'amount': 10.0,
    'price': 0.6
})

# Settle market
settlement = sdk.settle_market(market['market_id'], 'Yes')
```

#### 3. PNP Infrastructure (`pnp_infra/`)

##### Market Factory (`market_factory.py`)
Deploys and manages market contracts/accounts on Solana:
- Account deployment with Program Derived Addresses (PDAs)
- State management and updates
- Account lifecycle operations

##### Collateral Manager (`collateral_manager.py`)
Handles privacy token locking and release:
- Token locking for market creation
- Escrow management
- Partial and full collateral release
- Transaction history tracking

**Supported Tokens:** ELUSIV, LIGHT, PNP

##### Privacy Wrapper (`privacy_wrapper.py`)
Simulated zero-knowledge proof and encryption layer:
- Market data encryption
- Address anonymization
- ZK proof generation and verification
- Privacy-preserving orders and settlements

**Privacy Levels:** PUBLIC, PRIVATE, ANONYMOUS

### Testing

#### Test Infrastructure Components
```bash
python test_pnp_infra.py
```

This tests:
- Market Factory deployment
- Collateral Manager operations
- Privacy Wrapper functionality

#### Full Integration Test
```bash
python test_pnp_integration.py
```

This demonstrates the complete workflow:
1. Agent creates market from prompt
2. Market Factory deploys account on Solana
3. Collateral Manager locks privacy tokens
4. Privacy Wrapper encrypts and anonymizes operations
5. Order placement with privacy
6. Market settlement
7. Collateral release
8. Account closure

### Verification Plan

#### Automated Tests
- ✅ `python pnp_agent.py` - Verifies agent can trigger market creation
- ✅ `python test_pnp_infra.py` - Verifies collateral locking logic
- ✅ `python test_pnp_integration.py` - Full end-to-end workflow

#### Manual Verification
1. **Market Creation from Headlines:**
   ```python
   agent = PNPAgent()
   result = agent.create_market_from_prompt("Your news headline here")
   ```

2. **Privacy Token Verification:**
   - Check that privacy tokens (ELUSIV, LIGHT, PNP) are correctly identified
   - Verify collateral amounts are properly locked in simulated transactions

3. **Privacy Operations:**
   - Verify address anonymization works
   - Check ZK proof generation and verification
   - Confirm encrypted market data storage

### Architecture

```
┌─────────────┐
│  PNPAgent   │  ← Generates market questions, creates markets
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  PNP SDK    │  ← Market operations (create, order, settle)
│   (Mock)    │
└──────┬──────┘
       │
       ├──► MarketFactory ────► Solana account deployment
       │
       ├──► CollateralManager ──► Privacy token locking/release
       │
       └──► PrivacyWrapper ────► ZK proofs, encryption, anonymization
```

### Privacy Features

- **Private Orders**: Orders can be placed with anonymized trader addresses
- **Encrypted Data**: Market data can be encrypted for privacy
- **ZK Proofs**: Zero-knowledge proofs for ownership, participation, and settlement
- **Anonymized Addresses**: Public keys can be anonymized for anonymous participation

### Supported Privacy Tokens

- **ELUSIV**: Privacy-focused token for private transactions
- **LIGHT**: Light Protocol token for confidential transactions  
- **PNP**: Native PNP Exchange token

### Environment Setup

Ensure you have:
- Python 3.8+
- OpenAI API key (optional, for market question generation)
- All dependencies from `requirements.txt`

The system works without OpenAI API key (uses fallback question generation).
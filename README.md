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

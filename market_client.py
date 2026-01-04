import requests
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class MarketAdapter(ABC):
    @abstractmethod
    def fetch_active_markets(self) -> List[Dict[str, Any]]:
        """
        Fetches active markets and returns them in a normalized format.
        Normalized format:
        {
            'id': str,
            'source': str ('polymarket' | 'kalshi'),
            'question': str,
            'outcomes': List[Dict] [{'name': str, 'price': float}],
            'resolution_criteria': str
        }
        """
        pass

class PolymarketAdapter(MarketAdapter):
    def __init__(self):
        self.api_url = "https://gamma-api.polymarket.com/markets"

    def fetch_active_markets(self) -> List[Dict[str, Any]]:
        print("Fetching Polymarket data (Gamma API)...")
        try:
            # Fetch active markets, limit to 100 for better clustering chances
            params = {
                "limit": 100,
                "active": "true",
                "closed": "false",
                "order": "volume24hr",
                "ascending": "false" 
            }
            # Gamma API sometimes requires User-Agent
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; SemanticArbBot/1.0)"
            }
            response = requests.get(self.api_url, params=params, headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            normalized = []
            for item in data:
                # Gamma API structure varies, but generally has 'question', 'outcomes', 'outcomePrices'
                # Check if it's a binary market (simplest for MVP)
                if item.get('active') and len(item.get('outcomes', [])) == 2:
                    try:
                        outcomes = json.loads(item.get('outcomes')) if isinstance(item.get('outcomes'), str) else item.get('outcomes')
                        outcome_prices = json.loads(item.get('outcomePrices')) if isinstance(item.get('outcomePrices'), str) else item.get('outcomePrices')
                        
                        normalized_outcomes = []
                        for idx, name in enumerate(outcomes):
                            price = float(outcome_prices[idx]) if idx < len(outcome_prices) else 0.0
                            normalized_outcomes.append({'name': name, 'price': price})

                        normalized.append({
                            'id': f"poly_{item.get('id')}",
                            'source': 'polymarket',
                            'question': item.get('question'),
                            'outcomes': normalized_outcomes,
                            'resolution_criteria': item.get('description', 'See market page.')
                        })
                    except Exception as e:
                        continue # Skip malformed items
            
            return normalized
        except Exception as e:
            print(f"Error fetching Polymarket: {e}")
            return []
        # Dead code removed for demo clarity

class KalshiAdapter(MarketAdapter):
    def __init__(self):
        # Public-facing elections API often allows reads without auth
        self.api_url = "https://api.elections.kalshi.com/trade-api/v2/markets"

    def fetch_active_markets(self) -> List[Dict[str, Any]]:
        print("Fetching Kalshi data (Elections Public API)...")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; SemanticArbBot/1.0)"
            }
            params = {"limit": 100, "status": "active"}
            response = requests.get(self.api_url, params=params, headers=headers, timeout=15)
            
            if response.status_code in [401, 403]:
                print("Kalshi Public API access denied (Auth required). Skipping Kalshi.")
                return []
                
            response.raise_for_status()
            data = response.json()
            
            normalized = []
            markets = data.get('markets', [])
            for item in markets:
                # Filter for binary markets
                # Kalshi uses 'yes_bid', 'no_bid' etc.
                normalized.append({
                    'id': f"kalshi_{item.get('ticker')}",
                    'source': 'kalshi',
                    'question': item.get('title'),
                    'outcomes': [
                        {'name': 'Yes', 'price': (item.get('yes_bid', 0) / 100.0)},
                        {'name': 'No', 'price': (item.get('no_bid', 0) / 100.0)}
                    ],
                    'resolution_criteria': item.get('rules_primary', 'See market page.')
                })
            return normalized
        except Exception as e:
            print(f"Error fetching Kalshi (skipping): {e}")
            return []

class MarketAggregator:
    def __init__(self, adapters: List[MarketAdapter]):
        self.adapters = adapters

    def get_all_markets(self) -> List[Dict[str, Any]]:
        all_markets = []
        for adapter in self.adapters:
            try:
                markets = adapter.fetch_active_markets()
                all_markets.extend(markets)
            except Exception as e:
                print(f"Error fetching from adapter {adapter.__class__.__name__}: {e}")
        return all_markets

if __name__ == "__main__":
    # Test adapters
    poly = PolymarketAdapter()
    kalshi = KalshiAdapter()
    aggregator = MarketAggregator([poly, kalshi])
    
    data = aggregator.get_all_markets()
    print(f"Fetched {len(data)} total markets.")
    for m in data:
        print(f" - [{m['source']}] {m['question']} (Price: {m['outcomes'][0]['price']})")

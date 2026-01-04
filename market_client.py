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
            # Fetch active markets, limit to 50 for real scanning
            params = {
                "limit": 50,
                "active": "true",
                "closed": "false"
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
        self.api_url = "https://trading-api.kalshi.com/v1"
        # Kalshi API typically requires an API key
        # For demonstration, let's assume it's set as an environment variable or passed in
        # self.api_key = os.environ.get("KALSHI_API_KEY") # Uncomment and set your API key

    def fetch_active_markets(self) -> List[Dict[str, Any]]:
        print("Fetching Kalshi data...")
        try:
            headers = {
                # "X-API-KEY": self.api_key, # Uncomment if using an API key
                "User-Agent": "Mozilla/5.0 (compatible; SemanticArbBot/1.0)"
            }
            # Kalshi's /markets endpoint for fetching market data
            # We'll fetch all markets and filter for active ones, or use query params if available.
            # Kalshi's API documentation suggests /markets endpoint for listing markets.
            # Let's assume a simple GET request to /markets for now.
            # A real implementation would likely use /markets?status=active or similar.
            response = requests.get(f"{self.api_url}/markets", headers=headers, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            normalized = []
            # Kalshi API returns a 'markets' key containing a list of market objects
            for item in data.get('markets', []):
                # Check if the market is active and has binary outcomes (Yes/No)
                # Kalshi markets typically have 'status' and 'yes_bid', 'no_bid' etc.
                if item.get('status') == 'active' and item.get('market_type') == 'binary':
                    try:
                        # Kalshi prices are typically in cents, convert to dollars (0-1 range)
                        yes_price = item.get('yes_bid') / 100.0 if item.get('yes_bid') is not None else 0.0
                        no_price = item.get('no_bid') / 100.0 if item.get('no_bid') is not None else 0.0
                        
                        normalized_outcomes = [
                            {'name': 'Yes', 'price': yes_price},
                            {'name': 'No', 'price': no_price}
                        ]

                        normalized.append({
                            'id': f"kalshi_{item.get('ticker')}",
                            'source': 'kalshi',
                            'question': item.get('title'),
                            'outcomes': normalized_outcomes,
                            'resolution_criteria': item.get('settlement_details', 'See market page.')
                        })
                    except Exception as e:
                        print(f"Error processing Kalshi market {item.get('ticker')}: {e}")
                        continue # Skip malformed items
            
            return normalized
        except Exception as e:
            print(f"Error fetching Kalshi: {e}")
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

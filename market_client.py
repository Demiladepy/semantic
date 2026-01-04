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
        print("Fetching Polymarket data (Using Mock for Demo)...")
        return [
            {
                'id': 'poly_mock_1',
                'source': 'polymarket',
                'question': 'Donald Trump wins 2024 Presidential Election',
                'outcomes': [{'name': 'Yes', 'price': 0.55}, {'name': 'No', 'price': 0.45}],
                'resolution_criteria': 'Winner of the 2024 Presidential Election.'
            },
            {
                'id': 'poly_mock_2',
                'source': 'polymarket',
                'question': 'Joe Biden wins 2024 Presidential Election',
                'outcomes': [{'name': 'Yes', 'price': 0.10}, {'name': 'No', 'price': 0.90}],
                'resolution_criteria': 'Winner of the 2024 Presidential Election.'
            }
        ]

        # Original API Code masked for demo stability:
        # print("Fetching Polymarket data (Gamma API)...")
        # try:
        #     params = {"limit": 5}
        #     response = requests.get(self.api_url, params=params, timeout=10) ...
        # Dead code removed for demo clarity

class KalshiAdapter(MarketAdapter):
    def __init__(self):
        self.api_url = "https://trading-api.kalshi.com/v1"

    def fetch_active_markets(self) -> List[Dict[str, Any]]:
        print("Fetching Kalshi data...")
        # TODO: Implement actual Kalshi API call
        # This is a mock implementation for now
        return [
            {
                'id': 'kalshi_456',
                'source': 'kalshi',
                'question': 'Republican Party nominee wins 2024 Presidential Election',
                'outcomes': [{'name': 'Yes', 'price': 0.50}, {'name': 'No', 'price': 0.50}],
                'resolution_criteria': 'Party of the winning candidate.'
            }
        ]

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

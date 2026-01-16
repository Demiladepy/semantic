"""
Mock PNP SDK Implementation

This module provides a mock implementation of the anticipated PNP Exchange SDK
to allow development of agents and infrastructure before the actual SDK is available.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import uuid


class PNPSDKMock:
    """
    Mock implementation of PNP Exchange SDK.
    
    Simulates the core functionality needed for prediction market operations:
    - Market creation
    - Order placement
    - Market settlement
    """
    
    def __init__(self):
        """Initialize the mock SDK with in-memory storage."""
        self.markets: Dict[str, Dict[str, Any]] = {}
        self.orders: Dict[str, Dict[str, Any]] = {}
        self.market_counter = 0
    
    def create_market(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock market creation.
        
        Args:
            params: Dictionary containing:
                - question: str - The market question
                - outcomes: List[str] - List of possible outcomes
                - collateral_token: str - Privacy token symbol (e.g., 'ELUSIV', 'LIGHT', 'PNP')
                - collateral_amount: float - Amount of collateral to lock
                - end_date: Optional[str] - ISO format end date
                - resolution_criteria: Optional[str] - How the market will be resolved
                - creator: Optional[str] - Creator address/identifier
        
        Returns:
            Dictionary with:
                - market_id: str - Unique market identifier
                - status: str - 'pending' | 'active' | 'settled'
                - created_at: str - ISO timestamp
        """
        market_id = f"PNP-{self.market_counter:06d}"
        self.market_counter += 1
        
        # Validate required parameters
        if 'question' not in params:
            raise ValueError("Missing required parameter: 'question'")
        if 'outcomes' not in params or not params['outcomes']:
            raise ValueError("Missing or empty required parameter: 'outcomes'")
        if 'collateral_token' not in params:
            raise ValueError("Missing required parameter: 'collateral_token'")
        
        # Set defaults
        end_date = params.get('end_date')
        if end_date:
            end_date = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            end_date = datetime.utcnow() + timedelta(days=30)  # Default 30 days
        
        market_data = {
            'market_id': market_id,
            'question': params['question'],
            'outcomes': params['outcomes'],
            'collateral_token': params['collateral_token'],
            'collateral_amount': params.get('collateral_amount', 0.0),
            'end_date': end_date.isoformat(),
            'resolution_criteria': params.get('resolution_criteria', ''),
            'creator': params.get('creator', 'anonymous'),
            'status': 'active',
            'created_at': datetime.utcnow().isoformat(),
            'total_volume': 0.0,
            'outcome_prices': {outcome: 0.5 for outcome in params['outcomes']}  # Initialize equal prices
        }
        
        self.markets[market_id] = market_data
        
        print(f"[PNP SDK Mock] Market created: {market_id}")
        print(f"  Question: {params['question']}")
        print(f"  Outcomes: {', '.join(params['outcomes'])}")
        print(f"  Collateral: {params.get('collateral_amount', 0.0)} {params['collateral_token']}")
        
        return {
            'market_id': market_id,
            'status': 'active',
            'created_at': market_data['created_at']
        }
    
    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock order placement.
        
        Args:
            params: Dictionary containing:
                - market_id: str - Market identifier
                - outcome: str - Outcome to bet on
                - side: str - 'buy' | 'sell'
                - amount: float - Order amount
                - price: float - Price per share (0.0 to 1.0)
                - trader: Optional[str] - Trader address/identifier
        
        Returns:
            Dictionary with:
                - order_id: str - Unique order identifier
                - status: str - 'pending' | 'filled' | 'cancelled'
                - filled_at: Optional[str] - ISO timestamp if filled
        """
        market_id = params.get('market_id')
        if not market_id or market_id not in self.markets:
            raise ValueError(f"Invalid market_id: {market_id}")
        
        market = self.markets[market_id]
        if market['status'] != 'active':
            raise ValueError(f"Market {market_id} is not active (status: {market['status']})")
        
        outcome = params.get('outcome')
        if outcome not in market['outcomes']:
            raise ValueError(f"Invalid outcome '{outcome}'. Valid outcomes: {market['outcomes']}")
        
        order_id = str(uuid.uuid4())
        side = params.get('side', 'buy')
        amount = params.get('amount', 0.0)
        price = params.get('price', 0.5)
        
        # Validate price range
        if not 0.0 <= price <= 1.0:
            raise ValueError(f"Price must be between 0.0 and 1.0, got {price}")
        
        order_data = {
            'order_id': order_id,
            'market_id': market_id,
            'outcome': outcome,
            'side': side,
            'amount': amount,
            'price': price,
            'trader': params.get('trader', 'anonymous'),
            'status': 'filled',  # Mock: orders are immediately filled
            'filled_at': datetime.utcnow().isoformat(),
            'created_at': datetime.utcnow().isoformat()
        }
        
        self.orders[order_id] = order_data
        
        # Update market volume
        market['total_volume'] += amount
        
        # Simulate price movement (simple: move price slightly toward order side)
        if side == 'buy':
            market['outcome_prices'][outcome] = min(1.0, market['outcome_prices'][outcome] + 0.01)
        else:
            market['outcome_prices'][outcome] = max(0.0, market['outcome_prices'][outcome] - 0.01)
        
        print(f"[PNP SDK Mock] Order placed: {order_id}")
        print(f"  Market: {market_id}")
        print(f"  {side.upper()} {amount} shares of '{outcome}' at {price}")
        
        return {
            'order_id': order_id,
            'status': 'filled',
            'filled_at': order_data['filled_at']
        }
    
    def settle_market(self, market_id: str, outcome: str, resolver: Optional[str] = None) -> Dict[str, Any]:
        """
        Mock market settlement.
        
        Args:
            market_id: Market identifier
            outcome: The winning outcome
            resolver: Optional resolver identifier (e.g., AI agent ID)
        
        Returns:
            Dictionary with:
                - market_id: str
                - winning_outcome: str
                - settled_at: str - ISO timestamp
                - status: str - 'settled'
        """
        if market_id not in self.markets:
            raise ValueError(f"Market {market_id} not found")
        
        market = self.markets[market_id]
        if outcome not in market['outcomes']:
            raise ValueError(f"Invalid outcome '{outcome}'. Valid outcomes: {market['outcomes']}")
        
        if market['status'] == 'settled':
            raise ValueError(f"Market {market_id} is already settled")
        
        market['status'] = 'settled'
        market['winning_outcome'] = outcome
        market['settled_at'] = datetime.utcnow().isoformat()
        market['resolver'] = resolver or 'system'
        
        print(f"[PNP SDK Mock] Market settled: {market_id}")
        print(f"  Winning outcome: {outcome}")
        print(f"  Resolved by: {resolver or 'system'}")
        
        return {
            'market_id': market_id,
            'winning_outcome': outcome,
            'settled_at': market['settled_at'],
            'status': 'settled'
        }
    
    def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market details by ID."""
        return self.markets.get(market_id)
    
    def list_markets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all markets, optionally filtered by status."""
        markets = list(self.markets.values())
        if status:
            markets = [m for m in markets if m['status'] == status]
        return markets
    
    def get_orders(self, market_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders, optionally filtered by market_id."""
        orders = list(self.orders.values())
        if market_id:
            orders = [o for o in orders if o['market_id'] == market_id]
        return orders


# Global instance for easy import
_sdk_instance = None

def get_sdk() -> PNPSDKMock:
    """Get or create the global SDK instance."""
    global _sdk_instance
    if _sdk_instance is None:
        _sdk_instance = PNPSDKMock()
    return _sdk_instance


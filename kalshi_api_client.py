"""
Kalshi API Client - Full Integration

CFTC-regulated prediction market exchange integration with:
- REST API for market data and trading
- WebSocket for real-time updates
- Order placement and management
- Account management
"""

import os
import logging
import json
import time
import hmac
import hashlib
import requests
import websocket
import threading
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderSide(Enum):
    """Order side."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type."""
    LIMIT = "limit"
    MARKET = "market"


class OrderStatus(Enum):
    """Order status."""
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class KalshiMarket:
    """Kalshi market data."""
    ticker: str
    title: str
    subtitle: str
    yes_bid: float
    yes_ask: float
    no_bid: float
    no_ask: float
    last_price: float
    volume: int
    open_interest: int
    status: str
    close_time: Optional[datetime]
    category: str


@dataclass
class KalshiOrderbook:
    """Kalshi orderbook."""
    ticker: str
    yes_bids: List[Dict[str, float]]
    yes_asks: List[Dict[str, float]]
    no_bids: List[Dict[str, float]]
    no_asks: List[Dict[str, float]]
    timestamp: float


class KalshiAPIClient:
    """
    Kalshi API client for market data and trading.
    
    Features:
    - Market data fetching
    - Orderbook monitoring
    - Order placement
    - Account management
    - Real-time WebSocket updates
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = "https://api.elections.kalshi.com/trade-api/v2",
        demo: bool = False,
    ):
        """
        Initialize Kalshi API client.
        
        Args:
            api_key: Kalshi API key ID
            api_secret: Kalshi API secret (private key PEM)
            base_url: API base URL
            demo: Use demo environment
        """
        self.api_key = api_key or os.getenv("KALSHI_API_KEY")
        self.api_secret = api_secret or os.getenv("KALSHI_API_SECRET")
        self.base_url = base_url
        self.demo = demo

        if demo:
            self.base_url = "https://demo-api.elections.kalshi.com/trade-api/v2"

        self.session = requests.Session()
        self.ws_client: Optional[websocket.WebSocketApp] = None
        self.ws_callbacks: Dict[str, List[Callable]] = {}

        if self.api_key and self.api_secret:
            logger.info(f"✅ Kalshi API Client initialized (Demo: {demo})")
        else:
            logger.warning("⚠️ Kalshi API credentials not set - some features disabled")

    def _sign_request(self, method: str, path: str, body: str = "") -> tuple:
        """Generate HMAC signature for authenticated requests."""
        if not self.api_secret:
            return None, None

        timestamp = str(int(time.time() * 1000))
        message = f"{timestamp}{method}{path}{body}"

        signature = hmac.new(
            self.api_secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature, timestamp

    def _get_headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key and self.api_secret:
            signature, timestamp = self._sign_request(method, path, body)
            headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "X-Kalshi-Signature": signature,
                "X-Kalshi-Timestamp": timestamp,
            })

        return headers

    def get_account_balance(self) -> Optional[Dict[str, Any]]:
        """Get account balance."""
        if not self.api_key:
            logger.error("API key required for account balance")
            return None

        path = "/portfolio/balance"
        headers = self._get_headers("GET", path)

        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return None

    def get_markets(
        self,
        status: str = "open",
        limit: int = 100,
        category: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get all markets.
        
        Args:
            status: Market status ("open", "closed", "all")
            limit: Maximum number of markets to return
            category: Filter by category
            
        Returns:
            List of market dictionaries
        """
        path = "/markets"
        params = {
            "status": status,
            "limit": limit,
        }

        if category:
            params["category"] = category

        headers = self._get_headers("GET", path)

        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("markets", [])
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []

    def get_market(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Get specific market details."""
        path = f"/markets/{ticker}"
        headers = self._get_headers("GET", path)

        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching market {ticker}: {e}")
            return None

    def get_orderbook(self, ticker: str) -> Optional[KalshiOrderbook]:
        """Get orderbook for specific market."""
        path = f"/markets/{ticker}/orderbook"
        headers = self._get_headers("GET", path)

        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            return KalshiOrderbook(
                ticker=ticker,
                yes_bids=data.get("yes_bids", []),
                yes_asks=data.get("yes_asks", []),
                no_bids=data.get("no_bids", []),
                no_asks=data.get("no_asks", []),
                timestamp=time.time(),
            )
        except Exception as e:
            logger.error(f"Error fetching orderbook for {ticker}: {e}")
            return None

    def place_order(
        self,
        ticker: str,
        side: OrderSide,
        order_type: OrderType,
        price: float,
        quantity: int,
    ) -> Optional[Dict[str, Any]]:
        """
        Place limit or market order.
        
        Args:
            ticker: Market ticker
            side: "buy" or "sell"
            order_type: "limit" or "market"
            price: Order price (0-100 cents, required for limit orders)
            quantity: Number of contracts
            
        Returns:
            Order response dictionary
        """
        if not self.api_key:
            logger.error("API key required for placing orders")
            return None

        path = "/orders"
        body = {
            "ticker": ticker,
            "side": side.value,
            "type": order_type.value,
            "quantity": quantity,
        }

        if order_type == OrderType.LIMIT:
            body["price"] = int(price * 100)  # Convert to cents

        body_str = json.dumps(body)
        headers = self._get_headers("POST", path, body_str)

        try:
            response = self.session.post(
                f"{self.base_url}{path}",
                json=body,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None

    def get_orders(
        self,
        ticker: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get order history."""
        if not self.api_key:
            logger.error("API key required for getting orders")
            return []

        path = "/orders"
        params = {}

        if ticker:
            params["ticker"] = ticker
        if status:
            params["status"] = status

        headers = self._get_headers("GET", path)

        try:
            response = self.session.get(
                f"{self.base_url}{path}",
                params=params,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            return data.get("orders", [])
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return []

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an order."""
        if not self.api_key:
            logger.error("API key required for canceling orders")
            return False

        path = f"/orders/{order_id}"
        headers = self._get_headers("DELETE", path)

        try:
            response = self.session.delete(
                f"{self.base_url}{path}",
                headers=headers
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Error canceling order {order_id}: {e}")
            return False

    def connect_websocket(self, api_key: Optional[str] = None):
        """Connect to Kalshi WebSocket for real-time updates."""
        ws_url = "wss://api.elections.kalshi.com/trade-api/ws/v2"
        if self.demo:
            ws_url = "wss://demo-api.elections.kalshi.com/trade-api/ws/v2"

        api_key = api_key or self.api_key

        def on_message(ws, message):
            """Handle incoming WebSocket messages."""
            try:
                data = json.loads(message)

                if data.get("type") == "orderbook_update":
                    ticker = data.get("ticker")
                    if ticker in self.ws_callbacks:
                        for callback in self.ws_callbacks[ticker]:
                            callback(data)

                elif data.get("type") == "trade":
                    ticker = data.get("ticker")
                    if ticker in self.ws_callbacks:
                        for callback in self.ws_callbacks[ticker]:
                            callback(data)

            except Exception as e:
                logger.error(f"WebSocket message error: {e}")

        def on_error(ws, error):
            logger.error(f"WebSocket error: {error}")

        def on_close(ws, close_status_code, close_msg):
            logger.info("WebSocket connection closed")

        def on_open(ws):
            """Authenticate and subscribe on connection."""
            if api_key:
                auth_message = {
                    "type": "authenticate",
                    "api_key": api_key
                }
                ws.send(json.dumps(auth_message))
                logger.info("✅ WebSocket authenticated")

        self.ws_client = websocket.WebSocketApp(
            ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        # Start WebSocket in background thread
        wst = threading.Thread(target=self.ws_client.run_forever)
        wst.daemon = True
        wst.start()

        logger.info("✅ WebSocket connected")

    def subscribe_market(
        self,
        ticker: str,
        callback: Callable[[Dict[str, Any]], None],
    ):
        """
        Subscribe to market updates via WebSocket.
        
        Args:
            ticker: Market ticker
            callback: Callback function for updates
        """
        if not self.ws_client:
            self.connect_websocket()

        if ticker not in self.ws_callbacks:
            self.ws_callbacks[ticker] = []

        self.ws_callbacks[ticker].append(callback)

        # Send subscription message
        subscribe_message = {
            "type": "subscribe",
            "channels": [f"orderbook:{ticker}", f"trades:{ticker}"]
        }

        if self.ws_client:
            self.ws_client.send(json.dumps(subscribe_message))
            logger.info(f"✅ Subscribed to {ticker}")

    def compare_resolution_criteria(
        self,
        polymarket_market: Dict[str, Any],
        kalshi_ticker: str,
    ) -> Dict[str, Any]:
        """
        Compare resolution criteria between Polymarket and Kalshi markets.
        
        Args:
            polymarket_market: Polymarket market dict
            kalshi_ticker: Kalshi market ticker
            
        Returns:
            Comparison result dictionary
        """
        kalshi_market = self.get_market(kalshi_ticker)

        if not kalshi_market:
            return {"error": "Kalshi market not found"}

        comparison = {
            "polymarket_question": polymarket_market.get("question"),
            "kalshi_title": kalshi_market.get("title"),
            "polymarket_resolution": polymarket_market.get("resolution_criteria"),
            "kalshi_rules": kalshi_market.get("rules_primary"),
            "compatible": False,
            "risk_factors": [],
        }

        # Simple compatibility check (enhance with NLI)
        poly_res = str(polymarket_market.get("resolution_criteria", "")).lower()
        kalshi_rules = str(kalshi_market.get("rules_primary", "")).lower()

        # Check for common resolution sources
        common_sources = ["ap news", "ap call", "associated press", "reuters", "bloomberg"]

        poly_has_source = any(source in poly_res for source in common_sources)
        kalshi_has_source = any(source in kalshi_rules for source in common_sources)

        if poly_has_source and kalshi_has_source:
            comparison["compatible"] = True
        else:
            comparison["risk_factors"].append("Different resolution sources")

        # Check resolution dates
        poly_date = polymarket_market.get("resolution_date")
        kalshi_close = kalshi_market.get("close_time")

        if poly_date and kalshi_close:
            # Compare dates (simplified)
            comparison["date_match"] = True  # Implement actual comparison
        else:
            comparison["risk_factors"].append("Missing resolution dates")

        return comparison


# ========================
# UTILITY FUNCTIONS
# ========================

def get_kalshi_client(
    api_key: Optional[str] = None,
    api_secret: Optional[str] = None,
    demo: bool = False,
) -> KalshiAPIClient:
    """Factory function for KalshiAPIClient."""
    return KalshiAPIClient(
        api_key=api_key,
        api_secret=api_secret,
        demo=demo,
    )


if __name__ == "__main__":
    # Test Kalshi client
    client = get_kalshi_client(demo=True)
    
    # Test fetching markets
    markets = client.get_markets(status="open", limit=10)
    print(f"✅ Fetched {len(markets)} markets")
    
    if markets:
        ticker = markets[0].get("ticker")
        print(f"Sample market: {ticker}")
        
        # Test orderbook
        orderbook = client.get_orderbook(ticker)
        if orderbook:
            print(f"✅ Orderbook fetched: {len(orderbook.yes_bids)} bid levels")

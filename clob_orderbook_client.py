"""
CLOB Orderbook Client - Real-time Polymarket CLOB API integration

Provides:
- Live orderbook data fetching
- WebSocket connections for real-time updates
- Historical orderbook data collection
- Bid/ask spread tracking
"""

import os
import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import aiohttp
import websockets
from websockets.client import WebSocketClientProtocol

try:
    from py_clob_client.client import ClobClient
    from py_clob_client.clob_types import OrderArgs, OrderType
    CLOB_AVAILABLE = True
except ImportError:
    CLOB_AVAILABLE = False
    logging.warning("py-clob-client not installed. CLOB features disabled.")

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderbookUpdateType(Enum):
    """Types of orderbook updates."""
    PRICE_UPDATE = "price_update"
    ORDER_FILLED = "order_filled"
    NEW_ORDER = "new_order"
    ORDER_CANCELLED = "order_cancelled"
    MARKET_CLOSED = "market_closed"


@dataclass
class OrderbookLevel:
    """Single orderbook level (bid or ask)."""
    price: float
    size: float
    timestamp: float


@dataclass
class OrderbookSnapshot:
    """Complete orderbook snapshot."""
    market_id: str
    condition_id: str
    token_id: str
    bids: List[OrderbookLevel]
    asks: List[OrderbookLevel]
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    spread_pct: Optional[float]
    timestamp: float
    mid_price: Optional[float]


@dataclass
class HistoricalOrderbookData:
    """Historical orderbook data point."""
    market_id: str
    timestamp: float
    best_bid: Optional[float]
    best_ask: Optional[float]
    spread: Optional[float]
    bid_depth: float  # Total liquidity on bid side
    ask_depth: float  # Total liquidity on ask side
    snapshot: Dict[str, Any]


class CLOBOrderbookClient:
    """
    Client for fetching and monitoring Polymarket CLOB orderbook data.
    
    Features:
    - Real-time orderbook fetching via REST API
    - WebSocket subscriptions for live updates
    - Historical data collection for backtesting
    - Spread tracking and arbitrage detection
    """

    def __init__(
        self,
        api_url: str = "https://clob.polymarket.com",
        ws_url: str = "wss://ws-subscriptions-clob.polymarket.com/ws",
        private_key: Optional[str] = None,
    ):
        """
        Initialize CLOB orderbook client.
        
        Args:
            api_url: CLOB REST API URL
            ws_url: WebSocket URL for real-time updates
            private_key: Wallet private key (optional, needed for authenticated operations)
        """
        self.api_url = api_url
        self.ws_url = ws_url
        self.private_key = private_key or os.getenv("POLYGON_PRIVATE_KEY")
        self.client: Optional[ClobClient] = None
        self.ws_connection: Optional[WebSocketClientProtocol] = None
        self.ws_subscriptions: Dict[str, List[Callable]] = {}
        self.historical_data: List[HistoricalOrderbookData] = []
        self._init_client()

    def _init_client(self):
        """Initialize CLOB client if available."""
        if not CLOB_AVAILABLE:
            logger.warning("CLOB client not available - install py-clob-client")
            return

        if not self.private_key:
            logger.warning("No private key provided - some features may be limited")
            return

        try:
            from eth_account import Account
            from web3 import Web3
            
            self.client = ClobClient(
                self.api_url,
                chain_id=137,  # Polygon
                key=self.private_key,
            )
            # Derive API credentials if needed
            try:
                self.client.set_api_creds(self.client.create_or_derive_api_creds())
            except Exception as e:
                logger.warning(f"Could not set API credentials: {e}")
            
            logger.info("✅ CLOB client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize CLOB client: {e}")

    async def get_orderbook(
        self,
        token_id: str,
        condition_id: Optional[str] = None,
    ) -> Optional[OrderbookSnapshot]:
        """
        Fetch current orderbook snapshot for a token.
        
        Args:
            token_id: Polymarket token ID
            condition_id: Optional condition ID for market identification
            
        Returns:
            OrderbookSnapshot or None if fetch fails
        """
        if not self.client:
            logger.error("CLOB client not initialized")
            return None

        try:
            # Use CLOB client to get orderbook
            book_params = [{"token_id": token_id}]
            order_books = await asyncio.to_thread(self.client.getOrderBooks, book_params)
            
            if not order_books or len(order_books) == 0:
                logger.warning(f"No orderbook found for token {token_id}")
                return None

            order_book = order_books[0]
            
            # Parse bids and asks
            bids = [
                OrderbookLevel(
                    price=float(bid.get("price", 0)),
                    size=float(bid.get("size", 0)),
                    timestamp=time.time()
                )
                for bid in order_book.get("bids", [])
            ]
            
            asks = [
                OrderbookLevel(
                    price=float(ask.get("price", 0)),
                    size=float(ask.get("size", 0)),
                    timestamp=time.time()
                )
                for ask in order_book.get("asks", [])
            ]

            # Calculate best bid/ask and spread
            best_bid = bids[0].price if bids else None
            best_ask = asks[0].price if asks else None
            spread = (best_ask - best_bid) if (best_bid and best_ask) else None
            spread_pct = (spread / best_bid * 100) if (spread and best_bid) else None
            mid_price = ((best_bid + best_ask) / 2) if (best_bid and best_ask) else None

            snapshot = OrderbookSnapshot(
                market_id=order_book.get("market", ""),
                condition_id=condition_id or order_book.get("condition_id", ""),
                token_id=token_id,
                bids=bids,
                asks=asks,
                best_bid=best_bid,
                best_ask=best_ask,
                spread=spread,
                spread_pct=spread_pct,
                timestamp=time.time(),
                mid_price=mid_price,
            )

            logger.info(
                f"📊 Orderbook fetched: {token_id} | "
                f"Bid: {best_bid:.4f} | Ask: {best_ask:.4f} | "
                f"Spread: {spread_pct:.2f}%" if spread_pct else "N/A"
            )

            return snapshot

        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            return None

    async def get_multiple_orderbooks(
        self,
        token_ids: List[str],
    ) -> Dict[str, Optional[OrderbookSnapshot]]:
        """
        Fetch orderbooks for multiple tokens in parallel.
        
        Args:
            token_ids: List of token IDs
            
        Returns:
            Dict mapping token_id to OrderbookSnapshot
        """
        tasks = [self.get_orderbook(token_id) for token_id in token_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        orderbooks = {}
        for token_id, result in zip(token_ids, results):
            if isinstance(result, Exception):
                logger.error(f"Error fetching orderbook for {token_id}: {result}")
                orderbooks[token_id] = None
            else:
                orderbooks[token_id] = result
        
        return orderbooks

    async def connect_websocket(self) -> bool:
        """
        Connect to CLOB WebSocket for real-time updates.
        
        Returns:
            True if connection successful
        """
        try:
            logger.info(f"Connecting to WebSocket: {self.ws_url}")
            self.ws_connection = await websockets.connect(self.ws_url)
            logger.info("✅ WebSocket connected")
            return True
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False

    async def subscribe_market(
        self,
        token_id: str,
        callback: Callable[[Dict[str, Any]], None],
    ):
        """
        Subscribe to real-time updates for a market.
        
        Args:
            token_id: Token ID to subscribe to
            callback: Function to call when update received
        """
        if not self.ws_connection:
            if not await self.connect_websocket():
                logger.error("Cannot subscribe - WebSocket not connected")
                return

        # Register callback
        if token_id not in self.ws_subscriptions:
            self.ws_subscriptions[token_id] = []
        self.ws_subscriptions[token_id].append(callback)

        # Send subscription message
        subscription_msg = {
            "type": "market",
            "markets": [token_id],
            "initial_dump": True,
        }

        try:
            await self.ws_connection.send(json.dumps(subscription_msg))
            logger.info(f"✅ Subscribed to market: {token_id}")
        except Exception as e:
            logger.error(f"Failed to subscribe: {e}")

    async def listen_for_updates(self):
        """Listen for WebSocket updates and route to callbacks."""
        if not self.ws_connection:
            logger.error("WebSocket not connected")
            return

        try:
            async for message in self.ws_connection:
                try:
                    data = json.loads(message)
                    token_id = data.get("token_id") or data.get("market_id")
                    
                    if token_id and token_id in self.ws_subscriptions:
                        for callback in self.ws_subscriptions[token_id]:
                            try:
                                callback(data)
                            except Exception as e:
                                logger.error(f"Callback error: {e}")
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON message: {message}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.ws_connection = None
        except Exception as e:
            logger.error(f"WebSocket listen error: {e}")

    async def collect_historical_data(
        self,
        token_id: str,
        duration_minutes: int = 60,
        interval_seconds: int = 30,
    ) -> List[HistoricalOrderbookData]:
        """
        Collect historical orderbook data for backtesting.
        
        Args:
            token_id: Token ID to collect data for
            duration_minutes: How long to collect data
            interval_seconds: Interval between snapshots
            
        Returns:
            List of historical data points
        """
        logger.info(
            f"📈 Collecting historical data for {token_id} "
            f"({duration_minutes}min, {interval_seconds}s interval)"
        )

        end_time = time.time() + (duration_minutes * 60)
        data_points = []

        while time.time() < end_time:
            snapshot = await self.get_orderbook(token_id)
            
            if snapshot:
                historical_point = HistoricalOrderbookData(
                    market_id=snapshot.market_id,
                    timestamp=snapshot.timestamp,
                    best_bid=snapshot.best_bid,
                    best_ask=snapshot.best_ask,
                    spread=snapshot.spread,
                    bid_depth=sum(bid.size for bid in snapshot.bids),
                    ask_depth=sum(ask.size for ask in snapshot.asks),
                    snapshot=asdict(snapshot),
                )
                data_points.append(historical_point)
                self.historical_data.append(historical_point)

            await asyncio.sleep(interval_seconds)

        logger.info(f"✅ Collected {len(data_points)} data points")
        return data_points

    def save_historical_data(self, filepath: str):
        """Save collected historical data to JSON file."""
        data = [asdict(point) for point in self.historical_data]
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"💾 Saved {len(data)} data points to {filepath}")

    def load_historical_data(self, filepath: str) -> List[HistoricalOrderbookData]:
        """Load historical data from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)
        
        historical_points = [
            HistoricalOrderbookData(**point) for point in data
        ]
        self.historical_data.extend(historical_points)
        logger.info(f"📂 Loaded {len(historical_points)} data points from {filepath}")
        return historical_points

    async def track_spread(
        self,
        token_id: str,
        min_spread_pct: float = 2.5,
        callback: Optional[Callable[[OrderbookSnapshot], None]] = None,
    ):
        """
        Continuously track spread and alert when threshold is met.
        
        Args:
            token_id: Token ID to track
            min_spread_pct: Minimum spread percentage to trigger alert
            callback: Optional callback when threshold met
        """
        logger.info(f"🔍 Tracking spread for {token_id} (min: {min_spread_pct}%)")

        async def on_update(data: Dict[str, Any]):
            snapshot = await self.get_orderbook(token_id)
            if snapshot and snapshot.spread_pct:
                if snapshot.spread_pct >= min_spread_pct:
                    logger.info(
                        f"🚨 ARBITRAGE OPPORTUNITY: {token_id} | "
                        f"Spread: {snapshot.spread_pct:.2f}%"
                    )
                    if callback:
                        callback(snapshot)

        await self.subscribe_market(token_id, on_update)
        await self.listen_for_updates()

    async def close(self):
        """Close WebSocket connection."""
        if self.ws_connection:
            await self.ws_connection.close()
            logger.info("WebSocket connection closed")


# ========================
# UTILITY FUNCTIONS
# ========================

def get_clob_orderbook_client(
    api_url: Optional[str] = None,
    ws_url: Optional[str] = None,
) -> CLOBOrderbookClient:
    """Factory function for CLOBOrderbookClient."""
    return CLOBOrderbookClient(
        api_url=api_url or os.getenv("CLOB_API_URL", "https://clob.polymarket.com"),
        ws_url=ws_url or os.getenv("CLOB_WS_URL", "wss://ws-subscriptions-clob.polymarket.com/ws"),
    )


if __name__ == "__main__":
    # Test the orderbook client
    async def test_orderbook_client():
        client = get_clob_orderbook_client()
        
        # Test fetching orderbook (requires valid token ID)
        # token_id = "123456"  # Replace with actual token ID
        # snapshot = await client.get_orderbook(token_id)
        # if snapshot:
        #     print(f"Best Bid: {snapshot.best_bid}")
        #     print(f"Best Ask: {snapshot.best_ask}")
        #     print(f"Spread: {snapshot.spread_pct:.2f}%")
        
        print("✅ Orderbook client test complete")

    asyncio.run(test_orderbook_client())

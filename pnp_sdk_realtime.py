"""
PNP SDK Real-Time Integration

Real-time integration layer for PNP Exchange SDK with WebSocket support,
event handling, and seamless switching between mock and real SDK implementations.
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
from enum import Enum
import threading
from dataclasses import dataclass

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Warning: websockets package not installed. Install with: pip install websockets")

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("Warning: aiohttp package not installed. Install with: pip install aiohttp")


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SDKMode(Enum):
    """SDK operation mode."""
    MOCK = "mock"
    REAL = "real"
    AUTO = "auto"  # Auto-detect based on availability


class EventType(Enum):
    """Real-time event types."""
    MARKET_CREATED = "market.created"
    MARKET_UPDATED = "market.updated"
    MARKET_SETTLED = "market.settled"
    ORDER_PLACED = "order.placed"
    ORDER_FILLED = "order.filled"
    ORDER_CANCELLED = "order.cancelled"
    PRICE_UPDATE = "price.update"
    VOLUME_UPDATE = "volume.update"
    ERROR = "error"


@dataclass
class RealtimeEvent:
    """Real-time event data structure."""
    event_type: EventType
    timestamp: datetime
    data: Dict[str, Any]
    market_id: Optional[str] = None
    order_id: Optional[str] = None


class PNPSDKRealtime:
    """
    Real-time PNP SDK integration with WebSocket support.
    
    Features:
    - WebSocket connection for real-time updates
    - Event-driven architecture
    - Automatic reconnection
    - Support for both mock and real SDK
    """
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 api_url: Optional[str] = None,
                 ws_url: Optional[str] = None,
                 mode: SDKMode = SDKMode.AUTO,
                 sdk_instance=None):
        """
        Initialize real-time PNP SDK client.
        
        Args:
            api_key: PNP Exchange API key (for real SDK)
            api_url: Base API URL (defaults to production)
            ws_url: WebSocket URL (defaults to wss://api.pnp.exchange/ws)
            mode: SDK mode (MOCK, REAL, or AUTO)
            sdk_instance: Existing SDK instance to use (for mock mode)
        """
        self.api_key = api_key
        self.api_url = api_url or "https://api.pnp.exchange"
        self.ws_url = ws_url or "wss://api.pnp.exchange/ws"
        self.mode = mode
        self.sdk_instance = sdk_instance
        
        # Real-time connection state
        self.ws: Optional[WebSocketClientProtocol] = None
        self.ws_connected = False
        self.ws_task: Optional[asyncio.Task] = None
        self.reconnect_delay = 5
        self.max_reconnect_delay = 60
        
        # Event handlers
        self.event_handlers: Dict[EventType, List[Callable[[RealtimeEvent], Awaitable[None]]]] = {
            event_type: [] for event_type in EventType
        }
        
        # Subscriptions
        self.subscribed_markets: set = set()
        self.subscribed_orders: set = set()
        
        # Determine SDK mode
        if mode == SDKMode.AUTO:
            if api_key and WEBSOCKETS_AVAILABLE:
                self.mode = SDKMode.REAL
            else:
                self.mode = SDKMode.MOCK
                if not sdk_instance:
                    from pnp_sdk_mock import get_sdk
                    self.sdk_instance = get_sdk()
        
        logger.info(f"PNP SDK Realtime initialized in {self.mode.value} mode")
    
    def _get_sdk(self):
        """Get the appropriate SDK instance."""
        if self.mode == SDKMode.MOCK:
            if not self.sdk_instance:
                from pnp_sdk_mock import get_sdk
                self.sdk_instance = get_sdk()
            return self.sdk_instance
        else:
            # Real SDK will be implemented here when available
            return self._real_sdk_client()
    
    def _real_sdk_client(self):
        """Real SDK client (to be implemented when SDK is available)."""
        # Placeholder for real SDK implementation
        raise NotImplementedError(
            "Real PNP SDK not yet available. "
            "See https://docs.pnp.exchange/api-reference/introduction for updates."
        )
    
    # Synchronous SDK methods (delegated to underlying SDK)
    
    def create_market(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a prediction market."""
        result = self._get_sdk().create_market(params)
        
        # Emit real-time event
        if self.ws_connected:
            asyncio.create_task(self._emit_event(EventType.MARKET_CREATED, {
                'market_id': result.get('market_id'),
                'question': params.get('question'),
                'status': result.get('status')
            }, market_id=result.get('market_id')))
        
        return result
    
    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order."""
        result = self._get_sdk().place_order(params)
        
        # Emit real-time event
        if self.ws_connected:
            asyncio.create_task(self._emit_event(EventType.ORDER_PLACED, {
                'order_id': result.get('order_id'),
                'market_id': params.get('market_id'),
                'status': result.get('status')
            }, order_id=result.get('order_id'), market_id=params.get('market_id')))
        
        return result
    
    def settle_market(self, market_id: str, outcome: str, resolver: Optional[str] = None) -> Dict[str, Any]:
        """Settle a market."""
        result = self._get_sdk().settle_market(market_id, outcome, resolver)
        
        # Emit real-time event
        if self.ws_connected:
            asyncio.create_task(self._emit_event(EventType.MARKET_SETTLED, {
                'market_id': market_id,
                'winning_outcome': outcome,
                'resolver': resolver
            }, market_id=market_id))
        
        return result
    
    def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market details."""
        return self._get_sdk().get_market(market_id)
    
    def list_markets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List markets."""
        return self._get_sdk().list_markets(status)
    
    def get_orders(self, market_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders."""
        return self._get_sdk().get_orders(market_id)
    
    # Real-time WebSocket methods
    
    async def connect(self):
        """Connect to WebSocket for real-time updates."""
        if not WEBSOCKETS_AVAILABLE:
            logger.warning("WebSockets not available. Real-time features disabled.")
            return
        
        if self.mode == SDKMode.MOCK:
            logger.info("Mock mode: WebSocket connection simulated")
            self.ws_connected = True
            return
        
        try:
            # Build WebSocket URL with authentication
            ws_url = self.ws_url
            if self.api_key:
                # Add auth token to URL or headers (implementation depends on PNP API)
                ws_url = f"{ws_url}?token={self.api_key}"
            
            logger.info(f"Connecting to WebSocket: {ws_url}")
            self.ws = await websockets.connect(ws_url)
            self.ws_connected = True
            
            # Start listening for messages
            self.ws_task = asyncio.create_task(self._listen_messages())
            
            # Subscribe to previously subscribed markets/orders
            if self.subscribed_markets:
                await self.subscribe_markets(list(self.subscribed_markets))
            if self.subscribed_orders:
                await self.subscribe_orders(list(self.subscribed_orders))
            
            logger.info("WebSocket connected successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {e}")
            self.ws_connected = False
            if self.mode == SDKMode.REAL:
                # Schedule reconnection
                asyncio.create_task(self._reconnect())
    
    async def disconnect(self):
        """Disconnect from WebSocket."""
        self.ws_connected = False
        if self.ws_task:
            self.ws_task.cancel()
            try:
                await self.ws_task
            except asyncio.CancelledError:
                pass
        
        if self.ws:
            await self.ws.close()
            self.ws = None
        
        logger.info("WebSocket disconnected")
    
    async def _listen_messages(self):
        """Listen for incoming WebSocket messages."""
        try:
            async for message in self.ws:
                try:
                    data = json.loads(message)
                    await self._handle_ws_message(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse WebSocket message: {e}")
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {e}")
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.ws_connected = False
            if self.mode == SDKMode.REAL:
                await self._reconnect()
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            self.ws_connected = False
    
    async def _handle_ws_message(self, data: Dict[str, Any]):
        """Handle incoming WebSocket message."""
        event_type_str = data.get('type') or data.get('event')
        if not event_type_str:
            logger.warning(f"Unknown message format: {data}")
            return
        
        try:
            event_type = EventType(event_type_str)
        except ValueError:
            logger.warning(f"Unknown event type: {event_type_str}")
            return
        
        event = RealtimeEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data.get('data', data),
            market_id=data.get('market_id'),
            order_id=data.get('order_id')
        )
        
        await self._dispatch_event(event)
    
    async def _reconnect(self):
        """Reconnect to WebSocket with exponential backoff."""
        delay = self.reconnect_delay
        while not self.ws_connected:
            try:
                await asyncio.sleep(delay)
                logger.info(f"Attempting to reconnect... (delay: {delay}s)")
                await self.connect()
                if self.ws_connected:
                    delay = self.reconnect_delay  # Reset delay on success
            except Exception as e:
                logger.error(f"Reconnection failed: {e}")
                delay = min(delay * 2, self.max_reconnect_delay)
    
    async def subscribe_markets(self, market_ids: List[str]):
        """Subscribe to real-time updates for specific markets."""
        if not self.ws_connected:
            logger.warning("WebSocket not connected. Subscription queued.")
            self.subscribed_markets.update(market_ids)
            return
        
        if self.mode == SDKMode.MOCK:
            self.subscribed_markets.update(market_ids)
            logger.info(f"Subscribed to markets (mock): {market_ids}")
            return
        
        # Send subscription message
        message = {
            'action': 'subscribe',
            'type': 'markets',
            'market_ids': market_ids
        }
        
        try:
            await self.ws.send(json.dumps(message))
            self.subscribed_markets.update(market_ids)
            logger.info(f"Subscribed to markets: {market_ids}")
        except Exception as e:
            logger.error(f"Failed to subscribe to markets: {e}")
    
    async def subscribe_orders(self, order_ids: List[str]):
        """Subscribe to real-time updates for specific orders."""
        if not self.ws_connected:
            logger.warning("WebSocket not connected. Subscription queued.")
            self.subscribed_orders.update(order_ids)
            return
        
        if self.mode == SDKMode.MOCK:
            self.subscribed_orders.update(order_ids)
            logger.info(f"Subscribed to orders (mock): {order_ids}")
            return
        
        # Send subscription message
        message = {
            'action': 'subscribe',
            'type': 'orders',
            'order_ids': order_ids
        }
        
        try:
            await self.ws.send(json.dumps(message))
            self.subscribed_orders.update(order_ids)
            logger.info(f"Subscribed to orders: {order_ids}")
        except Exception as e:
            logger.error(f"Failed to subscribe to orders: {e}")
    
    async def unsubscribe_markets(self, market_ids: List[str]):
        """Unsubscribe from market updates."""
        self.subscribed_markets -= set(market_ids)
        
        if self.ws_connected and self.mode == SDKMode.REAL:
            message = {
                'action': 'unsubscribe',
                'type': 'markets',
                'market_ids': market_ids
            }
            try:
                await self.ws.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to unsubscribe from markets: {e}")
    
    # Event handling
    
    def on_event(self, event_type: EventType, handler: Callable[[RealtimeEvent], Awaitable[None]]):
        """Register an event handler."""
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for {event_type.value}")
    
    def off_event(self, event_type: EventType, handler: Callable[[RealtimeEvent], Awaitable[None]]):
        """Unregister an event handler."""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
    
    async def _emit_event(self, event_type: EventType, data: Dict[str, Any],
                         market_id: Optional[str] = None, order_id: Optional[str] = None):
        """Emit an event to registered handlers."""
        event = RealtimeEvent(
            event_type=event_type,
            timestamp=datetime.utcnow(),
            data=data,
            market_id=market_id,
            order_id=order_id
        )
        await self._dispatch_event(event)
    
    async def _dispatch_event(self, event: RealtimeEvent):
        """Dispatch event to all registered handlers."""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Error in event handler for {event.event_type.value}: {e}")


# Convenience function for synchronous usage
def get_realtime_sdk(api_key: Optional[str] = None,
                     mode: SDKMode = SDKMode.AUTO,
                     **kwargs) -> PNPSDKRealtime:
    """
    Get a real-time PNP SDK instance.
    
    Args:
        api_key: PNP Exchange API key
        mode: SDK mode (MOCK, REAL, or AUTO)
        **kwargs: Additional arguments for PNPSDKRealtime
    
    Returns:
        PNPSDKRealtime instance
    """
    return PNPSDKRealtime(api_key=api_key, mode=mode, **kwargs)


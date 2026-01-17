"""
PNP SDK Adapter

Unified adapter interface for PNP SDK that seamlessly switches between
mock and real SDK implementations. Provides a consistent API regardless
of which SDK is being used.
"""

import os
from typing import Dict, Any, List, Optional
from pnp_sdk_realtime import PNPSDKRealtime, SDKMode, get_realtime_sdk


class PNPSDKAdapter:
    """
    Unified adapter for PNP SDK that works with both mock and real implementations.
    
    This adapter provides a consistent interface and automatically handles
    the transition from mock to real SDK when available.
    """
    
    def __init__(self,
                 api_key: Optional[str] = None,
                 use_realtime: bool = True,
                 mode: Optional[SDKMode] = None):
        """
        Initialize PNP SDK adapter.
        
        Args:
            api_key: PNP Exchange API key (from env or parameter)
            use_realtime: Whether to enable real-time WebSocket features
            mode: Force SDK mode (MOCK, REAL, or AUTO). Defaults to AUTO.
        """
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.getenv('PNP_API_KEY') or os.getenv('PNP_EXCHANGE_API_KEY')
        
        # Determine mode
        if mode is None:
            mode = SDKMode.AUTO
        
        # Initialize real-time SDK
        self.realtime_sdk = get_realtime_sdk(
            api_key=api_key,
            mode=mode
        )
        
        self.use_realtime = use_realtime
        self._realtime_connected = False
    
    # Delegate all SDK methods to realtime_sdk
    
    def create_market(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create a prediction market."""
        return self.realtime_sdk.create_market(params)
    
    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Place an order."""
        return self.realtime_sdk.place_order(params)
    
    def settle_market(self, market_id: str, outcome: str, resolver: Optional[str] = None) -> Dict[str, Any]:
        """Settle a market."""
        return self.realtime_sdk.settle_market(market_id, outcome, resolver)
    
    def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market details."""
        return self.realtime_sdk.get_market(market_id)
    
    def list_markets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List markets."""
        return self.realtime_sdk.list_markets(status)
    
    def get_orders(self, market_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get orders."""
        return self.realtime_sdk.get_orders(market_id)
    
    # Real-time methods
    
    async def connect_realtime(self):
        """Connect to real-time WebSocket."""
        if self.use_realtime:
            await self.realtime_sdk.connect()
            self._realtime_connected = True
    
    async def disconnect_realtime(self):
        """Disconnect from real-time WebSocket."""
        if self._realtime_connected:
            await self.realtime_sdk.disconnect()
            self._realtime_connected = False
    
    def on_market_created(self, handler):
        """Register handler for market created events."""
        from pnp_sdk_realtime import EventType
        self.realtime_sdk.on_event(EventType.MARKET_CREATED, handler)
    
    def on_market_updated(self, handler):
        """Register handler for market updated events."""
        from pnp_sdk_realtime import EventType
        self.realtime_sdk.on_event(EventType.MARKET_UPDATED, handler)
    
    def on_market_settled(self, handler):
        """Register handler for market settled events."""
        from pnp_sdk_realtime import EventType
        self.realtime_sdk.on_event(EventType.MARKET_SETTLED, handler)
    
    def on_order_placed(self, handler):
        """Register handler for order placed events."""
        from pnp_sdk_realtime import EventType
        self.realtime_sdk.on_event(EventType.ORDER_PLACED, handler)
    
    def on_order_filled(self, handler):
        """Register handler for order filled events."""
        from pnp_sdk_realtime import EventType
        self.realtime_sdk.on_event(EventType.ORDER_FILLED, handler)
    
    def on_price_update(self, handler):
        """Register handler for price update events."""
        from pnp_sdk_realtime import EventType
        self.realtime_sdk.on_event(EventType.PRICE_UPDATE, handler)
    
    async def subscribe_market(self, market_id: str):
        """Subscribe to real-time updates for a market."""
        await self.realtime_sdk.subscribe_markets([market_id])
    
    async def subscribe_order(self, order_id: str):
        """Subscribe to real-time updates for an order."""
        await self.realtime_sdk.subscribe_orders([order_id])
    
    @property
    def is_realtime_connected(self) -> bool:
        """Check if real-time connection is active."""
        return self._realtime_connected and self.realtime_sdk.ws_connected
    
    @property
    def mode(self) -> str:
        """Get current SDK mode."""
        return self.realtime_sdk.mode.value


# Global instance for backward compatibility
_adapter_instance = None

def get_sdk(api_key: Optional[str] = None, use_realtime: bool = False) -> PNPSDKAdapter:
    """
    Get a PNP SDK adapter instance.
    
    This function maintains backward compatibility with the existing codebase
    while providing access to the new real-time features.
    
    Args:
        api_key: PNP Exchange API key
        use_realtime: Whether to enable real-time features
    
    Returns:
        PNPSDKAdapter instance
    """
    global _adapter_instance
    if _adapter_instance is None or not use_realtime:
        _adapter_instance = PNPSDKAdapter(api_key=api_key, use_realtime=use_realtime)
    return _adapter_instance


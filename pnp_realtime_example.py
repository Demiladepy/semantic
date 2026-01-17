"""
PNP SDK Real-Time Integration Example

Demonstrates how to use the real-time PNP SDK integration with WebSocket
support, event handlers, and market subscriptions.
"""

import asyncio
import json
from datetime import datetime
from pnp_sdk_realtime import get_realtime_sdk, EventType, RealtimeEvent
from pnp_sdk_adapter import PNPSDKAdapter


async def market_created_handler(event: RealtimeEvent):
    """Handle market created events."""
    print(f"\n[EVENT] Market Created!")
    print(f"  Market ID: {event.market_id}")
    print(f"  Data: {json.dumps(event.data, indent=2)}")
    print(f"  Timestamp: {event.timestamp}")


async def order_filled_handler(event: RealtimeEvent):
    """Handle order filled events."""
    print(f"\n[EVENT] Order Filled!")
    print(f"  Order ID: {event.order_id}")
    print(f"  Market ID: {event.market_id}")
    print(f"  Data: {json.dumps(event.data, indent=2)}")


async def price_update_handler(event: RealtimeEvent):
    """Handle price update events."""
    print(f"\n[EVENT] Price Update!")
    print(f"  Market ID: {event.market_id}")
    print(f"  Price Data: {json.dumps(event.data, indent=2)}")


async def market_settled_handler(event: RealtimeEvent):
    """Handle market settled events."""
    print(f"\n[EVENT] Market Settled!")
    print(f"  Market ID: {event.market_id}")
    print(f"  Winning Outcome: {event.data.get('winning_outcome')}")
    print(f"  Resolver: {event.data.get('resolver')}")


async def example_realtime_integration():
    """Example of real-time PNP SDK integration."""
    print("=" * 60)
    print("PNP SDK Real-Time Integration Example")
    print("=" * 60)
    
    # Initialize real-time SDK
    # In mock mode, WebSocket is simulated
    # In real mode, it connects to PNP Exchange WebSocket
    from pnp_sdk_realtime import SDKMode
    sdk = get_realtime_sdk(
        api_key=None,  # Set your PNP API key here when available
        mode=SDKMode.AUTO  # Auto-detect: uses mock if no API key, real if API key provided
    )
    
    print(f"\nSDK Mode: {sdk.mode.value}")
    print(f"WebSockets Available: {sdk.ws_connected}")
    
    # Register event handlers
    sdk.on_event(EventType.MARKET_CREATED, market_created_handler)
    sdk.on_event(EventType.ORDER_FILLED, order_filled_handler)
    sdk.on_event(EventType.PRICE_UPDATE, price_update_handler)
    sdk.on_event(EventType.MARKET_SETTLED, market_settled_handler)
    
    # Connect to WebSocket (if in real mode)
    print("\nConnecting to WebSocket...")
    await sdk.connect()
    
    # Create a market (this will trigger MARKET_CREATED event)
    print("\n" + "-" * 60)
    print("Creating a market...")
    print("-" * 60)
    
    market_result = sdk.create_market({
        'question': 'Will AI achieve AGI by 2025?',
        'outcomes': ['Yes', 'No'],
        'collateral_token': 'ELUSIV',
        'collateral_amount': 100.0,
        'resolution_criteria': 'Based on consensus definition of AGI'
    })
    
    market_id = market_result['market_id']
    print(f"Market created: {market_id}")
    
    # Subscribe to market updates
    print(f"\nSubscribing to market {market_id}...")
    await sdk.subscribe_markets([market_id])
    
    # Place an order (this will trigger ORDER_PLACED event)
    print("\n" + "-" * 60)
    print("Placing an order...")
    print("-" * 60)
    
    order_result = sdk.place_order({
        'market_id': market_id,
        'outcome': 'Yes',
        'side': 'buy',
        'amount': 10.0,
        'price': 0.6
    })
    
    order_id = order_result['order_id']
    print(f"Order placed: {order_id}")
    
    # Subscribe to order updates
    await sdk.subscribe_orders([order_id])
    
    # Wait a bit to see events
    print("\nWaiting for events...")
    await asyncio.sleep(2)
    
    # Settle the market (this will trigger MARKET_SETTLED event)
    print("\n" + "-" * 60)
    print("Settling the market...")
    print("-" * 60)
    
    settlement_result = sdk.settle_market(
        market_id=market_id,
        outcome='Yes',
        resolver='example-agent'
    )
    
    print(f"Market settled: {settlement_result}")
    
    # Wait for final events
    await asyncio.sleep(1)
    
    # Disconnect
    print("\nDisconnecting from WebSocket...")
    await sdk.disconnect()
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


async def example_with_adapter():
    """Example using the SDK adapter for easier integration."""
    print("\n" + "=" * 60)
    print("PNP SDK Adapter Example")
    print("=" * 60)
    
    # Use the adapter for a cleaner API
    adapter = PNPSDKAdapter(
        api_key=None,  # Set your PNP API key here
        use_realtime=True
    )
    
    # Connect to real-time
    await adapter.connect_realtime()
    
    # Register handlers using convenience methods
    async def on_market_created(event):
        print(f"Market created: {event.market_id}")
    
    adapter.on_market_created(on_market_created)
    
    # Create market
    result = adapter.create_market({
        'question': 'Example market question?',
        'outcomes': ['Yes', 'No'],
        'collateral_token': 'ELUSIV',
        'collateral_amount': 50.0
    })
    
    # Subscribe to market
    await adapter.subscribe_market(result['market_id'])
    
    # Wait and disconnect
    await asyncio.sleep(1)
    await adapter.disconnect_realtime()
    
    print("Adapter example completed!")


def main():
    """Run examples."""
    # Run async examples
    asyncio.run(example_realtime_integration())
    asyncio.run(example_with_adapter())


if __name__ == "__main__":
    main()


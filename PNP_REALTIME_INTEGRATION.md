# PNP SDK Real-Time Integration Guide

This document describes the real-time integration with the PNP Exchange SDK for prediction markets.

## Overview

The real-time integration provides:
- **WebSocket Support**: Real-time market updates, order fills, and price changes
- **Event-Driven Architecture**: Register handlers for market and order events  
- **Seamless SDK Switching**: Automatically uses mock SDK for development, real SDK when API key is provided
- **Auto-Reconnection**: Automatic WebSocket reconnection with exponential backoff

## Architecture

```
┌─────────────────┐
│   PNPAgent      │  ← High-level agent interface
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PNPSDKAdapter   │  ← Unified adapter interface
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PNPSDKRealtime  │  ← Real-time SDK with WebSocket
└────────┬────────┘
         │
         ├──► Mock SDK (development)
         └──► Real SDK (production, when available)
```

## Components

### 1. PNPSDKRealtime (`pnp_sdk_realtime.py`)

Core real-time SDK implementation with WebSocket support.

**Features:**
- WebSocket connection management
- Event subscription and handling
- Automatic reconnection
- Support for both mock and real SDK modes

**Key Methods:**
- `create_market(params)`: Create a prediction market
- `place_order(params)`: Place an order
- `settle_market(market_id, outcome)`: Settle a market
- `connect()`: Connect to WebSocket
- `disconnect()`: Disconnect from WebSocket
- `subscribe_markets(market_ids)`: Subscribe to market updates
- `on_event(event_type, handler)`: Register event handler

### 2. PNPSDKAdapter (`pnp_sdk_adapter.py`)

Unified adapter that provides a consistent interface regardless of SDK mode.

**Features:**
- Automatic mode detection (mock vs real)
- Convenience methods for event handling
- Backward compatibility with existing code

### 3. Event Types

The SDK supports the following event types:

- `MARKET_CREATED`: New market created
- `MARKET_UPDATED`: Market state updated
- `MARKET_SETTLED`: Market resolved
- `ORDER_PLACED`: New order placed
- `ORDER_FILLED`: Order filled
- `ORDER_CANCELLED`: Order cancelled
- `PRICE_UPDATE`: Market price updated
- `VOLUME_UPDATE`: Market volume updated
- `ERROR`: Error occurred

## Usage Examples

### Basic Real-Time Integration

```python
from pnp_sdk_realtime import get_realtime_sdk, EventType, SDKMode
import asyncio

async def main():
    # Initialize SDK
    sdk = get_realtime_sdk(
        api_key="your-api-key",  # Optional: uses mock if not provided
        mode=SDKMode.AUTO
    )
    
    # Register event handlers
    async def on_market_created(event):
        print(f"Market created: {event.market_id}")
        print(f"Data: {event.data}")
    
    sdk.on_event(EventType.MARKET_CREATED, on_market_created)
    
    # Connect to WebSocket
    await sdk.connect()
    
    # Create market (triggers event)
    result = sdk.create_market({
        'question': 'Will AI achieve AGI by 2025?',
        'outcomes': ['Yes', 'No'],
        'collateral_token': 'ELUSIV',
        'collateral_amount': 100.0
    })
    
    # Subscribe to updates
    await sdk.subscribe_markets([result['market_id']])
    
    # Keep running
    await asyncio.sleep(10)
    await sdk.disconnect()

asyncio.run(main())
```

### Using the Adapter

```python
from pnp_sdk_adapter import PNPSDKAdapter
import asyncio

async def main():
    adapter = PNPSDKAdapter(
        api_key="your-api-key",
        use_realtime=True
    )
    
    await adapter.connect_realtime()
    
    # Convenience methods
    adapter.on_market_created(lambda e: print(f"Market: {e.market_id}"))
    adapter.on_order_filled(lambda e: print(f"Order filled: {e.order_id}"))
    
    # Create and subscribe
    market = adapter.create_market({...})
    await adapter.subscribe_market(market['market_id'])
    
    await asyncio.sleep(10)
    await adapter.disconnect_realtime()

asyncio.run(main())
```

### Integration with PNPAgent

```python
from pnp_agent import PNPAgent
import asyncio

async def main():
    # Initialize agent with real-time support
    agent = PNPAgent(
        default_collateral_token='ELUSIV',
        use_realtime=True,
        pnp_api_key="your-api-key"
    )
    
    # Agent automatically uses real-time SDK if enabled
    result = agent.create_market_from_prompt(
        "Bitcoin reaches $100,000 by end of 2024"
    )
    
    # Access real-time SDK if needed
    if agent.realtime_enabled:
        await agent.sdk.connect_realtime()
        await agent.sdk.subscribe_market(result['market_id'])

asyncio.run(main())
```

## Configuration

### Environment Variables

Set these in your `.env` file:

```bash
# PNP Exchange API Key (for real SDK)
PNP_API_KEY=your-api-key-here
PNP_EXCHANGE_API_KEY=your-api-key-here  # Alternative name

# OpenAI API Key (for agent)
OPENAI_API_KEY=your-openai-key
```

### SDK Modes

- **MOCK**: Always use mock SDK (for development/testing)
- **REAL**: Always use real SDK (requires API key)
- **AUTO**: Auto-detect based on API key availability (default)

## Real SDK Integration

When the PNP SDK becomes available (see [PNP SDK Documentation](https://docs.pnp.exchange/api-reference/introduction)), the integration will automatically work with the real SDK by:

1. Providing your API key via environment variable or parameter
2. The SDK will detect the API key and switch to REAL mode
3. WebSocket connections will use the actual PNP Exchange endpoints

**Expected API Structure:**
- Base API URL: `https://api.pnp.exchange`
- WebSocket URL: `wss://api.pnp.exchange/ws`
- Authentication: API key via header or query parameter

## Error Handling

The SDK includes robust error handling:

- **Connection Errors**: Automatic reconnection with exponential backoff
- **Event Handler Errors**: Errors in handlers are logged but don't crash the SDK
- **Invalid Events**: Unknown event types are logged and ignored
- **WebSocket Failures**: Graceful degradation to polling (if implemented)

## Testing

Run the example:

```bash
python pnp_realtime_example.py
```

This demonstrates:
- SDK initialization
- Event handler registration
- Market creation
- Order placement
- Market subscription
- Event handling

## Migration from Mock to Real SDK

The integration is designed for seamless migration:

1. **Development**: Use mock SDK (no API key needed)
2. **Testing**: Use mock SDK with real-time features simulated
3. **Production**: Provide API key, SDK automatically switches to real mode

No code changes required - just set the API key!

## Future Enhancements

When the real PNP SDK is available, we'll add:

- Full WebSocket protocol implementation
- Real-time price feeds
- Order book updates
- Market depth updates
- Trade history streaming
- Account balance updates

## References

- [PNP Exchange SDK Documentation](https://docs.pnp.exchange/api-reference/introduction)
- [PNP Exchange Website](https://pnp.exchange)
- Example code: `pnp_realtime_example.py`


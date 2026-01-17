# Installing PNP SDK

This guide explains how to install and use the official PNP SDK (`pnp-sdk` npm package) with this project.

## Prerequisites

1. **Node.js** (v16 or higher) - [Download Node.js](https://nodejs.org/)
2. **npm** (comes with Node.js)

## Installation Steps

### 1. Install the npm Package

Navigate to the `plugin-polymarket` directory and install the PNP SDK:

```bash
cd plugin-polymarket
npm install pnp-sdk
```

Or if you want to install a specific version:

```bash
npm install pnp-sdk@latest
```

### 2. Verify Installation

Check that `pnp-sdk` is in your `package.json`:

```bash
cat package.json | grep pnp-sdk
```

You should see `pnp-sdk` in the dependencies.

### 3. Get Your API Key

**Note:** As of January 2026, the PNP SDK is still "coming soon" according to the [official documentation](https://docs.pnp.exchange/api-reference/introduction). The API key generation page is not yet available.

When the SDK is fully released, you'll likely get an API key by:

1. Signing into the PNP Exchange developer dashboard (when available)
2. Creating a project/application
3. Copying the API key from your dashboard

**Current Status:**
- The npm package `pnp-sdk` exists but may be in early/beta stage
- Full API documentation is not yet published
- API key generation is not yet available

### 4. Configure Your API Key

Once you have an API key, set it in your environment:

**Option 1: Environment Variable**
```bash
export PNP_API_KEY=your-api-key-here
```

**Option 2: .env File**
Create or update `.env` in the project root:
```bash
PNP_API_KEY=your-api-key-here
```

## Usage

### Python Integration (via Node.js Bridge)

The project includes a Python bridge that allows you to use the npm `pnp-sdk` from Python:

```python
from pnp_sdk_adapter import PNPSDKAdapter

# Use Node.js SDK (npm pnp-sdk)
adapter = PNPSDKAdapter(
    api_key="your-api-key",
    use_nodejs_sdk=True  # Use npm package
)

# Create a market
result = adapter.create_market({
    'question': 'Will AI achieve AGI by 2025?',
    'outcomes': ['Yes', 'No'],
    'collateral_token': 'ELUSIV',
    'collateral_amount': 100.0
})
```

### TypeScript/JavaScript Usage

You can also use the SDK directly in TypeScript/JavaScript:

```typescript
import { PNPClient } from 'pnp-sdk';

const client = new PNPClient({
  apiKey: process.env.PNP_API_KEY
});

// Create a market
const market = await client.createMarket({
  question: 'Will AI achieve AGI by 2025?',
  outcomes: ['Yes', 'No'],
  collateralToken: 'ELUSIV',
  collateralAmount: 100.0
});
```

## SDK Modes

The adapter supports multiple SDK modes:

1. **Python Mock SDK** (default, no API key needed)
   - For development and testing
   - Fully functional mock implementation

2. **Python Real-Time SDK** (with API key)
   - Real-time WebSocket integration
   - Uses Python implementation

3. **Node.js SDK** (npm `pnp-sdk` package)
   - Official PNP SDK from npm
   - Requires Node.js installed
   - Use `use_nodejs_sdk=True` in adapter

## Troubleshooting

### Node.js Not Found

If you get "Node.js not found" errors:

1. Install Node.js from [nodejs.org](https://nodejs.org/)
2. Verify installation: `node --version`
3. Verify npm: `npm --version`

### Package Not Found

If `npm install pnp-sdk` fails:

1. Check npm registry: `npm config get registry`
2. Try with explicit registry: `npm install pnp-sdk --registry https://registry.npmjs.org/`
3. Check if package exists: Visit [npmjs.com/package/pnp-sdk](https://www.npmjs.com/package/pnp-sdk)

### API Key Issues

If you're getting authentication errors:

1. Verify your API key is set: `echo $PNP_API_KEY`
2. Check the `.env` file is loaded
3. Ensure the API key is valid (when SDK is fully released)

## Current Limitations

As the PNP SDK is still "coming soon":

- ⚠️ Full API documentation may not be available
- ⚠️ Some features may not be implemented yet
- ⚠️ API key generation is not yet available
- ⚠️ The npm package may be in beta/early stage

## Resources

- [PNP Exchange Documentation](https://docs.pnp.exchange)
- [PNP SDK API Reference](https://docs.pnp.exchange/api-reference/introduction)
- [PNP Protocol GitHub](https://github.com/orgs/pnp-protocol/repositories)
- [npm pnp-sdk Package](https://www.npmjs.com/package/pnp-sdk)

## Next Steps

1. Monitor the [PNP Exchange documentation](https://docs.pnp.exchange) for SDK release updates
2. Check the [PNP Protocol GitHub repositories](https://github.com/orgs/pnp-protocol/repositories) for SDK source code
3. Join PNP Exchange community channels for updates on API key availability
4. Use the mock SDK for development until the real SDK is fully available


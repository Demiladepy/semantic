# PNP SDK Integration Summary

## Overview

This project now supports integration with the official PNP SDK (`pnp-sdk` npm package) alongside the existing Python mock SDK and real-time integration.

## What Was Added

### 1. npm Package Integration
- ✅ Added `pnp-sdk` to `plugin-polymarket/package.json` dependencies
- ✅ Created installation scripts for Linux/Mac (`install_pnp_sdk.sh`) and Windows (`install_pnp_sdk.ps1`)
- ✅ Created comprehensive installation guide (`INSTALL_PNP_SDK.md`)

### 2. Node.js Bridge for Python
- ✅ Created `pnp_sdk_nodejs_bridge.py` - Python wrapper for the npm `pnp-sdk` package
- ✅ Allows Python code to use the official TypeScript/JavaScript SDK
- ✅ Handles Node.js execution, error handling, and JSON communication

### 3. Enhanced SDK Adapter
- ✅ Updated `pnp_sdk_adapter.py` to support three SDK modes:
  1. **Python Mock SDK** (default) - For development/testing
  2. **Python Real-Time SDK** - Real-time WebSocket integration
  3. **Node.js SDK** - Official npm `pnp-sdk` package

## Installation

### Quick Install

**Linux/Mac:**
```bash
bash install_pnp_sdk.sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy Bypass -File install_pnp_sdk.ps1
```

**Manual Install:**
```bash
cd plugin-polymarket
npm install pnp-sdk
```

### Prerequisites
- Node.js (v16+) - [Download](https://nodejs.org/)
- npm (comes with Node.js)

## Usage Examples

### Using npm SDK from Python

```python
from pnp_sdk_adapter import PNPSDKAdapter

# Use the official npm pnp-sdk package
adapter = PNPSDKAdapter(
    api_key="your-api-key",  # When available
    use_nodejs_sdk=True      # Use npm package
)

# Create a market
result = adapter.create_market({
    'question': 'Will AI achieve AGI by 2025?',
    'outcomes': ['Yes', 'No'],
    'collateral_token': 'ELUSIV',
    'collateral_amount': 100.0
})
```

### Using npm SDK in TypeScript/JavaScript

```typescript
import { PNPClient } from 'pnp-sdk';

const client = new PNPClient({
  apiKey: process.env.PNP_API_KEY
});

const market = await client.createMarket({
  question: 'Will AI achieve AGI by 2025?',
  outcomes: ['Yes', 'No'],
  collateralToken: 'ELUSIV',
  collateralAmount: 100.0
});
```

## Current Status

### ✅ What's Ready
- Installation scripts and documentation
- Python bridge to npm SDK
- SDK adapter with multiple modes
- Backward compatibility with existing code

### ⚠️ What's Coming Soon
According to the [PNP Exchange documentation](https://docs.pnp.exchange/api-reference/introduction):
- Full API documentation
- API key generation page
- Complete SDK feature set
- Production-ready release

### 📝 Notes
- The npm package `pnp-sdk` exists but may be in beta/early stage
- API key generation is not yet available
- Some features may not be fully implemented
- The SDK is designed to work with both server apps and agent runtimes

## Architecture

```
┌─────────────────┐
│   PNPAgent      │  ← High-level agent interface
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ PNPSDKAdapter   │  ← Unified adapter (supports 3 modes)
└────────┬────────┘
         │
         ├──► Python Mock SDK (development)
         ├──► Python Real-Time SDK (WebSocket)
         └──► Node.js SDK (npm pnp-sdk) ← NEW!
              └──► PNPSDKNodeJSBridge
                   └──► Node.js subprocess
                        └──► npm pnp-sdk package
```

## Files Created/Modified

### New Files
- `pnp_sdk_nodejs_bridge.py` - Python bridge to npm SDK
- `INSTALL_PNP_SDK.md` - Installation and usage guide
- `install_pnp_sdk.sh` - Linux/Mac installation script
- `install_pnp_sdk.ps1` - Windows installation script
- `PNP_SDK_INTEGRATION_SUMMARY.md` - This file

### Modified Files
- `plugin-polymarket/package.json` - Added `pnp-sdk` dependency
- `pnp_sdk_adapter.py` - Added Node.js SDK support
- `README.md` - Added npm SDK installation instructions

## Next Steps

1. **Install the SDK:**
   ```bash
   cd plugin-polymarket
   npm install pnp-sdk
   ```

2. **Get API Key** (when available):
   - Monitor [PNP Exchange docs](https://docs.pnp.exchange)
   - Check [PNP Protocol GitHub](https://github.com/orgs/pnp-protocol/repositories)
   - Join PNP Exchange community for updates

3. **Use the SDK:**
   - Set `PNP_API_KEY` environment variable
   - Use `use_nodejs_sdk=True` in `PNPSDKAdapter`
   - See `INSTALL_PNP_SDK.md` for detailed examples

## Resources

- [PNP Exchange Documentation](https://docs.pnp.exchange)
- [PNP SDK API Reference](https://docs.pnp.exchange/api-reference/introduction)
- [PNP Protocol GitHub](https://github.com/orgs/pnp-protocol/repositories)
- [npm pnp-sdk Package](https://www.npmjs.com/package/pnp-sdk)

## Support

For issues or questions:
1. Check `INSTALL_PNP_SDK.md` for troubleshooting
2. Review the installation scripts for error messages
3. Verify Node.js and npm are properly installed
4. Check that the `pnp-sdk` package is in `package.json` dependencies


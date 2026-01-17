#!/bin/bash
# Installation script for PNP SDK npm package

echo "=========================================="
echo "PNP SDK Installation Script"
echo "=========================================="
echo ""

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed."
    echo "Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo "✅ npm found: $(npm --version)"
echo ""

# Navigate to plugin directory
PLUGIN_DIR="plugin-polymarket"

if [ ! -d "$PLUGIN_DIR" ]; then
    echo "❌ Directory $PLUGIN_DIR not found"
    exit 1
fi

echo "📦 Installing pnp-sdk package..."
cd "$PLUGIN_DIR"

# Install the package
npm install pnp-sdk

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ pnp-sdk installed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Get your API key from PNP Exchange (when available)"
    echo "2. Set PNP_API_KEY environment variable"
    echo "3. Use the SDK with: use_nodejs_sdk=True in PNPSDKAdapter"
    echo ""
    echo "See INSTALL_PNP_SDK.md for more details."
else
    echo ""
    echo "❌ Installation failed. Check the error messages above."
    exit 1
fi


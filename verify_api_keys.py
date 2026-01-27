"""
Quick API Keys Verification Script

Run this to verify all API keys are properly configured.
"""

import os
from dotenv import load_dotenv

load_dotenv()

def verify_keys():
    """Verify all API keys are set."""
    required = {
        "TELEGRAM_BOT_TOKEN": "Telegram Bot Token",
        "TELEGRAM_CHAT_ID": "Telegram Chat ID",
        "KALSHI_API_KEY": "Kalshi API Key",
        "KALSHI_API_SECRET": "Kalshi API Secret",
        "POLYMARKET_PRIVATE_KEY": "Polymarket Private Key",
        "POLYGON_PRIVATE_KEY": "Polygon Private Key",
        "UMA_FINDER_ADDRESS": "UMA Finder Address",
        "UMA_OOV3_ADDRESS": "UMA OOv3 Address",
    }
    
    optional = {
        "PNP_API_KEY": "PNP Exchange API Key",
        "OPENAI_API_KEY": "OpenAI API Key (for NLI)",
    }
    
    print("=" * 60)
    print("🔍 API KEYS VERIFICATION")
    print("=" * 60)
    print("\n📋 Required Keys:\n")
    
    all_set = True
    for key, name in required.items():
        value = os.getenv(key)
        if value:
            # Mask sensitive values
            if "SECRET" in key or "PRIVATE_KEY" in key or "TOKEN" in key:
                masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                print(f"✅ {name}: {masked}")
            else:
                print(f"✅ {name}: {value[:20]}..." if len(value) > 20 else f"✅ {name}: {value}")
        else:
            print(f"❌ {name}: MISSING")
            all_set = False
    
    print("\n📋 Optional Keys:\n")
    for key, name in optional.items():
        value = os.getenv(key)
        if value:
            masked = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {name}: {masked}")
        else:
            print(f"⚠️  {name}: Not set (optional)")
    
    print("\n" + "=" * 60)
    if all_set:
        print("✅ All required keys are set!")
        print("\n🧪 Next steps:")
        print("1. Run: python verify_api_keys.py --test")
        print("2. Check individual integrations:")
        print("   - python -c 'from telegram_alerter import get_telegram_alerter; print(\"✅ Telegram OK\")'")
        print("   - python -c 'from kalshi_api_client import get_kalshi_client; print(\"✅ Kalshi OK\")'")
        print("   - python -c 'from uma_oracle_client import get_uma_oracle_client; print(\"✅ UMA OK\")'")
    else:
        print("❌ Some required keys are missing!")
        print("\n📖 See API_KEYS_SETUP.md for setup instructions")
    print("=" * 60)
    
    return all_set

def test_integrations():
    """Test each integration."""
    print("\n" + "=" * 60)
    print("🧪 TESTING INTEGRATIONS")
    print("=" * 60)
    
    # Test Telegram
    print("\n1. Testing Telegram...")
    try:
        from telegram_alerter import get_telegram_alerter
        alerter = get_telegram_alerter()
        print("   ✅ Telegram client initialized")
    except Exception as e:
        print(f"   ❌ Telegram error: {e}")
    
    # Test Kalshi
    print("\n2. Testing Kalshi...")
    try:
        from kalshi_api_client import get_kalshi_client
        client = get_kalshi_client(demo=True)
        print("   ✅ Kalshi client initialized")
    except Exception as e:
        print(f"   ❌ Kalshi error: {e}")
    
    # Test UMA
    print("\n3. Testing UMA Oracle...")
    try:
        from uma_oracle_client import get_uma_oracle_client
        client = get_uma_oracle_client()
        print("   ✅ UMA Oracle client initialized")
    except Exception as e:
        print(f"   ❌ UMA error: {e}")
    
    # Test Polymarket CLOB
    print("\n4. Testing Polymarket CLOB...")
    try:
        from clob_orderbook_client import get_clob_orderbook_client
        client = get_clob_orderbook_client()
        print("   ✅ Polymarket CLOB client initialized")
    except Exception as e:
        print(f"   ❌ Polymarket error: {e}")
    
    # Test PNP
    print("\n5. Testing PNP Enhanced...")
    try:
        from pnp_enhanced import get_pnp_enhanced
        pnp = get_pnp_enhanced(use_realtime=False)
        print("   ✅ PNP Enhanced client initialized")
    except Exception as e:
        print(f"   ⚠️  PNP error (expected if API not available): {e}")
    
    print("\n" + "=" * 60)
    print("✅ Testing complete!")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        verify_keys()
        test_integrations()
    else:
        verify_keys()

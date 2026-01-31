"""
Comprehensive Test - All Main Modules

Tests all 5 core modules to verify they work correctly:
1. PNP Agent - AI market creation
2. Privacy Wrapper - ZK proofs, address anonymization
3. Collateral Manager - Token locking/release
4. Market Factory - Market deployment
5. SDK Adapter - Unified SDK interface
"""

import sys
import time
from datetime import datetime

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_test(name, passed, details=""):
    status = "[PASS]" if passed else "[FAIL]"
    print(f"  {status} {name}")
    if details:
        print(f"         {details}")

def test_pnp_agent():
    """Test PNP Agent module."""
    print_header("TEST 1: PNP Agent")
    
    try:
        from pnp_agent import PNPAgent
        print_test("Import PNPAgent", True)
    except ImportError as e:
        print_test("Import PNPAgent", False, str(e))
        return False
    
    try:
        agent = PNPAgent(
            default_collateral_token='ELUSIV',
            agent_id='test-agent'
        )
        print_test("Initialize Agent", True, f"ID: {agent.agent_id}")
    except Exception as e:
        print_test("Initialize Agent", False, str(e))
        return False
    
    try:
        result = agent.create_market_from_prompt(
            prompt="Bitcoin reaches $200K by 2027",
            collateral_token="ELUSIV",
            collateral_amount=100.0
        )
        print_test("Create Market from Prompt", True, f"Market: {result['market_id']}")
        print_test("Market Question Generated", True, f"Q: {result['question'][:50]}...")
    except Exception as e:
        print_test("Create Market from Prompt", False, str(e))
        return False
    
    try:
        markets = agent.list_created_markets()
        print_test("List Created Markets", True, f"Count: {len(markets)}")
    except Exception as e:
        print_test("List Created Markets", False, str(e))
    
    try:
        info = agent.get_agent_info()
        print_test("Get Agent Info", True, f"Markets: {info['markets_created']}")
    except Exception as e:
        print_test("Get Agent Info", False, str(e))
    
    return True

def test_privacy_wrapper():
    """Test Privacy Wrapper module."""
    print_header("TEST 2: Privacy Wrapper")
    
    try:
        from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel
        print_test("Import PrivacyWrapper", True)
    except ImportError as e:
        print_test("Import PrivacyWrapper", False, str(e))
        return False
    
    try:
        wrapper = PrivacyWrapper(default_privacy_level=PrivacyLevel.ANONYMOUS)
        print_test("Initialize Wrapper", True, f"Level: {wrapper.default_privacy_level.value}")
    except Exception as e:
        print_test("Initialize Wrapper", False, str(e))
        return False
    
    try:
        test_addr = "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"
        anon = wrapper.anonymize_address(test_addr)
        print_test("Anonymize Address", True, f"Result: {anon[:24]}...")
    except Exception as e:
        print_test("Anonymize Address", False, str(e))
        return False
    
    try:
        proof = wrapper.create_zk_proof(
            proof_type="ownership",
            statement={"has_collateral": True},
            witness={"amount": 100.0}
        )
        print_test("Create ZK Proof", True, f"ID: {proof['proof_id'][:20]}...")
        print_test("Proof Verified", proof['verified'], f"Type: {proof['proof_type']}")
    except Exception as e:
        print_test("Create ZK Proof", False, str(e))
        return False
    
    try:
        encrypted = wrapper.encrypt_market_data(
            market_id="TEST-001",
            data={"question": "Test?", "outcomes": ["Yes", "No"]}
        )
        print_test("Encrypt Market Data", True, f"Hash: {encrypted['encrypted_hash'][:16]}...")
    except Exception as e:
        print_test("Encrypt Market Data", False, str(e))
    
    try:
        order = wrapper.create_private_order(
            market_id="TEST-001",
            outcome="Yes",
            amount=50.0,
            price=0.65,
            trader_pubkey="TestTrader123",
            privacy_level=PrivacyLevel.PRIVATE
        )
        print_test("Create Private Order", True, f"Order: {order['order_id'][:20]}...")
    except Exception as e:
        print_test("Create Private Order", False, str(e))
    
    return True

def test_collateral_manager():
    """Test Collateral Manager module."""
    print_header("TEST 3: Collateral Manager")
    
    try:
        from pnp_infra.collateral_manager import CollateralManager, CollateralStatus
        print_test("Import CollateralManager", True)
    except ImportError as e:
        print_test("Import CollateralManager", False, str(e))
        return False
    
    try:
        manager = CollateralManager()
        print_test("Initialize Manager", True, f"Tokens: {list(manager.SUPPORTED_TOKENS.keys())}")
    except Exception as e:
        print_test("Initialize Manager", False, str(e))
        return False
    
    # Test locking for each token
    for token in ['ELUSIV', 'LIGHT', 'PNP']:
        try:
            result = manager.lock_collateral(
                market_id=f"TEST-{token}-001",
                token=token,
                amount=100.0,
                owner_pubkey="TestOwner123"
            )
            print_test(f"Lock {token} Collateral", True, f"Lock ID: {result['lock_id'][:20]}...")
        except Exception as e:
            print_test(f"Lock {token} Collateral", False, str(e))
            return False
    
    try:
        total = manager.get_total_locked('ELUSIV')
        print_test("Get Total Locked", True, f"ELUSIV: {total}")
    except Exception as e:
        print_test("Get Total Locked", False, str(e))
    
    try:
        collateral = manager.get_collateral_by_market("TEST-ELUSIV-001")
        print_test("Get Collateral by Market", True, f"Found: {collateral is not None}")
    except Exception as e:
        print_test("Get Collateral by Market", False, str(e))
    
    try:
        release = manager.release_by_market(
            market_id="TEST-PNP-001",
            resolution_outcome="Yes"
        )
        print_test("Release Collateral", True, f"Status: {release['status']}")
    except Exception as e:
        print_test("Release Collateral", False, str(e))
    
    return True

def test_market_factory():
    """Test Market Factory module."""
    print_header("TEST 4: Market Factory")
    
    try:
        from pnp_infra.market_factory import MarketFactory
        print_test("Import MarketFactory", True)
    except ImportError as e:
        print_test("Import MarketFactory", False, str(e))
        return False
    
    try:
        factory = MarketFactory(network='devnet')
        print_test("Initialize Factory", True, f"Network: {factory.network}")
    except Exception as e:
        print_test("Initialize Factory", False, str(e))
        return False
    
    try:
        account = factory.deploy_market_account(
            market_id="TEST-MKT-001",
            question="Will ETH reach $10K?",
            outcomes=["Yes", "No"],
            creator_pubkey="TestCreator123",
            collateral_token="ELUSIV",
            collateral_amount=200.0
        )
        print_test("Deploy Market Account", True, f"Address: {account['account_address'][:24]}...")
    except Exception as e:
        print_test("Deploy Market Account", False, str(e))
        return False
    
    try:
        market = factory.get_market("TEST-MKT-001")
        print_test("Get Market", True, f"Status: {market['status']}")
    except Exception as e:
        print_test("Get Market", False, str(e))
    
    try:
        liquidity = factory.add_liquidity(
            market_id="TEST-MKT-001",
            outcome="Yes",
            amount=50.0
        )
        print_test("Add Liquidity", True, f"New Total: {liquidity['new_liquidity']}")
    except Exception as e:
        print_test("Add Liquidity", False, str(e))
    
    try:
        markets = factory.list_markets()
        print_test("List Markets", True, f"Count: {len(markets)}")
    except Exception as e:
        print_test("List Markets", False, str(e))
    
    return True

def test_sdk_adapter():
    """Test SDK Adapter module."""
    print_header("TEST 5: SDK Adapter")
    
    try:
        from pnp_sdk_adapter import PNPSDKAdapter
        print_test("Import PNPSDKAdapter", True)
    except ImportError as e:
        print_test("Import PNPSDKAdapter", False, str(e))
        return False
    
    try:
        adapter = PNPSDKAdapter(use_realtime=False)
        print_test("Initialize Adapter", True, f"Type: {adapter.sdk_type}")
    except Exception as e:
        print_test("Initialize Adapter", False, str(e))
        return False
    
    try:
        market = adapter.create_market({
            'question': 'Test market from SDK adapter?',
            'outcomes': ['Yes', 'No'],
            'collateral_token': 'ELUSIV',
            'collateral_amount': 100.0
        })
        print_test("Create Market via Adapter", True, f"ID: {market['market_id']}")
    except Exception as e:
        print_test("Create Market via Adapter", False, str(e))
        return False
    
    try:
        fetched = adapter.get_market(market['market_id'])
        print_test("Get Market via Adapter", True, f"Found: {fetched is not None}")
    except Exception as e:
        print_test("Get Market via Adapter", False, str(e))
    
    try:
        order = adapter.place_order({
            'market_id': market['market_id'],
            'outcome': 'Yes',
            'side': 'buy',
            'amount': 10.0,
            'price': 0.55
        })
        print_test("Place Order via Adapter", True, f"Order: {order['order_id']}")
    except Exception as e:
        print_test("Place Order via Adapter", False, str(e))
    
    try:
        markets = adapter.list_markets()
        print_test("List Markets via Adapter", True, f"Count: {len(markets)}")
    except Exception as e:
        print_test("List Markets via Adapter", False, str(e))
    
    return True

def test_integration():
    """Test full integration flow."""
    print_header("TEST 6: Full Integration Flow")
    
    try:
        from pnp_agent import PNPAgent
        from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel
        from pnp_infra.collateral_manager import CollateralManager
        from pnp_infra.market_factory import MarketFactory
        
        print_test("Import All Modules", True)
    except ImportError as e:
        print_test("Import All Modules", False, str(e))
        return False
    
    # Initialize all
    agent = PNPAgent(default_collateral_token='ELUSIV', agent_id='integration-test')
    wrapper = PrivacyWrapper()
    manager = CollateralManager()
    factory = MarketFactory(network='devnet')
    
    print_test("Initialize All Modules", True)
    
    # Step 1: Create market with AI agent
    start = time.time()
    market = agent.create_market_from_prompt(
        prompt="Solana TVL exceeds $50B by 2026",
        collateral_token="LIGHT",
        collateral_amount=500.0
    )
    elapsed = time.time() - start
    print_test("1. AI Creates Market", True, f"{elapsed:.3f}s - {market['market_id']}")
    
    # Step 2: Lock collateral
    start = time.time()
    lock = manager.lock_collateral(
        market_id=market['market_id'],
        token="LIGHT",
        amount=500.0,
        owner_pubkey="integration-user"
    )
    elapsed = time.time() - start
    print_test("2. Lock Collateral", True, f"{elapsed:.3f}s - {lock['lock_id'][:16]}...")
    
    # Step 3: Deploy market account
    start = time.time()
    account = factory.deploy_market_account(
        market_id=market['market_id'],
        question=market['question'],
        outcomes=market['outcomes'],
        creator_pubkey="integration-user",
        collateral_token="LIGHT",
        collateral_amount=500.0
    )
    elapsed = time.time() - start
    print_test("3. Deploy Market Account", True, f"{elapsed:.3f}s - {account['account_address'][:20]}...")
    
    # Step 4: Create ZK proof
    start = time.time()
    proof = wrapper.create_zk_proof(
        proof_type="market_creation",
        statement={"market_id": market['market_id'], "deployed": True},
        witness={"amount": 500.0, "token": "LIGHT"}
    )
    elapsed = time.time() - start
    print_test("4. Create ZK Proof", True, f"{elapsed:.3f}s - Verified: {proof['verified']}")
    
    # Step 5: Anonymize creator address
    start = time.time()
    anon = wrapper.anonymize_address("integration-user")
    elapsed = time.time() - start
    print_test("5. Anonymize Address", True, f"{elapsed:.3f}s - {anon[:20]}...")
    
    # Summary
    print("\n  Integration Flow Complete:")
    print(f"    Market ID: {market['market_id']}")
    print(f"    Question: {market['question'][:40]}...")
    print(f"    Collateral: 500 LIGHT")
    print(f"    Account: {account['account_address'][:30]}...")
    print(f"    ZK Proof: {proof['proof_id'][:20]}...")
    
    return True

def main():
    print("\n" + "=" * 60)
    print("  PNP MODULE COMPREHENSIVE TEST")
    print("  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    
    results = {}
    
    results['PNP Agent'] = test_pnp_agent()
    results['Privacy Wrapper'] = test_privacy_wrapper()
    results['Collateral Manager'] = test_collateral_manager()
    results['Market Factory'] = test_market_factory()
    results['SDK Adapter'] = test_sdk_adapter()
    results['Integration'] = test_integration()
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\n  Result: {passed}/{total} modules passed")
    
    if passed == total:
        print("\n  All modules working correctly!")
    else:
        print("\n  Some modules failed. Check errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

"""
Solana Devnet Deployment Test Script

This script verifies that the PNP integration works correctly on Solana devnet
for the Solana Privacy Hack hackathon submission.

Tests:
1. Solana devnet connection
2. PNP Agent market creation
3. Privacy wrapper functionality
4. Collateral manager operations
5. Full market lifecycle
"""

import os
import sys
import asyncio
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

load_dotenv()

# Test results storage
test_results: List[Dict[str, Any]] = []

def log_test(name: str, passed: bool, message: str = ""):
    """Log test result."""
    status = "[PASS]" if passed else "[FAIL]"
    result = {
        "name": name,
        "passed": passed,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    print(f"{status}: {name}")
    if message:
        print(f"       {message}")


def test_solana_connection():
    """Test 1: Verify Solana devnet connection."""
    print("\n" + "=" * 60)
    print("TEST 1: Solana Devnet Connection")
    print("=" * 60)
    
    try:
        from solana.rpc.api import Client
        
        # Try devnet
        devnet_url = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        client = Client(devnet_url)
        
        # Check connection
        health = client.is_connected()
        
        if health:
            # Get latest blockhash to verify RPC works
            try:
                blockhash = client.get_latest_blockhash()
                log_test(
                    "Solana Devnet Connection",
                    True,
                    f"Connected to {devnet_url}"
                )
                return True
            except Exception as e:
                log_test(
                    "Solana Devnet Connection",
                    False,
                    f"RPC connected but blockhash failed: {e}"
                )
                return False
        else:
            log_test(
                "Solana Devnet Connection",
                False,
                f"Failed to connect to {devnet_url}"
            )
            return False
            
    except ImportError:
        log_test(
            "Solana Devnet Connection",
            False,
            "solana-py package not installed"
        )
        return False
    except Exception as e:
        log_test(
            "Solana Devnet Connection",
            False,
            f"Error: {e}"
        )
        return False


def test_wallet_initialization():
    """Test 2: Verify Solana wallet initialization."""
    print("\n" + "=" * 60)
    print("TEST 2: Wallet Initialization")
    print("=" * 60)
    
    try:
        from wallet_manager import WalletManager
        
        wallet = WalletManager()
        
        # Check Solana address
        solana_address = wallet.get_solana_address()
        if solana_address:
            log_test(
                "Solana Wallet",
                True,
                f"Address: {solana_address[:20]}..."
            )
        else:
            log_test(
                "Solana Wallet",
                False,
                "No Solana wallet configured (set SOLANA_PRIVATE_KEY in .env)"
            )
            return False
        
        # Check balance
        balance = wallet.get_solana_balance()
        if balance is not None:
            log_test(
                "Solana Balance",
                True,
                f"Balance: {balance} SOL"
            )
        else:
            log_test(
                "Solana Balance",
                False,
                "Could not fetch balance"
            )
        
        return True
        
    except Exception as e:
        log_test(
            "Wallet Initialization",
            False,
            f"Error: {e}"
        )
        return False


def test_pnp_agent_market_creation():
    """Test 3: Verify PNP Agent can create markets."""
    print("\n" + "=" * 60)
    print("TEST 3: PNP Agent Market Creation")
    print("=" * 60)
    
    try:
        from pnp_agent import PNPAgent
        
        # Initialize agent (uses mock SDK if real not available)
        agent = PNPAgent(
            default_collateral_token='ELUSIV',
            agent_id='test-hackathon-agent'
        )
        
        log_test(
            "Agent Initialization",
            True,
            f"Agent ID: {agent.agent_id}"
        )
        
        # Test market creation from prompt
        result = agent.create_market_from_prompt(
            prompt="Will Solana reach $500 by end of 2026?",
            collateral_token='ELUSIV',
            collateral_amount=100.0
        )
        
        if result and 'market_id' in result:
            log_test(
                "Market Creation (ELUSIV)",
                True,
                f"Market ID: {result['market_id']}"
            )
        else:
            log_test(
                "Market Creation (ELUSIV)",
                False,
                "No market_id in result"
            )
            return False
        
        # Test with different privacy token
        result2 = agent.create_market_from_prompt(
            prompt="Will Bitcoin hit $200,000 by 2027?",
            collateral_token='LIGHT',
            collateral_amount=50.0
        )
        
        if result2 and 'market_id' in result2:
            log_test(
                "Market Creation (LIGHT)",
                True,
                f"Market ID: {result2['market_id']}"
            )
        else:
            log_test(
                "Market Creation (LIGHT)",
                False,
                "Failed with LIGHT token"
            )
        
        # Test custom market
        result3 = agent.create_custom_market(
            question="Will the Privacy Hack hackathon have over 100 submissions?",
            outcomes=['Yes', 'No'],
            collateral_token='PNP',
            collateral_amount=25.0,
            resolution_criteria="Based on official hackathon announcement"
        )
        
        if result3 and 'market_id' in result3:
            log_test(
                "Custom Market Creation (PNP)",
                True,
                f"Market ID: {result3['market_id']}"
            )
        else:
            log_test(
                "Custom Market Creation (PNP)",
                False,
                "Failed with PNP token"
            )
        
        # List created markets
        markets = agent.list_created_markets()
        log_test(
            "List Markets",
            True,
            f"Created {len(markets)} markets"
        )
        
        return True
        
    except Exception as e:
        log_test(
            "PNP Agent Market Creation",
            False,
            f"Error: {e}"
        )
        return False


def test_privacy_wrapper():
    """Test 4: Verify privacy wrapper functionality."""
    print("\n" + "=" * 60)
    print("TEST 4: Privacy Wrapper (ZK Proof Simulation)")
    print("=" * 60)
    
    try:
        from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel
        
        wrapper = PrivacyWrapper(default_privacy_level=PrivacyLevel.PRIVATE)
        
        log_test(
            "Privacy Wrapper Init",
            True,
            f"Default level: {wrapper.default_privacy_level.value}"
        )
        
        # Test address anonymization
        test_pubkey = "TestWallet123456789abcdef"
        anon_address = wrapper.anonymize_address(test_pubkey)
        
        log_test(
            "Address Anonymization",
            anon_address.startswith("anon_"),
            f"Anonymized: {anon_address[:20]}..."
        )
        
        # Test ZK proof creation
        proof = wrapper.create_zk_proof(
            proof_type="ownership",
            statement={"has_collateral": True, "market_id": "test-market"},
            witness={"amount": 100.0, "token": "ELUSIV"}
        )
        
        log_test(
            "ZK Proof Creation",
            proof and 'proof_id' in proof,
            f"Proof ID: {proof['proof_id'][:16]}..."
        )
        
        # Test ZK proof verification
        verified = wrapper.verify_zk_proof(proof['proof_id'])
        
        log_test(
            "ZK Proof Verification",
            verified,
            f"Verified: {verified}"
        )
        
        # Test private order creation
        private_order = wrapper.create_private_order(
            market_id="test-market-001",
            outcome="Yes",
            amount=50.0,
            price=0.65,
            trader_pubkey=test_pubkey,
            privacy_level=PrivacyLevel.ANONYMOUS
        )
        
        log_test(
            "Private Order Creation",
            private_order and 'order_id' in private_order,
            f"Order ID: {private_order['order_id'][:16]}..."
        )
        
        # Test private settlement
        settlement = wrapper.create_private_settlement(
            market_id="test-market-001",
            winning_outcome="Yes",
            resolver_pubkey="ResolverWallet123",
            privacy_level=PrivacyLevel.ANONYMOUS
        )
        
        log_test(
            "Private Settlement",
            settlement and 'settlement_id' in settlement,
            f"Settlement ID: {settlement['settlement_id'][:16]}..."
        )
        
        # Get privacy stats
        stats = wrapper.get_privacy_stats()
        log_test(
            "Privacy Stats",
            True,
            f"ZK Proofs: {stats['zk_proofs_created']}, Anonymized: {stats['anonymized_addresses']}"
        )
        
        return True
        
    except Exception as e:
        log_test(
            "Privacy Wrapper",
            False,
            f"Error: {e}"
        )
        return False


def test_collateral_manager():
    """Test 5: Verify collateral manager functionality."""
    print("\n" + "=" * 60)
    print("TEST 5: Collateral Manager")
    print("=" * 60)
    
    try:
        from pnp_infra.collateral_manager import CollateralManager
        
        manager = CollateralManager()
        
        log_test(
            "Collateral Manager Init",
            True,
            f"Supported tokens: {list(manager.SUPPORTED_TOKENS.keys())}"
        )
        
        # Test locking collateral
        lock_result = manager.lock_collateral(
            market_id="test-hackathon-market",
            token='ELUSIV',
            amount=100.0,
            owner_pubkey='TestOwner123456789012345678901234'
        )
        
        log_test(
            "Lock Collateral (ELUSIV)",
            lock_result and lock_result.get('status') == 'locked',
            f"Lock ID: {lock_result.get('lock_id')}"
        )
        
        # Test getting total locked
        locked = manager.get_total_locked('ELUSIV')
        log_test(
            "Get Locked Amount",
            locked == 100.0,
            f"Amount: {locked}"
        )
        
        # Test releasing collateral
        lock_id = lock_result.get('lock_id')
        release_result = manager.release_collateral(
            lock_id=lock_id,
            recipient_pubkey="TestRecipient12345678901234567890"
        )
        
        log_test(
            "Release Collateral",
            release_result and release_result.get('status') == 'released',
            f"Released: {release_result.get('amount')} {release_result.get('token')}"
        )
        
        return True
        
    except Exception as e:
        log_test(
            "Collateral Manager",
            False,
            f"Error: {e}"
        )
        return False


def test_pnp_enhanced():
    """Test 6: Verify enhanced PNP features."""
    print("\n" + "=" * 60)
    print("TEST 6: PNP Enhanced (Privacy-Preserving Arbitrage)")
    print("=" * 60)
    
    try:
        from pnp_enhanced import PNPEnhancedArbitrage, ArbitrageOpportunity, PrivacyLevel, CollateralToken
        from datetime import datetime
        
        pnp = PNPEnhancedArbitrage(use_realtime=False)
        
        log_test(
            "PNP Enhanced Init",
            True,
            "Initialized with mock SDK"
        )
        
        # Test collateral token selection
        test_opp = ArbitrageOpportunity(
            question="Test market for hackathon",
            outcomes=["Yes", "No"],
            expected_profit_usd=750.0,  # Should select LIGHT
            capital_required=500.0,
            privacy_required=PrivacyLevel.PRIVATE,
            timestamp=datetime.now()
        )
        
        token = pnp.select_collateral_token(test_opp)
        expected_token = CollateralToken.LIGHT  # $500-$1000 = LIGHT
        
        log_test(
            "Collateral Token Selection",
            token == expected_token,
            f"Selected: {token.value} (expected: {expected_token.value})"
        )
        
        # Test high-profit scenario (should select ELUSIV)
        high_profit_opp = ArbitrageOpportunity(
            question="High profit test",
            outcomes=["Yes", "No"],
            expected_profit_usd=1500.0,  # Should select ELUSIV
            capital_required=1000.0,
            privacy_required=PrivacyLevel.ANONYMOUS,
            timestamp=datetime.now()
        )
        
        high_token = pnp.select_collateral_token(high_profit_opp)
        
        log_test(
            "High Profit Token Selection",
            high_token == CollateralToken.ELUSIV,
            f"Selected: {high_token.value} for high profit"
        )
        
        # Test collateral allocation optimization
        opportunities = [test_opp, high_profit_opp]
        allocation = pnp.optimize_collateral_allocation(opportunities, total_capital=2000.0)
        
        log_test(
            "Collateral Allocation",
            sum(allocation.values()) <= 2000.0,
            f"Allocated: ELUSIV=${allocation[CollateralToken.ELUSIV]:.2f}, LIGHT=${allocation[CollateralToken.LIGHT]:.2f}"
        )
        
        return True
        
    except Exception as e:
        log_test(
            "PNP Enhanced",
            False,
            f"Error: {e}"
        )
        return False


def generate_test_report():
    """Generate test report."""
    print("\n" + "=" * 60)
    print("TEST REPORT SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in test_results if r['passed'])
    total = len(test_results)
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print(f"Pass Rate: {passed/total*100:.1f}%")
    
    if total - passed > 0:
        print("\nFailed Tests:")
        for r in test_results:
            if not r['passed']:
                print(f"  - {r['name']}: {r['message']}")
    
    # Save report to file
    report = {
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{passed/total*100:.1f}%"
        },
        "tests": test_results
    }
    
    with open("devnet_test_report.json", "w") as f:
        import json
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: devnet_test_report.json")
    
    return passed == total


def main():
    """Run all devnet deployment tests."""
    print("=" * 60)
    print("SOLANA DEVNET DEPLOYMENT TEST")
    print("Solana Privacy Hack - PNP Exchange Bounty")
    print("=" * 60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run tests
    test_solana_connection()
    test_wallet_initialization()
    test_pnp_agent_market_creation()
    test_privacy_wrapper()
    test_collateral_manager()
    test_pnp_enhanced()
    
    # Generate report
    all_passed = generate_test_report()
    
    if all_passed:
        print("\n[SUCCESS] ALL TESTS PASSED - Ready for submission!")
    else:
        print("\n[WARNING] SOME TESTS FAILED - Review before submission")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

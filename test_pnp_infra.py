"""
Test script for PNP Infrastructure components.

Verifies:
- Market Factory deployment
- Collateral Manager locking/release
- Privacy Wrapper operations
"""

from pnp_infra import MarketFactory, CollateralManager, PrivacyWrapper
from pnp_infra.privacy_wrapper import PrivacyLevel


def test_market_factory():
    """Test Market Factory operations."""
    print("=" * 60)
    print("Testing Market Factory")
    print("=" * 60)
    
    factory = MarketFactory(network='devnet')
    
    # Deploy a market account
    result = factory.deploy_market_account(
        market_id='PNP-000000',
        question='Test market question',
        outcomes=['Yes', 'No'],
        creator_pubkey='TestCreator123456789012345678901234567890',
        collateral_token='ELUSIV',
        collateral_amount=100.0
    )
    
    print(f"\nDeployed account: {result['account_address']}")
    
    # Get market account
    account = factory.get_market_account('PNP-000000')
    print(f"Account status: {account['status']}")
    
    # Update state
    factory.update_market_state('PNP-000000', {'total_liquidity': 500.0})
    updated = factory.get_market_account('PNP-000000')
    print(f"Updated liquidity: {updated['total_liquidity']}")
    
    # List markets
    markets = factory.list_deployed_markets()
    print(f"\nTotal deployed markets: {len(markets)}")
    
    return True


def test_collateral_manager():
    """Test Collateral Manager operations."""
    print("\n" + "=" * 60)
    print("Testing Collateral Manager")
    print("=" * 60)
    
    manager = CollateralManager()
    
    # Lock collateral
    lock_result = manager.lock_collateral(
        market_id='PNP-000000',
        token='ELUSIV',
        amount=100.0,
        owner_pubkey='TestOwner123456789012345678901234567890',
        purpose='market_creation'
    )
    
    print(f"\nLock ID: {lock_result['lock_id']}")
    
    # Get lock
    lock = manager.get_lock(lock_result['lock_id'])
    print(f"Lock status: {lock['status']}")
    print(f"Locked amount: {lock['amount']} {lock['token']}")
    
    # Get total locked
    total = manager.get_total_locked('ELUSIV')
    print(f"\nTotal ELUSIV locked: {total}")
    
    # Partial release
    partial = manager.partial_release(
        lock_result['lock_id'],
        amount=25.0
    )
    print(f"\nPartial release: {partial['released_amount']} ELUSIV")
    print(f"Remaining: {partial['remaining_amount']} ELUSIV")
    
    # Full release
    release = manager.release_collateral(
        lock_result['lock_id'],
        release_transaction='0x1234567890abcdef'
    )
    print(f"\nReleased: {release['amount']} {release['token']}")
    
    # Transaction history
    history = manager.get_transaction_history('PNP-000000')
    print(f"\nTransaction history entries: {len(history)}")
    
    return True


def test_privacy_wrapper():
    """Test Privacy Wrapper operations."""
    print("\n" + "=" * 60)
    print("Testing Privacy Wrapper")
    print("=" * 60)
    
    wrapper = PrivacyWrapper(default_privacy_level=PrivacyLevel.PRIVATE)
    
    # Encrypt market data
    encrypted = wrapper.encrypt_market_data(
        market_id='PNP-000000',
        data={'question': 'Test', 'outcomes': ['Yes', 'No']},
        privacy_level=PrivacyLevel.PRIVATE
    )
    print(f"\nEncrypted hash: {encrypted['encrypted_hash'][:32]}...")
    
    # Anonymize address
    anonymized = wrapper.anonymize_address('TestPubkey123456789012345678901234567890')
    print(f"Anonymized address: {anonymized[:32]}...")
    
    # Create ZK proof
    proof = wrapper.create_zk_proof(
        proof_type='ownership',
        statement={'has_collateral': True},
        witness={'amount': 100.0, 'token': 'ELUSIV'}
    )
    print(f"\nZK Proof ID: {proof['proof_id'][:32]}...")
    
    # Verify proof
    verified = wrapper.verify_zk_proof(proof['proof_id'])
    print(f"Proof verified: {verified}")
    
    # Create private order
    private_order = wrapper.create_private_order(
        market_id='PNP-000000',
        outcome='Yes',
        amount=10.0,
        price=0.6,
        trader_pubkey='TestTrader123456789012345678901234567890',
        privacy_level=PrivacyLevel.ANONYMOUS
    )
    print(f"\nPrivate order ID: {private_order['order_id'][:32]}...")
    print(f"Anonymized trader: {private_order['anonymized_trader'][:32]}...")
    
    # Create private settlement
    settlement = wrapper.create_private_settlement(
        market_id='PNP-000000',
        winning_outcome='Yes',
        resolver_pubkey='TestResolver123456789012345678901234567890',
        privacy_level=PrivacyLevel.PRIVATE
    )
    print(f"\nPrivate settlement ID: {settlement['settlement_id'][:32]}...")
    
    # Privacy stats
    stats = wrapper.get_privacy_stats()
    print(f"\nPrivacy Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("PNP Infrastructure Test Suite")
    print("=" * 60)
    
    try:
        test_market_factory()
        test_collateral_manager()
        test_privacy_wrapper()
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    main()


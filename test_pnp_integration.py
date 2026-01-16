"""
Integration test demonstrating the full PNP workflow:

1. Agent creates a market from a prompt
2. Market Factory deploys the market account
3. Collateral Manager locks privacy tokens
4. Privacy Wrapper encrypts and anonymizes operations
5. Market settlement with privacy preservation
"""

from pnp_agent import PNPAgent
from pnp_infra import MarketFactory, CollateralManager, PrivacyWrapper
from pnp_infra.privacy_wrapper import PrivacyLevel


def test_full_workflow():
    """Test the complete PNP workflow."""
    print("=" * 70)
    print("PNP Full Integration Test")
    print("=" * 70)
    
    # Step 1: Initialize components
    print("\n[Step 1] Initializing components...")
    agent = PNPAgent(default_collateral_token='ELUSIV')
    factory = MarketFactory(network='devnet')
    collateral_manager = CollateralManager()
    privacy_wrapper = PrivacyWrapper(default_privacy_level=PrivacyLevel.PRIVATE)
    
    print(f"  Agent ID: {agent.agent_id}")
    print(f"  Network: {factory.network}")
    print(f"  Privacy Level: {privacy_wrapper.default_privacy_level.value}")
    
    # Step 2: Agent creates market from prompt
    print("\n[Step 2] Agent creating market from prompt...")
    headline = "Ethereum 2.0 staking reaches 50 million ETH by Q2 2024"
    market_result = agent.create_market_from_prompt(
        headline,
        collateral_token='ELUSIV',
        collateral_amount=150.0
    )
    
    market_id = market_result['market_id']
    print(f"  Market created: {market_id}")
    
    # Step 3: Deploy market account on Solana
    print("\n[Step 3] Deploying market account on Solana...")
    creator_pubkey = f"Creator_{agent.agent_id}"
    account_result = factory.deploy_market_account(
        market_id=market_id,
        question=market_result['question'],
        outcomes=market_result['outcomes'],
        creator_pubkey=creator_pubkey,
        collateral_token=market_result['collateral_token'],
        collateral_amount=market_result['collateral_amount']
    )
    print(f"  Account deployed: {account_result['account_address']}")
    
    # Step 4: Lock collateral
    print("\n[Step 4] Locking collateral...")
    lock_result = collateral_manager.lock_collateral(
        market_id=market_id,
        token=market_result['collateral_token'],
        amount=market_result['collateral_amount'],
        owner_pubkey=creator_pubkey,
        purpose='market_creation'
    )
    print(f"  Collateral locked: {lock_result['lock_id']}")
    print(f"  Amount: {market_result['collateral_amount']} {market_result['collateral_token']}")
    
    # Step 5: Encrypt market data
    print("\n[Step 5] Encrypting market data...")
    market_data = {
        'question': market_result['question'],
        'outcomes': market_result['outcomes'],
        'market_id': market_id
    }
    encrypted = privacy_wrapper.encrypt_market_data(
        market_id=market_id,
        data=market_data,
        privacy_level=PrivacyLevel.PRIVATE
    )
    print(f"  Data encrypted with hash: {encrypted['encrypted_hash'][:32]}...")
    
    # Step 6: Create private order
    print("\n[Step 6] Creating private order...")
    trader_pubkey = "Trader_123456789012345678901234567890"
    private_order = privacy_wrapper.create_private_order(
        market_id=market_id,
        outcome='Yes',
        amount=25.0,
        price=0.65,
        trader_pubkey=trader_pubkey,
        privacy_level=PrivacyLevel.ANONYMOUS
    )
    print(f"  Private order created: {private_order['order_id'][:32]}...")
    print(f"  Anonymized trader: {private_order['anonymized_trader'][:32]}...")
    
    # Step 7: Place order via SDK (simulated)
    print("\n[Step 7] Placing order via SDK...")
    from pnp_sdk_mock import get_sdk
    sdk = get_sdk()
    order_result = sdk.place_order({
        'market_id': market_id,
        'outcome': 'Yes',
        'side': 'buy',
        'amount': 25.0,
        'price': 0.65,
        'trader': private_order['anonymized_trader']
    })
    print(f"  Order placed: {order_result['order_id']}")
    print(f"  Status: {order_result['status']}")
    
    # Step 8: Create private settlement
    print("\n[Step 8] Creating private settlement...")
    resolver_pubkey = f"Resolver_{agent.agent_id}"
    settlement = privacy_wrapper.create_private_settlement(
        market_id=market_id,
        winning_outcome='Yes',
        resolver_pubkey=resolver_pubkey,
        privacy_level=PrivacyLevel.PRIVATE
    )
    print(f"  Settlement created: {settlement['settlement_id'][:32]}...")
    
    # Step 9: Settle market via SDK
    print("\n[Step 9] Settling market via SDK...")
    settle_result = sdk.settle_market(
        market_id=market_id,
        outcome='Yes',
        resolver=settlement['anonymized_resolver']
    )
    print(f"  Market settled: {settle_result['winning_outcome']}")
    
    # Step 10: Release collateral
    print("\n[Step 10] Releasing collateral...")
    release_result = collateral_manager.release_collateral(
        lock_id=lock_result['lock_id'],
        release_transaction='0x' + settlement['settlement_id'][:16]
    )
    print(f"  Collateral released: {release_result['amount']} {release_result['token']}")
    
    # Step 11: Close market account
    print("\n[Step 11] Closing market account...")
    factory.close_market_account(market_id)
    account = factory.get_market_account(market_id)
    print(f"  Account status: {account['status']}")
    
    # Summary
    print("\n" + "=" * 70)
    print("Integration Test Summary")
    print("=" * 70)
    print(f"Market ID: {market_id}")
    print(f"Market Question: {market_result['question']}")
    print(f"Collateral Token: {market_result['collateral_token']}")
    print(f"Collateral Amount: {market_result['collateral_amount']}")
    print(f"Account Address: {account_result['account_address']}")
    print(f"Privacy Level: {privacy_wrapper.default_privacy_level.value}")
    print(f"ZK Proofs Created: {privacy_wrapper.get_privacy_stats()['zk_proofs_created']}")
    print(f"Anonymized Addresses: {privacy_wrapper.get_privacy_stats()['anonymized_addresses']}")
    print("=" * 70)
    
    return True


if __name__ == "__main__":
    try:
        test_full_workflow()
        print("\n[SUCCESS] Full integration test passed!")
    except Exception as e:
        print(f"\n[ERROR] Integration test failed: {e}")
        import traceback
        traceback.print_exc()


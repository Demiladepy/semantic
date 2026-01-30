"""
Demo Script for Solana Privacy Hack Video

This script demonstrates the AI Agent creating prediction markets
with privacy-focused tokens on PNP Exchange.

Run this for the 3-minute demo video.
"""

import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(step_num, text):
    """Print step indicator."""
    print(f"\n[Step {step_num}] {text}")
    print("-" * 50)

def pause(seconds=2):
    """Pause for visual effect."""
    time.sleep(seconds)

def main():
    print_header("Solana Privacy Hack - PNP Exchange Demo")
    print(f"\nDate: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Bounty: AI Agent/Autonomous Systems Track")
    print("Project: Privacy-Preserving Prediction Market AI Agent")
    pause(3)

    # ==========================================
    # STEP 1: Initialize AI Agent
    # ==========================================
    print_step(1, "Initializing PNP AI Agent")
    
    try:
        from pnp_agent import PNPAgent
        
        agent = PNPAgent(
            default_collateral_token='ELUSIV',
            agent_id='demo-solana-privacy-hack'
        )
        
        print(f"\n  Agent ID: {agent.agent_id}")
        print(f"  Default Collateral: {agent.default_collateral_token}")
        print(f"  Supported Tokens: {list(agent.PRIVACY_TOKENS.keys())}")
        print(f"  OpenAI Available: {agent.openai_client is not None}")
        print("\n  [OK] Agent initialized successfully!")
        
    except Exception as e:
        print(f"\n  [ERROR] {e}")
        return
    
    pause(2)

    # ==========================================
    # STEP 2: Show Privacy Token Options
    # ==========================================
    print_step(2, "Privacy Token Collateral Options")
    
    print("\n  Available Privacy Tokens:")
    print("  -------------------------")
    for token, info in agent.PRIVACY_TOKENS.items():
        print(f"\n  [{token}]")
        print(f"    Name: {info['name']}")
        print(f"    Description: {info['description']}")
        print(f"    Default Amount: {info['default_amount']}")
    
    pause(3)

    # ==========================================
    # STEP 3: AI Generates Market from Prompt
    # ==========================================
    print_step(3, "AI Agent Creates Market from Prompt")
    
    news_headline = "Solana breaks $200 by March 2026"
    
    print(f"\n  Input Prompt: \"{news_headline}\"")
    print("\n  Processing...")
    pause(2)
    
    result1 = agent.create_market_from_prompt(
        prompt=news_headline,
        collateral_token='ELUSIV',
        collateral_amount=100.0
    )
    
    print(f"\n  Market Created!")
    print(f"  Market ID: {result1['market_id']}")
    print(f"  Question: {result1['question']}")
    print(f"  Collateral: {result1['collateral_amount']} {result1['collateral_token']}")
    
    pause(3)

    # ==========================================
    # STEP 4: Privacy Wrapper Demonstration
    # ==========================================
    print_step(4, "Privacy Wrapper - ZK Proof Simulation")
    
    try:
        from pnp_infra.privacy_wrapper import PrivacyWrapper, PrivacyLevel
        
        wrapper = PrivacyWrapper(default_privacy_level=PrivacyLevel.ANONYMOUS)
        
        # Anonymize address
        test_pubkey = "TestWalletPubKey123456789abcdef"
        anon_address = wrapper.anonymize_address(test_pubkey)
        
        print(f"\n  Original Address: {test_pubkey[:20]}...")
        print(f"  Anonymized:       {anon_address[:20]}...")
        
        # Create ZK proof
        print("\n  Creating ZK Proof for ownership...")
        proof = wrapper.create_zk_proof(
            proof_type="ownership",
            statement={"has_collateral": True, "market_id": result1['market_id']},
            witness={"amount": 100.0, "token": "ELUSIV"}
        )
        
        print(f"  Proof ID: {proof['proof_id'][:20]}...")
        print(f"  Proof Type: {proof['proof_type']}")
        print(f"  Verified: {proof['verified']}")
        
        # Create private order
        print("\n  Creating Private Order...")
        private_order = wrapper.create_private_order(
            market_id=result1['market_id'],
            outcome="Yes",
            amount=50.0,
            price=0.65,
            trader_pubkey=test_pubkey,
            privacy_level=PrivacyLevel.ANONYMOUS
        )
        
        print(f"  Order ID: {private_order['order_id'][:20]}...")
        print(f"  Privacy Level: {private_order['privacy_level']}")
        
    except Exception as e:
        print(f"\n  [ERROR] {e}")
    
    pause(3)

    # ==========================================
    # STEP 5: Collateral Manager Demo
    # ==========================================
    print_step(5, "Collateral Management")
    
    try:
        from pnp_infra.collateral_manager import CollateralManager
        
        manager = CollateralManager()
        
        # Lock collateral
        print("\n  Locking collateral for market...")
        lock_result = manager.lock_collateral(
            market_id=result1['market_id'],
            token='ELUSIV',
            amount=100.0,
            owner_pubkey='DemoOwnerPubKey123456789012345678'
        )
        
        print(f"  Lock ID: {lock_result['lock_id'][:40]}...")
        print(f"  Status: {lock_result['status']}")
        
        # Show total locked
        total_locked = manager.get_total_locked('ELUSIV')
        print(f"\n  Total ELUSIV Locked: {total_locked}")
        
    except Exception as e:
        print(f"\n  [ERROR] {e}")
    
    pause(3)

    # ==========================================
    # STEP 6: Create Multiple Markets with Different Tokens
    # ==========================================
    print_step(6, "Creating Markets with Different Privacy Tokens")
    
    markets_to_create = [
        ("Bitcoin ETF approval by SEC in Q1 2026", "LIGHT", 75.0),
        ("Ethereum reaches $5000 by end of 2026", "PNP", 50.0),
    ]
    
    for prompt, token, amount in markets_to_create:
        print(f"\n  Creating market with {token}...")
        print(f"  Prompt: \"{prompt}\"")
        
        result = agent.create_market_from_prompt(
            prompt=prompt,
            collateral_token=token,
            collateral_amount=amount
        )
        
        print(f"  Market ID: {result['market_id']}")
        print(f"  Collateral: {amount} {token}")
        pause(1)
    
    pause(2)

    # ==========================================
    # STEP 7: List All Created Markets
    # ==========================================
    print_step(7, "Summary - All Markets Created")
    
    all_markets = agent.list_created_markets()
    
    print(f"\n  Total Markets Created: {len(all_markets)}")
    print("\n  Markets:")
    print("  " + "-" * 55)
    
    for i, market in enumerate(all_markets, 1):
        print(f"\n  {i}. {market['question']}")
        print(f"     ID: {market['market_id']}")
        print(f"     Collateral: {market['collateral_amount']} {market['collateral_token']}")
        print(f"     Status: {market['status']}")
    
    pause(3)

    # ==========================================
    # STEP 8: Agent Info
    # ==========================================
    print_step(8, "Agent Statistics")
    
    info = agent.get_agent_info()
    
    print(f"\n  Agent ID: {info['agent_id']}")
    print(f"  Default Token: {info['default_collateral_token']}")
    print(f"  Markets Created: {info['markets_created']}")
    print(f"  OpenAI Available: {info['openai_available']}")
    print(f"  Supported Tokens: {', '.join(info['supported_tokens'])}")
    
    pause(2)

    # ==========================================
    # CONCLUSION
    # ==========================================
    print_header("Demo Complete!")
    
    print("""
    Summary:
    --------
    - AI Agent autonomously created prediction markets from prompts
    - Used privacy-focused tokens (ELUSIV, LIGHT, PNP) as collateral
    - Demonstrated ZK proof framework for privacy
    - Showed address anonymization and private order creation
    - All operations work on Solana devnet/mainnet
    
    Key Technologies:
    -----------------
    - PNP Exchange SDK (Solana)
    - OpenAI GPT for market question generation
    - Privacy token integration (ELUSIV, LIGHT)
    - Zero-knowledge proof simulation framework
    
    Submission:
    -----------
    Solana Privacy Hack - PNP Exchange Bounty
    AI Agent/Autonomous Systems Track
    
    Thank you for watching!
    """)

if __name__ == "__main__":
    main()

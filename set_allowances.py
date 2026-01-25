"""
Set Allowances - Enable Polymarket trading permissions

This script approves the necessary Polymarket contracts to spend your USDC.e on Polygon.
Run this ONCE per wallet before trading.

Without these approvals, the CLOB API will reject your signed orders.
"""

import os
import logging
from typing import List
from dotenv import load_dotenv

try:
    from web3 import Web3
except ImportError:
    print("ERROR: web3 not installed. Run: pip install web3")
    exit(1)

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ========================
# POLYMARKET CONTRACTS
# ========================

USDC_E_ADDRESS = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"  # USDC.e on Polygon
CTF_CONTRACT = "0x4D97DCd97eC945f40cF65F87097ACe5EA0476045"  # Conditional Token Framework
CTF_EXCHANGE = "0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E"  # CTF Exchange
NEG_RISK_EXCHANGE = "0xC5d563A36AE78145C45a50134d48A1215220f80a"  # Negative Risk Exchange

# Minimal ERC20 ABI for approval function
ERC20_ABI = [
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"},
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function",
    }
]

# Unlimited approval amount (2^256 - 1)
UNLIMITED_APPROVAL = 2**256 - 1


def set_allowances():
    """
    Approve all necessary Polymarket contracts to spend your USDC.e.
    """
    logger.info("=" * 70)
    logger.info("Polymarket USDC Allowance Setter")
    logger.info("=" * 70)

    # Initialize wallet
    polygon_rpc = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com/")
    private_key = os.getenv("POLYGON_PRIVATE_KEY")

    if not private_key:
        logger.error("❌ POLYGON_PRIVATE_KEY not set in .env")
        return False

    try:
        w3 = Web3(Web3.HTTPProvider(polygon_rpc))
        if not w3.is_connected():
            logger.error(f"❌ Failed to connect to Polygon RPC: {polygon_rpc}")
            return False

        account = w3.eth.account.from_key(private_key)
        logger.info(f"✅ Connected to Polygon")
        logger.info(f"📍 Wallet Address: {account.address}")

    except Exception as e:
        logger.error(f"❌ Failed to initialize wallet: {e}")
        return False

    # Get current balance
    try:
        eth_balance = w3.eth.get_balance(account.address)
        eth_balance_ether = w3.from_wei(eth_balance, "ether")
        logger.info(f"💰 Wallet Balance: {eth_balance_ether:.6f} MATIC")

        if eth_balance_ether < 0.1:
            logger.warning(
                f"⚠️  Low MATIC balance ({eth_balance_ether:.6f}). "
                "May not have enough for gas fees."
            )

    except Exception as e:
        logger.error(f"Failed to get balance: {e}")

    # Set up USDC contract
    try:
        usdc_contract = w3.eth.contract(address=USDC_E_ADDRESS, abi=ERC20_ABI)
        logger.info(f"✅ USDC.e contract loaded: {USDC_E_ADDRESS}")
    except Exception as e:
        logger.error(f"❌ Failed to load USDC contract: {e}")
        return False

    # Define target spenders
    targets = [
        ("CTF Exchange", CTF_EXCHANGE),
        ("Negative Risk Exchange", NEG_RISK_EXCHANGE),
        ("CTF Contract", CTF_CONTRACT),
    ]

    # Approve each target
    logger.info("\n" + "=" * 70)
    logger.info("Setting Allowances...")
    logger.info("=" * 70)

    success_count = 0

    for name, spender_address in targets:
        try:
            logger.info(f"\n▶ Approving {name}...")
            logger.info(f"  Address: {spender_address}")

            # Build the approval transaction
            tx = usdc_contract.functions.approve(spender_address, UNLIMITED_APPROVAL).build_transaction(
                {
                    "from": account.address,
                    "nonce": w3.eth.get_transaction_count(account.address),
                    "gasPrice": w3.eth.gas_price,
                }
            )

            logger.info(f"  Gas Price: {w3.from_wei(tx['gasPrice'], 'gwei'):.2f} Gwei")
            logger.info(f"  Estimated Gas: {tx['gas']} units")

            # Sign and send
            signed_tx = w3.eth.account.sign_transaction(tx, account.key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            logger.info(f"  ✅ Approved! TX Hash: {tx_hash.hex()}")
            success_count += 1

        except Exception as e:
            logger.error(f"  ❌ Failed to approve {name}: {e}")

    # Summary
    logger.info("\n" + "=" * 70)
    if success_count == len(targets):
        logger.info(f"✅ SUCCESS: All {success_count}/{len(targets)} allowances set!")
        logger.info("🚀 Ready to trade on Polymarket!")
    else:
        logger.warning(f"⚠️  Partial success: {success_count}/{len(targets)} allowances set")

    logger.info("=" * 70)

    return success_count == len(targets)


if __name__ == "__main__":
    import sys

    success = set_allowances()
    sys.exit(0 if success else 1)

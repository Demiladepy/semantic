"""
Wallet Manager - Secure key management and transaction signing for Polygon (Polymarket) and Solana (PNP)

This module handles:
- Secure storage of private keys (from .env)
- Polygon/Ethereum transaction signing (for Polymarket)
- Solana transaction signing (for PNP Exchange)
- Balance checks and gas estimation
"""

import os
import logging
from typing import Optional, Dict, Any
from dotenv import load_dotenv

try:
    from web3 import Web3
    from eth_account.signers.local import LocalAccount
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logging.warning("web3 not installed. Polygon functionality disabled.")

try:
    from solana.rpc.api import Client
    from solders.keypair import Keypair
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    logging.warning("solana not installed. Solana functionality disabled.")

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WalletManager:
    """
    Unified wallet manager for Polygon (Polymarket) and Solana (PNP Exchange).
    """

    def __init__(self):
        """Initialize wallet connections for both chains."""
        self.polygon_account: Optional[LocalAccount] = None
        self.solana_keypair: Optional[Keypair] = None
        self.w3_polygon: Optional[Web3] = None
        self.solana_client: Optional[Client] = None

        self._init_polygon()
        self._init_solana()

    def _init_polygon(self):
        """Initialize Polygon/Ethereum wallet."""
        if not WEB3_AVAILABLE:
            logger.warning("Web3 not available. Polygon wallet skipped.")
            return

        polygon_rpc = os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com/")
        private_key = os.getenv("POLYGON_PRIVATE_KEY")

        if not private_key:
            logger.warning("POLYGON_PRIVATE_KEY not set. Polygon operations will fail.")
            return

        try:
            self.w3_polygon = Web3(Web3.HTTPProvider(polygon_rpc))
            self.polygon_account = self.w3_polygon.eth.account.from_key(private_key)
            logger.info(f"✅ Polygon wallet initialized: {self.polygon_account.address}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Polygon wallet: {e}")

    def _init_solana(self):
        """Initialize Solana wallet."""
        if not SOLANA_AVAILABLE:
            logger.warning("Solana libraries not available. Solana wallet skipped.")
            return

        solana_rpc = os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        private_key_str = os.getenv("SOLANA_PRIVATE_KEY")

        if not private_key_str:
            logger.warning("SOLANA_PRIVATE_KEY not set. Solana operations will fail.")
            return

        try:
            self.solana_client = Client(solana_rpc)
            self.solana_keypair = Keypair.from_base58_string(private_key_str)
            logger.info(f"✅ Solana wallet initialized: {self.solana_keypair.pubkey()}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Solana wallet: {e}")

    # ========================
    # POLYGON (POLYMARKET) METHODS
    # ========================

    def get_polygon_address(self) -> Optional[str]:
        """Get Polygon wallet address."""
        return self.polygon_account.address if self.polygon_account else None

    def get_polygon_balance(self, token_address: Optional[str] = None) -> float:
        """
        Get ETH or ERC20 token balance on Polygon.

        Args:
            token_address: If None, returns ETH balance. Otherwise, ERC20 token balance.

        Returns:
            Balance in token units (converted from Wei).
        """
        if not self.w3_polygon or not self.polygon_account:
            logger.error("Polygon wallet not initialized")
            return 0.0

        try:
            if token_address is None:
                # Get ETH balance
                balance_wei = self.w3_polygon.eth.get_balance(self.polygon_account.address)
                return self.w3_polygon.from_wei(balance_wei, "ether")
            else:
                # Get ERC20 balance
                abi = [
                    {
                        "constant": True,
                        "inputs": [{"name": "_owner", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "balance", "type": "uint256"}],
                        "type": "function",
                    }
                ]
                contract = self.w3_polygon.eth.contract(address=token_address, abi=abi)
                balance = contract.functions.balanceOf(self.polygon_account.address).call()
                # Assuming 18 decimals (USDC.e has 6, adjust if needed)
                return balance / 1e18
        except Exception as e:
            logger.error(f"Failed to get Polygon balance: {e}")
            return 0.0

    def get_polygon_gas_price(self) -> Dict[str, Any]:
        """Get current Polygon gas price."""
        if not self.w3_polygon:
            return {}

        try:
            gas_price_wei = self.w3_polygon.eth.gas_price
            gas_price_gwei = self.w3_polygon.from_wei(gas_price_wei, "gwei")
            return {
                "gas_price_wei": gas_price_wei,
                "gas_price_gwei": gas_price_gwei,
            }
        except Exception as e:
            logger.error(f"Failed to get gas price: {e}")
            return {}

    def sign_polygon_tx(self, tx: Dict[str, Any]) -> str:
        """
        Sign and submit a transaction on Polygon.

        Args:
            tx: Transaction dictionary with fields: to, data, value, gas, gasPrice, nonce, etc.

        Returns:
            Transaction hash as hex string.
        """
        if not self.w3_polygon or not self.polygon_account:
            logger.error("Polygon wallet not initialized")
            return ""

        try:
            # Add default nonce if not provided
            if "nonce" not in tx:
                tx["nonce"] = self.w3_polygon.eth.get_transaction_count(
                    self.polygon_account.address
                )

            # Add default gas price if not provided
            if "gasPrice" not in tx:
                tx["gasPrice"] = self.w3_polygon.eth.gas_price

            # Sign the transaction
            signed_tx = self.w3_polygon.eth.account.sign_transaction(tx, self.polygon_account.key)

            # Send the transaction
            tx_hash = self.w3_polygon.eth.send_raw_transaction(signed_tx.rawTransaction)
            logger.info(f"✅ Transaction submitted: {tx_hash.hex()}")
            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Failed to sign/submit transaction: {e}")
            return ""

    # ========================
    # SOLANA METHODS
    # ========================

    def get_solana_address(self) -> Optional[str]:
        """Get Solana wallet address (public key)."""
        return str(self.solana_keypair.pubkey()) if self.solana_keypair else None

    def get_solana_balance(self) -> float:
        """Get SOL balance on Solana."""
        if not self.solana_client or not self.solana_keypair:
            logger.error("Solana wallet not initialized")
            return 0.0

        try:
            balance = self.solana_client.get_balance(self.solana_keypair.pubkey())
            return balance["result"]["value"] / 1e9  # Convert lamports to SOL
        except Exception as e:
            logger.error(f"Failed to get Solana balance: {e}")
            return 0.0

    def get_solana_keypair(self) -> Optional[Keypair]:
        """Get the Solana keypair object."""
        return self.solana_keypair


# ========================
# UTILITY FUNCTIONS
# ========================


def get_wallet_manager() -> WalletManager:
    """Factory function to get a WalletManager instance."""
    return WalletManager()


if __name__ == "__main__":
    # Test the wallet manager
    wallet = WalletManager()

    print("=" * 60)
    print("Wallet Manager Test")
    print("=" * 60)

    # Polygon
    polygon_addr = wallet.get_polygon_address()
    if polygon_addr:
        print(f"\n📍 Polygon Address: {polygon_addr}")
        eth_balance = wallet.get_polygon_balance()
        print(f"   ETH Balance: {eth_balance:.6f}")
        gas_info = wallet.get_polygon_gas_price()
        if gas_info:
            print(f"   Gas Price: {gas_info.get('gas_price_gwei', 0):.2f} Gwei")

    # Solana
    solana_addr = wallet.get_solana_address()
    if solana_addr:
        print(f"\n📍 Solana Address: {solana_addr}")
        sol_balance = wallet.get_solana_balance()
        print(f"   SOL Balance: {sol_balance:.6f}")

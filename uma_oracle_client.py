"""
UMA Optimistic Oracle Integration

Monitors UMA OOv3 for market resolution tracking, dispute detection,
and settlement alerts for cross-platform arbitrage.
"""

import os
import logging
import json
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logging.warning("web3 not installed - UMA features disabled")

from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AssertionStatus(Enum):
    """Assertion status."""
    PENDING = "pending"
    RESOLVED = "resolved"
    DISPUTED = "disputed"
    EXPIRED = "expired"
    SETTLED = "settled"


@dataclass
class AssertionInfo:
    """UMA assertion information."""
    assertion_id: str
    market_id: str
    resolved: bool
    resolved_value: Optional[bool]
    expiration_time: int
    settled: bool
    asserter: str
    dispute_bond: Optional[int]
    status: AssertionStatus
    timestamp: float


class UMAOracleClient:
    """
    UMA Optimistic Oracle V3 client for monitoring market resolutions.
    
    Features:
    - Assertion status monitoring
    - Dispute detection
    - Settlement tracking
    - Real-time event listening
    """

    def __init__(
        self,
        rpc_url: Optional[str] = None,
        finder_address: Optional[str] = None,
        oov3_address: Optional[str] = None,
    ):
        """
        Initialize UMA Oracle client.
        
        Args:
            rpc_url: Polygon RPC URL
            finder_address: UMA Finder contract address
            oov3_address: OptimisticOracleV3 contract address
        """
        if not WEB3_AVAILABLE:
            raise ImportError("web3 package required for UMA integration")

        self.rpc_url = rpc_url or os.getenv("POLYGON_RPC_URL", "https://polygon-rpc.com")
        self.finder_address = finder_address or os.getenv("UMA_FINDER_ADDRESS")
        self.oov3_address = oov3_address or os.getenv("UMA_OOV3_ADDRESS")

        self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        
        # Add PoA middleware for Polygon
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"Failed to connect to RPC: {self.rpc_url}")

        # Load contract ABIs
        self.finder_abi = self._load_finder_abi()
        self.oov3_abi = self._load_oov3_abi()

        # Initialize contracts
        if self.finder_address:
            self.finder_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.finder_address),
                abi=self.finder_abi
            )
            logger.info(f"✅ Finder contract initialized: {self.finder_address}")

        if self.oov3_address:
            self.oov3_contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.oov3_address),
                abi=self.oov3_abi
            )
            logger.info(f"✅ OOv3 contract initialized: {self.oov3_address}")

        self.event_listeners: List[Callable] = []
        logger.info("✅ UMA Oracle Client initialized")

    def _load_finder_abi(self) -> List[Dict]:
        """Load Finder contract ABI."""
        # Minimal ABI for getImplementationAddress
        return [
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "interfaceName", "type": "bytes32"}
                ],
                "name": "getImplementationAddress",
                "outputs": [
                    {"internalType": "address", "name": "", "type": "address"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def _load_oov3_abi(self) -> List[Dict]:
        """Load OptimisticOracleV3 contract ABI."""
        # Key functions for monitoring
        return [
            {
                "inputs": [
                    {"internalType": "bytes32", "name": "assertionId", "type": "bytes32"}
                ],
                "name": "getAssertion",
                "outputs": [
                    {"internalType": "bool", "name": "resolved", "type": "bool"},
                    {"internalType": "bool", "name": "resolvedValue", "type": "bool"},
                    {"internalType": "uint256", "name": "expirationTime", "type": "uint256"},
                    {"internalType": "bool", "name": "settled", "type": "bool"},
                    {"internalType": "address", "name": "asserter", "type": "address"},
                    {"internalType": "uint256", "name": "disputeBond", "type": "uint256"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "assertionId", "type": "bytes32"},
                    {"indexed": False, "name": "resolvedTruthfully", "type": "bool"}
                ],
                "name": "AssertionResolved",
                "type": "event"
            },
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "name": "assertionId", "type": "bytes32"},
                    {"indexed": False, "name": "disputer", "type": "address"}
                ],
                "name": "AssertionDisputed",
                "type": "event"
            }
        ]

    def get_assertion_status(self, assertion_id: str) -> Optional[AssertionInfo]:
        """
        Get status of a market resolution assertion.
        
        Args:
            assertion_id: UMA assertion ID (bytes32)
            
        Returns:
            AssertionInfo or None if not found
        """
        if not self.oov3_contract:
            logger.error("OOv3 contract not initialized")
            return None

        try:
            # Convert assertion_id to bytes32 if needed
            if isinstance(assertion_id, str) and assertion_id.startswith("0x"):
                assertion_bytes = bytes.fromhex(assertion_id[2:])
            else:
                assertion_bytes = Web3.keccak(text=assertion_id)

            result = self.oov3_contract.functions.getAssertion(assertion_bytes).call()

            resolved, resolved_value, expiration_time, settled, asserter, dispute_bond = result

            # Determine status
            if settled:
                status = AssertionStatus.SETTLED
            elif resolved:
                status = AssertionStatus.RESOLVED
            elif dispute_bond > 0:
                status = AssertionStatus.DISPUTED
            elif time.time() > expiration_time:
                status = AssertionStatus.EXPIRED
            else:
                status = AssertionStatus.PENDING

            return AssertionInfo(
                assertion_id=assertion_id,
                market_id=assertion_id,  # Map to your market ID
                resolved=resolved,
                resolved_value=bool(resolved_value) if resolved else None,
                expiration_time=expiration_time,
                settled=settled,
                asserter=asserter,
                dispute_bond=dispute_bond,
                status=status,
                timestamp=time.time(),
            )

        except Exception as e:
            logger.error(f"Error fetching assertion status: {e}")
            return None

    def monitor_resolutions(
        self,
        market_ids: List[str],
        callback: Optional[Callable[[AssertionInfo], None]] = None,
    ) -> Dict[str, AssertionInfo]:
        """
        Monitor multiple markets for resolution.
        
        Args:
            market_ids: List of market/assertion IDs
            callback: Optional callback function when resolution detected
            
        Returns:
            Dict mapping market_id to AssertionInfo
        """
        resolutions = {}

        for market_id in market_ids:
            assertion_info = self.get_assertion_status(market_id)

            if assertion_info:
                if assertion_info.resolved and assertion_info not in resolutions.values():
                    resolutions[market_id] = assertion_info

                    if callback:
                        callback(assertion_info)

                    logger.info(
                        f"✅ Market {market_id} resolved: "
                        f"{assertion_info.resolved_value} "
                        f"(Status: {assertion_info.status.value})"
                    )

        return resolutions

    def monitor_assertion_events(
        self,
        from_block: int = 0,
        callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        Listen for AssertionResolved and AssertionDisputed events.
        
        Args:
            from_block: Block number to start from (0 = latest)
            callback: Callback function for events
        """
        if not self.oov3_contract:
            logger.error("OOv3 contract not initialized")
            return

        try:
            # Get latest block if from_block is 0
            if from_block == 0:
                from_block = self.w3.eth.block_number - 1000  # Last 1000 blocks

            # Create event filters
            resolved_filter = self.oov3_contract.events.AssertionResolved.create_filter(
                fromBlock=from_block
            )
            disputed_filter = self.oov3_contract.events.AssertionDisputed.create_filter(
                fromBlock=from_block
            )

            logger.info(f"🔍 Monitoring UMA events from block {from_block}")

            while True:
                # Check for resolved assertions
                for event in resolved_filter.get_new_entries():
                    assertion_id = event['args']['assertionId'].hex()
                    resolved_truthfully = event['args']['resolvedTruthfully']

                    event_data = {
                        'type': 'resolved',
                        'assertion_id': assertion_id,
                        'resolved_truthfully': resolved_truthfully,
                        'block_number': event['blockNumber'],
                        'transaction_hash': event['transactionHash'].hex(),
                    }

                    logger.info(
                        f"🚨 Assertion Resolved: {assertion_id} "
                        f"(Truthful: {resolved_truthfully})"
                    )

                    if callback:
                        callback(event_data)

                    # Get full assertion info
                    assertion_info = self.get_assertion_status(assertion_id)
                    if assertion_info:
                        self.handle_resolution(assertion_info)

                # Check for disputes
                for event in disputed_filter.get_new_entries():
                    assertion_id = event['args']['assertionId'].hex()
                    disputer = event['args']['disputer']

                    event_data = {
                        'type': 'disputed',
                        'assertion_id': assertion_id,
                        'disputer': disputer,
                        'block_number': event['blockNumber'],
                        'transaction_hash': event['transactionHash'].hex(),
                    }

                    logger.warning(
                        f"⚠️ Assertion Disputed: {assertion_id} by {disputer}"
                    )

                    if callback:
                        callback(event_data)

                time.sleep(10)  # Poll every 10 seconds

        except KeyboardInterrupt:
            logger.info("Event monitoring stopped")
        except Exception as e:
            logger.error(f"Error monitoring events: {e}")

    def handle_resolution(self, assertion_info: AssertionInfo):
        """
        Handle market resolution (override for custom logic).
        
        Args:
            assertion_info: Assertion information
        """
        logger.info(
            f"📊 Handling resolution for {assertion_info.market_id}: "
            f"{assertion_info.resolved_value}"
        )

        # Trigger settlement in your system
        # This should integrate with your market settlement logic
        self.trigger_settlement(assertion_info)

    def trigger_settlement(self, assertion_info: AssertionInfo):
        """
        Trigger settlement for resolved market.
        
        Args:
            assertion_info: Assertion information
        """
        logger.info(
            f"💰 Triggering settlement for market {assertion_info.market_id} "
            f"(Value: {assertion_info.resolved_value})"
        )

        # Implement your settlement logic here
        # This should:
        # 1. Update market status in your database
        # 2. Distribute payouts
        # 3. Update position tracking
        # 4. Send notifications

    def check_settlement_discrepancy(
        self,
        market_id: str,
        polymarket_resolution: bool,
        kalshi_resolution: Optional[bool] = None,
    ) -> bool:
        """
        Check for settlement discrepancies between platforms.
        
        Args:
            market_id: Market identifier
            polymarket_resolution: Resolution on Polymarket
            kalshi_resolution: Resolution on Kalshi (if applicable)
            
        Returns:
            True if discrepancy detected
        """
        assertion_info = self.get_assertion_status(market_id)

        if not assertion_info or not assertion_info.resolved:
            return False

        uma_resolution = assertion_info.resolved_value

        # Check discrepancy with Polymarket
        if uma_resolution != polymarket_resolution:
            logger.warning(
                f"⚠️ Settlement discrepancy detected for {market_id}: "
                f"UMA={uma_resolution}, Polymarket={polymarket_resolution}"
            )
            return True

        # Check discrepancy with Kalshi if provided
        if kalshi_resolution is not None and uma_resolution != kalshi_resolution:
            logger.warning(
                f"⚠️ Settlement discrepancy detected for {market_id}: "
                f"UMA={uma_resolution}, Kalshi={kalshi_resolution}"
            )
            return True

        return False

    def auto_claim_resolved_markets(
        self,
        market_ids: List[str],
        private_key: Optional[str] = None,
    ) -> List[str]:
        """
        Auto-claim resolved markets (requires wallet with private key).
        
        Args:
            market_ids: List of market IDs to claim
            private_key: Private key for claiming (optional)
            
        Returns:
            List of successfully claimed market IDs
        """
        if not private_key:
            private_key = os.getenv("POLYGON_PRIVATE_KEY")

        if not private_key:
            logger.error("Private key required for auto-claiming")
            return []

        from eth_account import Account
        account = Account.from_key(private_key)

        claimed = []

        for market_id in market_ids:
            assertion_info = self.get_assertion_status(market_id)

            if assertion_info and assertion_info.resolved and not assertion_info.settled:
                try:
                    # Implement claim logic here
                    # This would call the settlement function on the market contract
                    logger.info(f"💰 Auto-claiming market {market_id}")
                    claimed.append(market_id)
                except Exception as e:
                    logger.error(f"Error claiming market {market_id}: {e}")

        return claimed


# ========================
# UTILITY FUNCTIONS
# ========================

def get_uma_oracle_client(
    rpc_url: Optional[str] = None,
    finder_address: Optional[str] = None,
    oov3_address: Optional[str] = None,
) -> UMAOracleClient:
    """Factory function for UMAOracleClient."""
    return UMAOracleClient(
        rpc_url=rpc_url,
        finder_address=finder_address,
        oov3_address=oov3_address,
    )


if __name__ == "__main__":
    # Test UMA oracle client
    try:
        client = get_uma_oracle_client()
        print("✅ UMA Oracle Client initialized")
        
        # Example: Monitor a specific assertion
        # assertion_id = "0x..."  # Replace with actual assertion ID
        # status = client.get_assertion_status(assertion_id)
        # if status:
        #     print(f"Status: {status.status.value}")
        #     print(f"Resolved: {status.resolved}")
        #     print(f"Value: {status.resolved_value}")
    except Exception as e:
        print(f"Error: {e}")

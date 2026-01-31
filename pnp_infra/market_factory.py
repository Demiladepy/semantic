"""
Market Factory

Logic for deploying market contracts/accounts on Solana.
Simulates the creation and management of prediction market accounts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json


class MarketFactory:
    """
    Factory for creating and managing prediction market accounts on Solana.
    
    This class simulates the deployment of market contracts/accounts,
    including account initialization, state management, and lifecycle operations.
    """
    
    def __init__(self, network: str = 'mainnet-beta'):
        """
        Initialize the Market Factory.
        
        Args:
            network: Solana network ('mainnet-beta', 'devnet', 'testnet')
        """
        self.network = network
        self.deployed_markets: Dict[str, Dict[str, Any]] = {}
        self.account_counter = 0
    
    def deploy_market_account(self,
                             market_id: str,
                             question: str,
                             outcomes: List[str],
                             creator_pubkey: str,
                             collateral_token: str,
                             collateral_amount: float) -> Dict[str, Any]:
        """
        Deploy a new market account on Solana.
        
        Args:
            market_id: Unique market identifier
            question: Market question
            outcomes: List of possible outcomes
            creator_pubkey: Public key of the market creator
            collateral_token: Privacy token symbol
            collateral_amount: Amount of collateral to lock
        
        Returns:
            Dictionary with account deployment details:
                - account_address: str - Solana account address
                - market_id: str
                - deployed_at: str - ISO timestamp
                - network: str
        """
        # Generate a simulated Solana account address
        # In real implementation, this would be a Program Derived Address (PDA)
        account_address = self._generate_account_address(market_id, creator_pubkey)
        
        account_data = {
            'account_address': account_address,
            'market_id': market_id,
            'question': question,
            'outcomes': outcomes,
            'creator_pubkey': creator_pubkey,
            'collateral_token': collateral_token,
            'collateral_amount': collateral_amount,
            'network': self.network,
            'deployed_at': datetime.utcnow().isoformat(),
            'status': 'active',
            'total_liquidity': 0.0,
            'outcome_liquidity': {outcome: 0.0 for outcome in outcomes}
        }
        
        self.deployed_markets[market_id] = account_data
        self.account_counter += 1
        
        print(f"[Market Factory] Market account deployed on {self.network}")
        print(f"  Account Address: {account_address}")
        print(f"  Market ID: {market_id}")
        print(f"  Creator: {creator_pubkey[:8]}...{creator_pubkey[-8:]}")
        
        return {
            'account_address': account_address,
            'market_id': market_id,
            'deployed_at': account_data['deployed_at'],
            'network': self.network
        }
    
    def _generate_account_address(self, market_id: str, creator_pubkey: str) -> str:
        """
        Generate a simulated Solana account address.
        
        In a real implementation, this would use Program Derived Addresses (PDAs)
        with seeds derived from market_id and creator_pubkey.
        """
        # Simulate PDA generation using hash
        seed_data = f"{market_id}:{creator_pubkey}:{self.account_counter}"
        hash_bytes = hashlib.sha256(seed_data.encode()).digest()[:32]
        
        # Convert to base58-like format (simplified)
        # Real Solana addresses are base58 encoded
        address = ''.join([f"{b:02x}" for b in hash_bytes[:16]])
        return f"PNP{address.upper()}"
    
    def get_market_account(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market account details by market_id."""
        return self.deployed_markets.get(market_id)
    
    def update_market_state(self,
                           market_id: str,
                           updates: Dict[str, Any]) -> bool:
        """
        Update market account state.
        
        Args:
            market_id: Market identifier
            updates: Dictionary of state updates
        
        Returns:
            True if update successful, False otherwise
        """
        if market_id not in self.deployed_markets:
            return False
        
        account = self.deployed_markets[market_id]
        account.update(updates)
        account['last_updated'] = datetime.utcnow().isoformat()
        
        return True
    
    def close_market_account(self, market_id: str) -> bool:
        """
        Close a market account (after settlement).
        
        Args:
            market_id: Market identifier
        
        Returns:
            True if closed successfully, False otherwise
        """
        if market_id not in self.deployed_markets:
            return False
        
        account = self.deployed_markets[market_id]
        account['status'] = 'closed'
        account['closed_at'] = datetime.utcnow().isoformat()
        
        print(f"[Market Factory] Market account closed: {market_id}")
        return True
    
    def list_deployed_markets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all deployed market accounts, optionally filtered by status."""
        markets = list(self.deployed_markets.values())
        if status:
            markets = [m for m in markets if m['status'] == status]
        return markets
    
    def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Alias for get_market_account for convenience."""
        return self.get_market_account(market_id)
    
    def list_markets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Alias for list_deployed_markets for convenience."""
        return self.list_deployed_markets(status)
    
    def add_liquidity(self, market_id: str, outcome: str, amount: float) -> Dict[str, Any]:
        """Add liquidity to a market outcome."""
        if market_id not in self.deployed_markets:
            raise ValueError(f"Market {market_id} not found")
        
        account = self.deployed_markets[market_id]
        
        if outcome not in account['outcome_liquidity']:
            raise ValueError(f"Invalid outcome: {outcome}")
        
        account['outcome_liquidity'][outcome] += amount
        account['total_liquidity'] += amount
        account['last_updated'] = datetime.utcnow().isoformat()
        
        return {
            'market_id': market_id,
            'outcome': outcome,
            'added': amount,
            'new_liquidity': account['outcome_liquidity'][outcome],
            'total_liquidity': account['total_liquidity']
        }
    
    def get_account_state(self, market_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current state of a market account.
        
        Returns a snapshot of the account state suitable for on-chain verification.
        """
        account = self.get_market_account(market_id)
        if not account:
            return None
        
        return {
            'account_address': account['account_address'],
            'market_id': account['market_id'],
            'status': account['status'],
            'total_liquidity': account['total_liquidity'],
            'outcome_liquidity': account['outcome_liquidity'],
            'last_updated': account.get('last_updated', account['deployed_at'])
        }


# Global factory instance
_factory_instance = None

def get_factory(network: str = 'mainnet-beta') -> MarketFactory:
    """Get or create the global MarketFactory instance."""
    global _factory_instance
    if _factory_instance is None:
        _factory_instance = MarketFactory(network=network)
    return _factory_instance


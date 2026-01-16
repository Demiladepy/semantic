"""
Collateral Manager

Handles privacy token locking and release for prediction markets.
Manages collateral deposits, withdrawals, and escrow operations.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class CollateralStatus(Enum):
    """Status of collateral in a market."""
    PENDING = "pending"
    LOCKED = "locked"
    RELEASED = "released"
    FORFEITED = "forfeited"


class CollateralManager:
    """
    Manages privacy token collateral for prediction markets.
    
    Handles:
    - Token locking for market creation
    - Escrow management
    - Collateral release after settlement
    - Partial releases for liquidity providers
    """
    
    # Supported privacy tokens
    SUPPORTED_TOKENS = {
        'ELUSIV': {
            'decimals': 9,
            'min_amount': 1.0,
            'max_amount': 1000000.0
        },
        'LIGHT': {
            'decimals': 9,
            'min_amount': 1.0,
            'max_amount': 1000000.0
        },
        'PNP': {
            'decimals': 9,
            'min_amount': 1.0,
            'max_amount': 1000000.0
        }
    }
    
    def __init__(self):
        """Initialize the Collateral Manager."""
        self.locked_collateral: Dict[str, Dict[str, Any]] = {}
        self.transaction_history: List[Dict[str, Any]] = []
    
    def lock_collateral(self,
                       market_id: str,
                       token: str,
                       amount: float,
                       owner_pubkey: str,
                       purpose: str = "market_creation") -> Dict[str, Any]:
        """
        Lock collateral tokens for a market.
        
        Args:
            market_id: Market identifier
            token: Privacy token symbol (ELUSIV, LIGHT, PNP)
            amount: Amount to lock
            owner_pubkey: Public key of the token owner
            purpose: Purpose of locking (market_creation, liquidity_provision, etc.)
        
        Returns:
            Dictionary with lock details:
                - lock_id: str - Unique lock identifier
                - status: str - Lock status
                - locked_at: str - ISO timestamp
        """
        # Validate token
        token_upper = token.upper()
        if token_upper not in self.SUPPORTED_TOKENS:
            raise ValueError(f"Unsupported token: {token}. Supported: {list(self.SUPPORTED_TOKENS.keys())}")
        
        # Validate amount
        token_info = self.SUPPORTED_TOKENS[token_upper]
        if amount < token_info['min_amount']:
            raise ValueError(f"Amount {amount} below minimum {token_info['min_amount']}")
        if amount > token_info['max_amount']:
            raise ValueError(f"Amount {amount} above maximum {token_info['max_amount']}")
        
        # Create lock
        lock_id = f"LOCK-{market_id}-{datetime.utcnow().timestamp()}"
        
        lock_data = {
            'lock_id': lock_id,
            'market_id': market_id,
            'token': token_upper,
            'amount': amount,
            'owner_pubkey': owner_pubkey,
            'purpose': purpose,
            'status': CollateralStatus.LOCKED.value,
            'locked_at': datetime.utcnow().isoformat(),
            'released_at': None,
            'release_transaction': None
        }
        
        self.locked_collateral[lock_id] = lock_data
        
        # Record transaction
        self._record_transaction(
            transaction_type='lock',
            market_id=market_id,
            token=token_upper,
            amount=amount,
            lock_id=lock_id
        )
        
        print(f"[Collateral Manager] Collateral locked")
        print(f"  Lock ID: {lock_id}")
        print(f"  Market ID: {market_id}")
        print(f"  Amount: {amount} {token_upper}")
        print(f"  Owner: {owner_pubkey[:8]}...{owner_pubkey[-8:]}")
        
        return {
            'lock_id': lock_id,
            'status': lock_data['status'],
            'locked_at': lock_data['locked_at']
        }
    
    def release_collateral(self,
                          lock_id: str,
                          recipient_pubkey: Optional[str] = None,
                          release_transaction: Optional[str] = None) -> Dict[str, Any]:
        """
        Release locked collateral.
        
        Args:
            lock_id: Lock identifier
            recipient_pubkey: Optional recipient (defaults to original owner)
            release_transaction: Optional transaction hash for on-chain verification
        
        Returns:
            Dictionary with release details
        """
        if lock_id not in self.locked_collateral:
            raise ValueError(f"Lock {lock_id} not found")
        
        lock = self.locked_collateral[lock_id]
        
        if lock['status'] != CollateralStatus.LOCKED.value:
            raise ValueError(f"Lock {lock_id} is not in LOCKED status (current: {lock['status']})")
        
        # Update lock status
        lock['status'] = CollateralStatus.RELEASED.value
        lock['released_at'] = datetime.utcnow().isoformat()
        lock['recipient_pubkey'] = recipient_pubkey or lock['owner_pubkey']
        lock['release_transaction'] = release_transaction
        
        # Record transaction
        self._record_transaction(
            transaction_type='release',
            market_id=lock['market_id'],
            token=lock['token'],
            amount=lock['amount'],
            lock_id=lock_id,
            transaction_hash=release_transaction
        )
        
        print(f"[Collateral Manager] Collateral released")
        print(f"  Lock ID: {lock_id}")
        print(f"  Amount: {lock['amount']} {lock['token']}")
        print(f"  Recipient: {lock['recipient_pubkey'][:8]}...{lock['recipient_pubkey'][-8:]}")
        
        return {
            'lock_id': lock_id,
            'status': lock['status'],
            'released_at': lock['released_at'],
            'amount': lock['amount'],
            'token': lock['token']
        }
    
    def partial_release(self,
                       lock_id: str,
                       amount: float,
                       recipient_pubkey: Optional[str] = None) -> Dict[str, Any]:
        """
        Partially release collateral (e.g., for liquidity providers).
        
        Args:
            lock_id: Lock identifier
            amount: Amount to release
            recipient_pubkey: Optional recipient
        
        Returns:
            Dictionary with release details
        """
        if lock_id not in self.locked_collateral:
            raise ValueError(f"Lock {lock_id} not found")
        
        lock = self.locked_collateral[lock_id]
        
        if amount > lock['amount']:
            raise ValueError(f"Release amount {amount} exceeds locked amount {lock['amount']}")
        
        if amount == lock['amount']:
            # Full release
            return self.release_collateral(lock_id, recipient_pubkey)
        
        # Partial release - create new lock for remaining amount
        remaining = lock['amount'] - amount
        
        # Update current lock
        lock['amount'] = remaining
        
        # Record partial release transaction
        self._record_transaction(
            transaction_type='partial_release',
            market_id=lock['market_id'],
            token=lock['token'],
            amount=amount,
            lock_id=lock_id
        )
        
        print(f"[Collateral Manager] Partial collateral release")
        print(f"  Lock ID: {lock_id}")
        print(f"  Released: {amount} {lock['token']}")
        print(f"  Remaining: {remaining} {lock['token']}")
        
        return {
            'lock_id': lock_id,
            'released_amount': amount,
            'remaining_amount': remaining,
            'token': lock['token']
        }
    
    def forfeit_collateral(self,
                          lock_id: str,
                          reason: str = "market_settlement") -> Dict[str, Any]:
        """
        Forfeit collateral (e.g., when market creator loses).
        
        Args:
            lock_id: Lock identifier
            reason: Reason for forfeiture
        
        Returns:
            Dictionary with forfeiture details
        """
        if lock_id not in self.locked_collateral:
            raise ValueError(f"Lock {lock_id} not found")
        
        lock = self.locked_collateral[lock_id]
        lock['status'] = CollateralStatus.FORFEITED.value
        lock['forfeited_at'] = datetime.utcnow().isoformat()
        lock['forfeit_reason'] = reason
        
        self._record_transaction(
            transaction_type='forfeit',
            market_id=lock['market_id'],
            token=lock['token'],
            amount=lock['amount'],
            lock_id=lock_id,
            reason=reason
        )
        
        print(f"[Collateral Manager] Collateral forfeited")
        print(f"  Lock ID: {lock_id}")
        print(f"  Reason: {reason}")
        
        return {
            'lock_id': lock_id,
            'status': lock['status'],
            'forfeited_at': lock['forfeited_at']
        }
    
    def get_lock(self, lock_id: str) -> Optional[Dict[str, Any]]:
        """Get lock details by lock_id."""
        return self.locked_collateral.get(lock_id)
    
    def get_market_locks(self, market_id: str) -> List[Dict[str, Any]]:
        """Get all locks for a specific market."""
        return [lock for lock in self.locked_collateral.values() 
                if lock['market_id'] == market_id]
    
    def get_total_locked(self, token: Optional[str] = None) -> float:
        """Get total amount of locked collateral, optionally filtered by token."""
        total = 0.0
        for lock in self.locked_collateral.values():
            if lock['status'] == CollateralStatus.LOCKED.value:
                if token is None or lock['token'] == token.upper():
                    total += lock['amount']
        return total
    
    def _record_transaction(self, **kwargs):
        """Record a transaction in history."""
        transaction = {
            'timestamp': datetime.utcnow().isoformat(),
            **kwargs
        }
        self.transaction_history.append(transaction)
    
    def get_transaction_history(self,
                               market_id: Optional[str] = None,
                               token: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get transaction history, optionally filtered."""
        transactions = self.transaction_history
        if market_id:
            transactions = [t for t in transactions if t.get('market_id') == market_id]
        if token:
            transactions = [t for t in transactions if t.get('token') == token.upper()]
        return transactions


# Global manager instance
_manager_instance = None

def get_manager() -> CollateralManager:
    """Get or create the global CollateralManager instance."""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = CollateralManager()
    return _manager_instance


"""
Risk Management & Position Tracking

Features:
- Capital allocation limits per opportunity
- Position size calculator based on available liquidity
- PnL tracking with attribution to strategy type
- Exposure monitoring across multiple markets
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PositionStatus(Enum):
    """Position status."""
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    FAILED = "failed"


class StrategyType(Enum):
    """Strategy type for attribution."""
    MARKET_REBALANCING = "market_rebalancing"
    COMBINATORIAL = "combinatorial"


@dataclass
class Position:
    """Trading position."""
    position_id: str
    market_id: str
    market_b_id: Optional[str]  # For combinatorial arbitrage
    strategy_type: StrategyType
    side: str  # "BUY" or "SELL"
    size_usd: float
    entry_price: float
    exit_price: Optional[float]
    status: PositionStatus
    opened_at: datetime
    closed_at: Optional[datetime]
    pnl_usd: float = 0.0
    pnl_pct: float = 0.0
    fees_paid_usd: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapitalAllocation:
    """Capital allocation for an opportunity."""
    opportunity_id: str
    strategy_type: StrategyType
    allocated_usd: float
    max_allocation_usd: float
    allocation_pct: float  # Percentage of total capital
    timestamp: datetime


@dataclass
class ExposureMetrics:
    """Exposure metrics across positions."""
    total_exposure_usd: float
    exposure_by_market: Dict[str, float]
    exposure_by_strategy: Dict[str, float]
    max_single_market_exposure: float
    max_single_market_exposure_pct: float  # Percentage of total capital
    diversification_score: float  # 0-1, higher = more diversified


class RiskManager:
    """
    Risk management and position tracking system.
    
    Features:
    - Capital allocation limits
    - Position sizing based on liquidity
    - PnL tracking with strategy attribution
    - Exposure monitoring
    """

    def __init__(
        self,
        total_capital_usd: float = 10000.0,
        max_position_size_pct: float = 10.0,  # Max 10% per position
        max_single_market_exposure_pct: float = 20.0,  # Max 20% per market
        max_total_exposure_pct: float = 80.0,  # Max 80% total exposure
    ):
        """
        Initialize risk manager.
        
        Args:
            total_capital_usd: Total capital available
            max_position_size_pct: Maximum position size as % of capital
            max_single_market_exposure_pct: Maximum exposure to single market
            max_total_exposure_pct: Maximum total exposure
        """
        self.total_capital_usd = total_capital_usd
        self.max_position_size_pct = max_position_size_pct
        self.max_single_market_exposure_pct = max_single_market_exposure_pct
        self.max_total_exposure_pct = max_total_exposure_pct

        self.positions: Dict[str, Position] = {}
        self.capital_allocations: List[CapitalAllocation] = []
        self.pnl_history: List[Dict[str, Any]] = []

        logger.info(f"✅ Risk Manager initialized (Capital: ${total_capital_usd:,.2f})")

    def calculate_position_size(
        self,
        opportunity: Any,
        available_liquidity: Optional[float] = None,
        max_allocation_usd: Optional[float] = None,
    ) -> float:
        """
        Calculate optimal position size based on risk limits and liquidity.
        
        Args:
            opportunity: Arbitrage opportunity (RebalancingOpportunity or CombinatorialOpportunity)
            available_liquidity: Available liquidity in orderbook
            max_allocation_usd: Maximum allocation for this opportunity
            
        Returns:
            Recommended position size in USD
        """
        # Start with maximum position size limit
        max_position = self.total_capital_usd * (self.max_position_size_pct / 100)

        # Apply opportunity-specific max allocation if provided
        if max_allocation_usd:
            max_position = min(max_position, max_allocation_usd)

        # Consider available liquidity
        if available_liquidity:
            # Don't take more than 50% of available liquidity to avoid market impact
            max_position = min(max_position, available_liquidity * 0.5)

        # Check current exposure
        current_exposure = self.get_total_exposure()
        max_total_exposure = self.total_capital_usd * (self.max_total_exposure_pct / 100)
        remaining_capacity = max_total_exposure - current_exposure

        if remaining_capacity <= 0:
            logger.warning("No remaining exposure capacity")
            return 0.0

        # Final position size is minimum of all constraints
        position_size = min(max_position, remaining_capacity)

        logger.info(
            f"📊 Position size calculated: ${position_size:,.2f} "
            f"(Max: ${max_position:,.2f}, Remaining: ${remaining_capacity:,.2f})"
        )

        return position_size

    def allocate_capital(
        self,
        opportunity_id: str,
        strategy_type: StrategyType,
        requested_amount_usd: float,
    ) -> Optional[CapitalAllocation]:
        """
        Allocate capital for an opportunity.
        
        Args:
            opportunity_id: Unique opportunity identifier
            strategy_type: Strategy type
            requested_amount_usd: Requested allocation amount
            
        Returns:
            CapitalAllocation if approved, None if rejected
        """
        # Check if we have capacity
        current_exposure = self.get_total_exposure()
        max_total_exposure = self.total_capital_usd * (self.max_total_exposure_pct / 100)
        remaining_capacity = max_total_exposure - current_exposure

        if requested_amount_usd > remaining_capacity:
            logger.warning(
                f"Insufficient capacity: requested ${requested_amount_usd:,.2f}, "
                f"available ${remaining_capacity:,.2f}"
            )
            return None

        # Check position size limit
        max_position = self.total_capital_usd * (self.max_position_size_pct / 100)
        if requested_amount_usd > max_position:
            logger.warning(
                f"Position size exceeds limit: ${requested_amount_usd:,.2f} > ${max_position:,.2f}"
            )
            return None

        allocation = CapitalAllocation(
            opportunity_id=opportunity_id,
            strategy_type=strategy_type,
            allocated_usd=requested_amount_usd,
            max_allocation_usd=max_position,
            allocation_pct=(requested_amount_usd / self.total_capital_usd * 100),
            timestamp=datetime.now(),
        )

        self.capital_allocations.append(allocation)
        logger.info(
            f"✅ Capital allocated: ${requested_amount_usd:,.2f} "
            f"({allocation.allocation_pct:.2f}% of capital) for {opportunity_id}"
        )

        return allocation

    def open_position(
        self,
        position_id: str,
        market_id: str,
        strategy_type: StrategyType,
        side: str,
        size_usd: float,
        entry_price: float,
        market_b_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Position:
        """
        Open a new position.
        
        Args:
            position_id: Unique position identifier
            market_id: Market identifier
            strategy_type: Strategy type
            side: "BUY" or "SELL"
            size_usd: Position size in USD
            entry_price: Entry price
            market_b_id: Second market ID (for combinatorial)
            metadata: Optional metadata
            
        Returns:
            Position object
        """
        position = Position(
            position_id=position_id,
            market_id=market_id,
            market_b_id=market_b_id,
            strategy_type=strategy_type,
            side=side,
            size_usd=size_usd,
            entry_price=entry_price,
            exit_price=None,
            status=PositionStatus.OPEN,
            opened_at=datetime.now(),
            closed_at=None,
            metadata=metadata or {},
        )

        self.positions[position_id] = position
        logger.info(
            f"📈 Position opened: {position_id} | "
            f"{strategy_type.value} | {side} ${size_usd:,.2f} @ {entry_price:.4f}"
        )

        return position

    def close_position(
        self,
        position_id: str,
        exit_price: float,
        fees_paid_usd: float = 0.0,
    ) -> Optional[Position]:
        """
        Close a position and calculate PnL.
        
        Args:
            position_id: Position identifier
            exit_price: Exit price
            fees_paid_usd: Fees paid for closing
            
        Returns:
            Updated Position object
        """
        if position_id not in self.positions:
            logger.error(f"Position not found: {position_id}")
            return None

        position = self.positions[position_id]

        if position.status != PositionStatus.OPEN:
            logger.warning(f"Position {position_id} is not open (status: {position.status.value})")
            return position

        # Calculate PnL
        if position.side == "BUY":
            pnl_pct = ((exit_price - position.entry_price) / position.entry_price) * 100
        else:  # SELL
            pnl_pct = ((position.entry_price - exit_price) / position.entry_price) * 100

        pnl_usd = (pnl_pct / 100) * position.size_usd - fees_paid_usd

        # Update position
        position.exit_price = exit_price
        position.status = PositionStatus.CLOSED
        position.closed_at = datetime.now()
        position.pnl_usd = pnl_usd
        position.pnl_pct = pnl_pct
        position.fees_paid_usd = fees_paid_usd

        # Record PnL history
        self.pnl_history.append({
            "position_id": position_id,
            "strategy_type": position.strategy_type.value,
            "pnl_usd": pnl_usd,
            "pnl_pct": pnl_pct,
            "timestamp": datetime.now().isoformat(),
        })

        logger.info(
            f"📉 Position closed: {position_id} | "
            f"PnL: ${pnl_usd:,.2f} ({pnl_pct:.2f}%)"
        )

        return position

    def get_total_exposure(self) -> float:
        """Get total current exposure across all open positions."""
        total = sum(
            pos.size_usd
            for pos in self.positions.values()
            if pos.status == PositionStatus.OPEN
        )
        return total

    def get_exposure_metrics(self) -> ExposureMetrics:
        """Get exposure metrics across all positions."""
        open_positions = [
            pos for pos in self.positions.values()
            if pos.status == PositionStatus.OPEN
        ]

        # Total exposure
        total_exposure = sum(pos.size_usd for pos in open_positions)

        # Exposure by market
        exposure_by_market: Dict[str, float] = {}
        for pos in open_positions:
            exposure_by_market[pos.market_id] = (
                exposure_by_market.get(pos.market_id, 0) + pos.size_usd
            )
            if pos.market_b_id:
                exposure_by_market[pos.market_b_id] = (
                    exposure_by_market.get(pos.market_b_id, 0) + pos.size_usd
                )

        # Exposure by strategy
        exposure_by_strategy: Dict[str, float] = {}
        for pos in open_positions:
            strategy_name = pos.strategy_type.value
            exposure_by_strategy[strategy_name] = (
                exposure_by_strategy.get(strategy_name, 0) + pos.size_usd
            )

        # Max single market exposure
        max_single_market_exposure = max(exposure_by_market.values()) if exposure_by_market else 0.0
        max_single_market_exposure_pct = (
            (max_single_market_exposure / self.total_capital_usd * 100)
            if self.total_capital_usd > 0 else 0.0
        )

        # Diversification score (inverse of concentration)
        if total_exposure > 0:
            # Herfindahl-Hirschman Index (HHI) for diversification
            market_shares = [exp / total_exposure for exp in exposure_by_market.values()]
            hhi = sum(share ** 2 for share in market_shares)
            diversification_score = 1.0 - hhi  # Higher = more diversified
        else:
            diversification_score = 1.0

        return ExposureMetrics(
            total_exposure_usd=total_exposure,
            exposure_by_market=exposure_by_market,
            exposure_by_strategy=exposure_by_strategy,
            max_single_market_exposure=max_single_market_exposure,
            max_single_market_exposure_pct=max_single_market_exposure_pct,
            diversification_score=diversification_score,
        )

    def get_pnl_summary(
        self,
        strategy_type: Optional[StrategyType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Get PnL summary with strategy attribution.
        
        Args:
            strategy_type: Filter by strategy type
            start_date: Start date filter
            end_date: End date filter
            
        Returns:
            PnL summary dict
        """
        filtered_history = self.pnl_history.copy()

        if strategy_type:
            filtered_history = [
                h for h in filtered_history
                if h["strategy_type"] == strategy_type.value
            ]

        if start_date:
            filtered_history = [
                h for h in filtered_history
                if datetime.fromisoformat(h["timestamp"]) >= start_date
            ]

        if end_date:
            filtered_history = [
                h for h in filtered_history
                if datetime.fromisoformat(h["timestamp"]) <= end_date
            ]

        total_pnl = sum(h["pnl_usd"] for h in filtered_history)
        total_trades = len(filtered_history)
        winning_trades = len([h for h in filtered_history if h["pnl_usd"] > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        avg_pnl = total_pnl / total_trades if total_trades > 0 else 0.0

        return {
            "total_pnl_usd": total_pnl,
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate_pct": win_rate,
            "avg_pnl_usd": avg_pnl,
            "strategy_type": strategy_type.value if strategy_type else "all",
        }

    def save_state(self, filepath: str):
        """Save risk manager state to JSON file."""
        state = {
            "total_capital_usd": self.total_capital_usd,
            "positions": {
                pid: {
                    "position_id": pos.position_id,
                    "market_id": pos.market_id,
                    "market_b_id": pos.market_b_id,
                    "strategy_type": pos.strategy_type.value,
                    "side": pos.side,
                    "size_usd": pos.size_usd,
                    "entry_price": pos.entry_price,
                    "exit_price": pos.exit_price,
                    "status": pos.status.value,
                    "opened_at": pos.opened_at.isoformat(),
                    "closed_at": pos.closed_at.isoformat() if pos.closed_at else None,
                    "pnl_usd": pos.pnl_usd,
                    "pnl_pct": pos.pnl_pct,
                    "fees_paid_usd": pos.fees_paid_usd,
                    "metadata": pos.metadata,
                }
                for pid, pos in self.positions.items()
            },
            "pnl_history": self.pnl_history,
        }

        with open(filepath, "w") as f:
            json.dump(state, f, indent=2)

        logger.info(f"💾 Risk manager state saved to {filepath}")


# ========================
# UTILITY FUNCTIONS
# ========================

def get_risk_manager(
    total_capital_usd: float = 10000.0,
) -> RiskManager:
    """Factory function for RiskManager."""
    return RiskManager(total_capital_usd=total_capital_usd)


if __name__ == "__main__":
    # Test the risk manager
    rm = get_risk_manager(total_capital_usd=10000.0)

    # Test position sizing
    class MockOpportunity:
        expected_profit_pct = 3.0

    opp = MockOpportunity()
    position_size = rm.calculate_position_size(opp, available_liquidity=5000.0)
    print(f"Recommended position size: ${position_size:,.2f}")

    # Test capital allocation
    allocation = rm.allocate_capital("opp1", StrategyType.MARKET_REBALANCING, 500.0)
    print(f"Allocation approved: {allocation is not None}")

    # Test exposure metrics
    metrics = rm.get_exposure_metrics()
    print(f"Total exposure: ${metrics.total_exposure_usd:,.2f}")
    print(f"Diversification score: {metrics.diversification_score:.2f}")

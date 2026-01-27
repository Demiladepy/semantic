"""
Backtesting Framework

Features:
- Historical data replay system
- Strategy performance metrics:
  - Win rate
  - Average profit per trade
  - Maximum drawdown
  - Capital efficiency
- A/B testing for NLI threshold tuning
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import numpy as np
import pandas as pd

from clob_orderbook_client import HistoricalOrderbookData
from arbitrage_strategies import (
    MarketRebalancingStrategy,
    CombinatorialArbitrageStrategy,
    RebalancingOpportunity,
    CombinatorialOpportunity,
)
from risk_manager import RiskManager, StrategyType, PositionStatus
from enhanced_fee_calculator import EnhancedFeeCalculator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BacktestConfig:
    """Backtesting configuration."""
    start_date: datetime
    end_date: datetime
    initial_capital_usd: float
    min_profit_margin_pct: float
    max_position_size_pct: float
    transaction_cost_model: str  # "conservative", "realistic", "optimistic"
    slippage_model: str  # "none", "linear", "sqrt"
    execution_delay_ms: int  # Simulated execution delay


@dataclass
class BacktestTrade:
    """Single backtest trade."""
    trade_id: str
    timestamp: datetime
    strategy_type: StrategyType
    market_id: str
    market_b_id: Optional[str]
    entry_price: float
    exit_price: float
    size_usd: float
    pnl_usd: float
    pnl_pct: float
    fees_usd: float
    slippage_usd: float
    execution_time_ms: float


@dataclass
class BacktestMetrics:
    """Backtesting performance metrics."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    total_pnl_usd: float
    avg_profit_per_trade_usd: float
    max_drawdown_usd: float
    max_drawdown_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    capital_efficiency: float  # Total PnL / Capital Used
    profit_factor: float  # Gross Profit / Gross Loss
    avg_holding_period_hours: float
    trades_by_strategy: Dict[str, int]
    pnl_by_strategy: Dict[str, float]


class BacktestEngine:
    """
    Backtesting engine for arbitrage strategies.
    
    Features:
    - Historical data replay
    - Performance metrics calculation
    - A/B testing support
    """

    def __init__(
        self,
        config: BacktestConfig,
        rebalancing_strategy: Optional[MarketRebalancingStrategy] = None,
        combinatorial_strategy: Optional[CombinatorialArbitrageStrategy] = None,
        fee_calculator: Optional[EnhancedFeeCalculator] = None,
    ):
        """
        Initialize backtest engine.
        
        Args:
            config: Backtest configuration
            rebalancing_strategy: Market rebalancing strategy
            combinatorial_strategy: Combinatorial arbitrage strategy
            fee_calculator: Fee calculator
        """
        self.config = config
        self.rebalancing_strategy = rebalancing_strategy or MarketRebalancingStrategy()
        self.combinatorial_strategy = combinatorial_strategy or CombinatorialArbitrageStrategy()
        self.fee_calculator = fee_calculator or EnhancedFeeCalculator(
            min_profit_margin_pct=config.min_profit_margin_pct
        )

        self.risk_manager = RiskManager(
            total_capital_usd=config.initial_capital_usd,
            max_position_size_pct=config.max_position_size_pct,
        )

        self.trades: List[BacktestTrade] = []
        self.equity_curve: List[Tuple[datetime, float]] = []

        logger.info(f"✅ Backtest Engine initialized ({config.start_date} to {config.end_date})")

    def load_historical_data(
        self,
        filepath: str,
    ) -> List[HistoricalOrderbookData]:
        """Load historical orderbook data from JSON file."""
        with open(filepath, "r") as f:
            data = json.load(f)

        historical_points = []
        for point in data:
            # Convert timestamp if needed
            if isinstance(point.get("timestamp"), str):
                timestamp = datetime.fromisoformat(point["timestamp"])
            else:
                timestamp = datetime.fromtimestamp(point["timestamp"])

            # Filter by date range
            if self.config.start_date <= timestamp <= self.config.end_date:
                historical_points.append(HistoricalOrderbookData(**point))

        logger.info(f"📂 Loaded {len(historical_points)} historical data points")
        return historical_points

    def replay_historical_data(
        self,
        historical_data: List[HistoricalOrderbookData],
    ) -> BacktestMetrics:
        """
        Replay historical data and simulate trading.
        
        Args:
            historical_data: Historical orderbook data points
            
        Returns:
            BacktestMetrics with performance results
        """
        logger.info(f"🎬 Starting backtest replay ({len(historical_data)} data points)...")

        # Group data by market and time
        data_by_market: Dict[str, List[HistoricalOrderbookData]] = {}
        for point in historical_data:
            market_id = point.market_id
            if market_id not in data_by_market:
                data_by_market[market_id] = []
            data_by_market[market_id].append(point)

        # Sort each market's data by timestamp
        for market_id in data_by_market:
            data_by_market[market_id].sort(key=lambda x: x.timestamp)

        # Simulate trading over time
        current_capital = self.config.initial_capital_usd
        peak_capital = current_capital
        max_drawdown = 0.0

        # Process data chronologically
        all_timestamps = sorted(set(point.timestamp for point in historical_data))
        
        for timestamp in all_timestamps:
            # Get current market states
            current_markets = self._get_market_states_at_timestamp(
                historical_data, timestamp
            )

            # Scan for opportunities
            opportunities = self._scan_opportunities(current_markets, timestamp)

            # Execute trades
            for opp in opportunities:
                trade = self._execute_trade(opp, timestamp, current_capital)
                if trade:
                    self.trades.append(trade)
                    current_capital += trade.pnl_usd

                    # Update drawdown
                    if current_capital > peak_capital:
                        peak_capital = current_capital
                    drawdown = (peak_capital - current_capital) / peak_capital * 100
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown

                    self.equity_curve.append((timestamp, current_capital))

        # Calculate metrics
        metrics = self._calculate_metrics(max_drawdown)

        logger.info(f"✅ Backtest complete: {metrics.total_trades} trades, ${metrics.total_pnl_usd:,.2f} PnL")
        return metrics

    def _get_market_states_at_timestamp(
        self,
        historical_data: List[HistoricalOrderbookData],
        timestamp: float,
    ) -> List[Dict[str, Any]]:
        """Get market states at a specific timestamp."""
        markets = []
        tolerance_seconds = 60  # 1 minute tolerance

        for point in historical_data:
            if abs(point.timestamp - timestamp) <= tolerance_seconds:
                markets.append({
                    "id": point.market_id,
                    "best_bid": point.best_bid,
                    "best_ask": point.best_ask,
                    "yes_price": point.best_bid or 0.5,  # Simplified
                    "no_price": (1.0 - point.best_bid) if point.best_bid else 0.5,
                    "timestamp": point.timestamp,
                })

        return markets

    def _scan_opportunities(
        self,
        markets: List[Dict[str, Any]],
        timestamp: float,
    ) -> List[Any]:
        """Scan for opportunities at current timestamp."""
        opportunities = []

        # Market rebalancing opportunities
        for market in markets:
            opp = self.rebalancing_strategy.detect_opportunity(
                market_id=market["id"],
                yes_price=market.get("yes_price", 0.5),
                no_price=market.get("no_price", 0.5),
            )
            if opp:
                opportunities.append(opp)

        # Combinatorial opportunities (simplified - would need market pairs)
        # For now, skip combinatorial in backtest

        return opportunities

    def _execute_trade(
        self,
        opportunity: Any,
        timestamp: float,
        available_capital: float,
    ) -> Optional[BacktestTrade]:
        """Execute a trade based on opportunity."""
        # Calculate position size
        position_size = self.risk_manager.calculate_position_size(
            opportunity,
            available_liquidity=10000.0,  # Assume sufficient liquidity
        )

        if position_size <= 0:
            return None

        # Check capital allocation
        allocation = self.risk_manager.allocate_capital(
            opportunity_id=f"opp_{timestamp}",
            strategy_type=StrategyType.MARKET_REBALANCING,
            requested_amount_usd=position_size,
        )

        if not allocation:
            return None

        # Simulate entry and exit
        if isinstance(opportunity, RebalancingOpportunity):
            entry_price = (opportunity.yes_price + opportunity.no_price) / 2
            # Exit when prices converge to $1.00
            exit_price = 0.5  # Simplified - would track actual convergence
            strategy_type = StrategyType.MARKET_REBALANCING
        else:
            return None  # Skip other types for now

        # Calculate PnL
        spread = abs(entry_price - exit_price)
        gross_pnl = spread * position_size

        # Apply transaction costs
        fees = self._calculate_transaction_costs(position_size)
        slippage = self._calculate_slippage(position_size, self.config.slippage_model)

        net_pnl = gross_pnl - fees - slippage
        pnl_pct = (net_pnl / position_size * 100) if position_size > 0 else 0.0

        # Simulate execution delay
        execution_time = self.config.execution_delay_ms

        trade = BacktestTrade(
            trade_id=f"trade_{timestamp}_{len(self.trades)}",
            timestamp=datetime.fromtimestamp(timestamp),
            strategy_type=strategy_type,
            market_id=opportunity.market_id,
            market_b_id=None,
            entry_price=entry_price,
            exit_price=exit_price,
            size_usd=position_size,
            pnl_usd=net_pnl,
            pnl_pct=pnl_pct,
            fees_usd=fees,
            slippage_usd=slippage,
            execution_time_ms=execution_time,
        )

        return trade

    def _calculate_transaction_costs(self, position_size: float) -> float:
        """Calculate transaction costs based on model."""
        if self.config.transaction_cost_model == "conservative":
            return position_size * 0.03  # 3% total costs
        elif self.config.transaction_cost_model == "realistic":
            return position_size * 0.02  # 2% total costs
        else:  # optimistic
            return position_size * 0.01  # 1% total costs

    def _calculate_slippage(self, position_size: float, model: str) -> float:
        """Calculate slippage based on model."""
        if model == "none":
            return 0.0
        elif model == "linear":
            return position_size * 0.001  # 0.1% linear slippage
        else:  # sqrt
            return position_size * 0.0005 * np.sqrt(position_size / 1000)  # Sqrt model

    def _calculate_metrics(self, max_drawdown: float) -> BacktestMetrics:
        """Calculate backtest performance metrics."""
        if not self.trades:
            return BacktestMetrics(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate_pct=0.0,
                total_pnl_usd=0.0,
                avg_profit_per_trade_usd=0.0,
                max_drawdown_usd=0.0,
                max_drawdown_pct=0.0,
                sharpe_ratio=0.0,
                sortino_ratio=0.0,
                capital_efficiency=0.0,
                profit_factor=0.0,
                avg_holding_period_hours=0.0,
                trades_by_strategy={},
                pnl_by_strategy={},
            )

        total_trades = len(self.trades)
        winning_trades = len([t for t in self.trades if t.pnl_usd > 0])
        losing_trades = total_trades - winning_trades
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0

        total_pnl = sum(t.pnl_usd for t in self.trades)
        avg_profit = total_pnl / total_trades if total_trades > 0 else 0.0

        # Drawdown
        max_drawdown_usd = (max_drawdown / 100) * self.config.initial_capital_usd

        # Sharpe ratio (simplified)
        returns = [t.pnl_pct / 100 for t in self.trades]
        if len(returns) > 1 and np.std(returns) > 0:
            sharpe = np.mean(returns) / np.std(returns) * np.sqrt(252)  # Annualized
        else:
            sharpe = 0.0

        # Sortino ratio (downside deviation only)
        downside_returns = [r for r in returns if r < 0]
        if len(downside_returns) > 1 and np.std(downside_returns) > 0:
            sortino = np.mean(returns) / np.std(downside_returns) * np.sqrt(252)
        else:
            sortino = 0.0

        # Capital efficiency
        total_capital_used = sum(t.size_usd for t in self.trades)
        capital_efficiency = (total_pnl / total_capital_used * 100) if total_capital_used > 0 else 0.0

        # Profit factor
        gross_profit = sum(t.pnl_usd for t in self.trades if t.pnl_usd > 0)
        gross_loss = abs(sum(t.pnl_usd for t in self.trades if t.pnl_usd < 0))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else float('inf')

        # Trades by strategy
        trades_by_strategy: Dict[str, int] = {}
        pnl_by_strategy: Dict[str, float] = {}
        for trade in self.trades:
            strategy_name = trade.strategy_type.value
            trades_by_strategy[strategy_name] = trades_by_strategy.get(strategy_name, 0) + 1
            pnl_by_strategy[strategy_name] = pnl_by_strategy.get(strategy_name, 0) + trade.pnl_usd

        # Average holding period (simplified - assume 1 hour per trade)
        avg_holding_period = 1.0

        return BacktestMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate_pct=win_rate,
            total_pnl_usd=total_pnl,
            avg_profit_per_trade_usd=avg_profit,
            max_drawdown_usd=max_drawdown_usd,
            max_drawdown_pct=max_drawdown,
            sharpe_ratio=sharpe,
            sortino_ratio=sortino,
            capital_efficiency=capital_efficiency,
            profit_factor=profit_factor,
            avg_holding_period_hours=avg_holding_period,
            trades_by_strategy=trades_by_strategy,
            pnl_by_strategy=pnl_by_strategy,
        )

    def export_results(self, filepath: str):
        """Export backtest results to JSON."""
        results = {
            "config": {
                "start_date": self.config.start_date.isoformat(),
                "end_date": self.config.end_date.isoformat(),
                "initial_capital_usd": self.config.initial_capital_usd,
            },
            "trades": [
                {
                    "trade_id": t.trade_id,
                    "timestamp": t.timestamp.isoformat(),
                    "strategy_type": t.strategy_type.value,
                    "market_id": t.market_id,
                    "pnl_usd": t.pnl_usd,
                    "pnl_pct": t.pnl_pct,
                }
                for t in self.trades
            ],
            "equity_curve": [
                {"timestamp": ts.isoformat(), "equity": eq}
                for ts, eq in self.equity_curve
            ],
        }

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

        logger.info(f"💾 Backtest results exported to {filepath}")


def run_ab_test(
    config: BacktestConfig,
    historical_data: List[HistoricalOrderbookData],
    parameter_name: str,
    parameter_values: List[Any],
) -> Dict[str, BacktestMetrics]:
    """
    Run A/B test with different parameter values.
    
    Args:
        config: Base backtest configuration
        historical_data: Historical data to test
        parameter_name: Parameter to vary (e.g., "min_profit_margin_pct")
        parameter_values: List of values to test
        
    Returns:
        Dict mapping parameter value to BacktestMetrics
    """
    results = {}

    for value in parameter_values:
        logger.info(f"🧪 Testing {parameter_name} = {value}")

        # Create modified config
        modified_config = BacktestConfig(**vars(config))
        setattr(modified_config, parameter_name, value)

        # Run backtest
        engine = BacktestEngine(modified_config)
        metrics = engine.replay_historical_data(historical_data)

        results[str(value)] = metrics

    return results


# ========================
# UTILITY FUNCTIONS
# ========================

def get_backtest_engine(config: BacktestConfig) -> BacktestEngine:
    """Factory function for BacktestEngine."""
    return BacktestEngine(config)


if __name__ == "__main__":
    # Example backtest configuration
    config = BacktestConfig(
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 31),
        initial_capital_usd=10000.0,
        min_profit_margin_pct=2.5,
        max_position_size_pct=10.0,
        transaction_cost_model="realistic",
        slippage_model="linear",
        execution_delay_ms=100,
    )

    engine = get_backtest_engine(config)
    print("✅ Backtest engine created")
    print(f"   Period: {config.start_date} to {config.end_date}")
    print(f"   Capital: ${config.initial_capital_usd:,.2f}")

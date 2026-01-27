"""
Enhanced Transaction Cost Modeling

Comprehensive fee calculator that accounts for:
- Polymarket's 2% winner fee
- Gas fees for on-chain execution
- Slippage estimation based on orderbook depth
- Minimum spread threshold detection (2.5-3% typically needed)
- Break-even analysis before executing trades
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from web3 import Web3
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False

from clob_orderbook_client import OrderbookSnapshot, OrderbookLevel
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeeStructure(Enum):
    """Fee structures for different platforms."""
    POLYMARKET_WINNER_FEE = 0.02  # 2% on winnings
    POLYMARKET_TAKER_FEE = 0.00  # No taker fee (fees on settlement)
    KALSHI_TAKER_FEE_LOW = 0.005  # 0.5% at extremes (<20 or >80)
    KALSHI_TAKER_FEE_MID = 0.015  # 1.5% in middle (20-80)
    PNP_EXCHANGE_FEE = 0.01  # 1% (estimated)


@dataclass
class GasEstimate:
    """Gas cost estimation."""
    gas_units: int
    gas_price_gwei: float
    gas_cost_matic: float
    gas_cost_usd: float
    matic_price_usd: float


@dataclass
class SlippageEstimate:
    """Slippage estimation."""
    best_price: float
    execution_price: float
    slippage_pct: float
    slippage_usd: float
    available_liquidity: float


@dataclass
class TransactionCosts:
    """Complete transaction cost breakdown."""
    platform_fees_usd: float
    gas_costs_usd: float
    slippage_costs_usd: float
    total_costs_usd: float
    total_costs_pct: float


@dataclass
class ProfitabilityAnalysis:
    """Complete profitability analysis."""
    gross_spread_usd: float
    gross_spread_pct: float
    transaction_costs: TransactionCosts
    net_profit_usd: float
    net_profit_pct: float
    is_profitable: bool
    break_even_spread_pct: float
    min_required_spread_pct: float
    recommendation: str
    risk_factors: List[str]


class EnhancedFeeCalculator:
    """
    Enhanced fee calculator with comprehensive cost modeling.
    
    Features:
    - Platform-specific fee calculation
    - Gas cost estimation with current network prices
    - Slippage estimation from orderbook depth
    - Break-even analysis
    - Minimum spread threshold detection
    """

    def __init__(
        self,
        min_profit_margin_pct: float = 2.5,
        matic_price_usd: Optional[float] = None,
    ):
        """
        Initialize enhanced fee calculator.
        
        Args:
            min_profit_margin_pct: Minimum profit margin required (default 2.5%)
            matic_price_usd: MATIC price in USD (fetches if not provided)
        """
        self.min_profit_margin_pct = min_profit_margin_pct
        self.matic_price_usd = matic_price_usd or 1.0  # Default estimate
        self.w3 = None
        
        if WEB3_AVAILABLE and os.getenv("POLYGON_RPC_URL"):
            try:
                self.w3 = Web3(Web3.HTTPProvider(os.getenv("POLYGON_RPC_URL")))
                logger.info("✅ Web3 connected for gas estimation")
            except Exception as e:
                logger.warning(f"Could not connect to Web3: {e}")

    def estimate_gas_cost(
        self,
        gas_units: int = 150000,
        gas_price_gwei: Optional[float] = None,
    ) -> GasEstimate:
        """
        Estimate gas cost for a transaction.
        
        Args:
            gas_units: Estimated gas units (default 150k for typical order)
            gas_price_gwei: Gas price in Gwei (fetches if not provided)
            
        Returns:
            GasEstimate with cost breakdown
        """
        if gas_price_gwei is None:
            gas_price_gwei = self._fetch_gas_price_gwei() or 30.0

        # Convert to MATIC
        cost_wei = gas_units * (gas_price_gwei * 1e9)
        cost_matic = cost_wei / 1e18
        cost_usd = cost_matic * self.matic_price_usd

        return GasEstimate(
            gas_units=gas_units,
            gas_price_gwei=gas_price_gwei,
            gas_cost_matic=cost_matic,
            gas_cost_usd=cost_usd,
            matic_price_usd=self.matic_price_usd,
        )

    def _fetch_gas_price_gwei(self) -> Optional[float]:
        """Fetch current gas price from Polygon network."""
        if not self.w3 or not self.w3.is_connected():
            return None

        try:
            gas_price_wei = self.w3.eth.gas_price
            gas_price_gwei = self.w3.from_wei(gas_price_wei, "gwei")
            return float(gas_price_gwei)
        except Exception as e:
            logger.warning(f"Failed to fetch gas price: {e}")
            return None

    def calculate_platform_fees(
        self,
        position_size_usd: float,
        platform: str,
        contract_price: Optional[float] = None,
        is_winner: bool = True,
    ) -> float:
        """
        Calculate platform-specific fees.
        
        Args:
            position_size_usd: Position size in USD
            platform: "polymarket", "kalshi", or "pnp"
            contract_price: Contract price (0-1) for Kalshi fee calculation
            is_winner: Whether this is a winning position (for Polymarket)
            
        Returns:
            Fee amount in USD
        """
        platform_lower = platform.lower()

        if platform_lower == "polymarket":
            # Polymarket charges 2% on winnings only
            if is_winner:
                return position_size_usd * FeeStructure.POLYMARKET_WINNER_FEE.value
            return 0.0

        elif platform_lower == "kalshi":
            # Kalshi fee varies by contract price
            if contract_price is None:
                contract_price = 0.5  # Default midpoint
            
            contract_price_cents = contract_price * 100
            if contract_price_cents < 20 or contract_price_cents > 80:
                fee_rate = FeeStructure.KALSHI_TAKER_FEE_LOW.value
            else:
                fee_rate = FeeStructure.KALSHI_TAKER_FEE_MID.value
            
            return position_size_usd * fee_rate

        elif platform_lower == "pnp":
            return position_size_usd * FeeStructure.PNP_EXCHANGE_FEE.value

        else:
            logger.warning(f"Unknown platform: {platform}, assuming 1% fee")
            return position_size_usd * 0.01

    def estimate_slippage(
        self,
        orderbook: Optional[OrderbookSnapshot],
        order_size_usd: float,
        side: str = "BUY",
    ) -> SlippageEstimate:
        """
        Estimate slippage based on orderbook depth.
        
        Args:
            orderbook: Orderbook snapshot
            order_size_usd: Order size in USD
            side: "BUY" or "SELL"
            
        Returns:
            SlippageEstimate with execution price and slippage
        """
        if not orderbook:
            # Conservative default: 0.5% slippage
            return SlippageEstimate(
                best_price=0.5,
                execution_price=0.5025,
                slippage_pct=0.5,
                slippage_usd=order_size_usd * 0.005,
                available_liquidity=0.0,
            )

        levels = orderbook.asks if side == "BUY" else orderbook.bids
        best_price = orderbook.best_ask if side == "BUY" else orderbook.best_bid

        if not levels or not best_price:
            return SlippageEstimate(
                best_price=0.5,
                execution_price=0.5025,
                slippage_pct=0.5,
                slippage_usd=order_size_usd * 0.005,
                available_liquidity=0.0,
            )

        # Calculate weighted average execution price
        total_filled = 0.0
        weighted_price_sum = 0.0
        available_liquidity = sum(level.size for level in levels)

        for level in levels:
            if total_filled >= order_size_usd:
                break

            fill_amount = min(level.size, order_size_usd - total_filled)
            weighted_price_sum += level.price * fill_amount
            total_filled += fill_amount

        if total_filled == 0:
            execution_price = best_price
            slippage_pct = 0.0
        else:
            execution_price = weighted_price_sum / total_filled
            slippage_pct = abs(execution_price - best_price) / best_price * 100

        slippage_usd = order_size_usd * (slippage_pct / 100)

        return SlippageEstimate(
            best_price=best_price,
            execution_price=execution_price,
            slippage_pct=slippage_pct,
            slippage_usd=slippage_usd,
            available_liquidity=available_liquidity,
        )

    def calculate_transaction_costs(
        self,
        market_a_orderbook: Optional[OrderbookSnapshot],
        market_b_orderbook: Optional[OrderbookSnapshot],
        position_size_usd: float,
        market_a_platform: str,
        market_b_platform: str,
        market_a_price: Optional[float] = None,
        market_b_price: Optional[float] = None,
    ) -> TransactionCosts:
        """
        Calculate total transaction costs for a two-leg arbitrage.
        
        Args:
            market_a_orderbook: Orderbook for first market
            market_b_orderbook: Orderbook for second market
            position_size_usd: Position size in USD
            market_a_platform: Platform name for market A
            market_b_platform: Platform name for market B
            market_a_price: Price for market A (for fee calculation)
            market_b_price: Price for market B (for fee calculation)
            
        Returns:
            TransactionCosts with complete breakdown
        """
        # Platform fees (assuming both legs win)
        fee_a = self.calculate_platform_fees(
            position_size_usd,
            market_a_platform,
            contract_price=market_a_price,
            is_winner=True,
        )
        fee_b = self.calculate_platform_fees(
            position_size_usd,
            market_b_platform,
            contract_price=market_b_price,
            is_winner=True,
        )
        platform_fees = fee_a + fee_b

        # Gas costs (two transactions)
        gas_estimate = self.estimate_gas_cost(gas_units=150000 * 2)  # Two legs
        gas_costs = gas_estimate.gas_cost_usd

        # Slippage costs
        slippage_a = self.estimate_slippage(market_a_orderbook, position_size_usd, "BUY")
        slippage_b = self.estimate_slippage(market_b_orderbook, position_size_usd, "SELL")
        slippage_costs = slippage_a.slippage_usd + slippage_b.slippage_usd

        total_costs = platform_fees + gas_costs + slippage_costs
        total_costs_pct = (total_costs / position_size_usd * 100) if position_size_usd > 0 else 0.0

        return TransactionCosts(
            platform_fees_usd=platform_fees,
            gas_costs_usd=gas_costs,
            slippage_costs_usd=slippage_costs,
            total_costs_usd=total_costs,
            total_costs_pct=total_costs_pct,
        )

    def analyze_profitability(
        self,
        market_a_price: float,
        market_b_price: float,
        market_a_orderbook: Optional[OrderbookSnapshot],
        market_b_orderbook: Optional[OrderbookSnapshot],
        position_size_usd: float,
        market_a_platform: str,
        market_b_platform: str,
    ) -> ProfitabilityAnalysis:
        """
        Complete profitability analysis with break-even calculation.
        
        Args:
            market_a_price: Price on market A
            market_b_price: Price on market B
            market_a_orderbook: Orderbook for market A
            market_b_orderbook: Orderbook for market B
            position_size_usd: Position size in USD
            market_a_platform: Platform name for market A
            market_b_platform: Platform name for market B
            
        Returns:
            ProfitabilityAnalysis with complete breakdown
        """
        # Calculate gross spread
        gross_spread = abs(market_a_price - market_b_price) * position_size_usd
        gross_spread_pct = abs(market_a_price - market_b_price) / max(market_a_price, market_b_price) * 100

        # Calculate transaction costs
        transaction_costs = self.calculate_transaction_costs(
            market_a_orderbook=market_a_orderbook,
            market_b_orderbook=market_b_orderbook,
            position_size_usd=position_size_usd,
            market_a_platform=market_a_platform,
            market_b_platform=market_b_platform,
            market_a_price=market_a_price,
            market_b_price=market_b_price,
        )

        # Calculate net profit
        net_profit = gross_spread - transaction_costs.total_costs_usd
        net_profit_pct = (net_profit / position_size_usd * 100) if position_size_usd > 0 else 0.0

        # Break-even analysis
        break_even_spread_pct = transaction_costs.total_costs_pct
        min_required_spread_pct = break_even_spread_pct + self.min_profit_margin_pct

        # Determine profitability
        is_profitable = net_profit_pct >= self.min_profit_margin_pct

        # Risk factors
        risk_factors = []
        if transaction_costs.slippage_costs_usd > gross_spread * 0.3:
            risk_factors.append("High slippage risk (>30% of gross spread)")
        if transaction_costs.gas_costs_usd > gross_spread * 0.2:
            risk_factors.append("High gas costs (>20% of gross spread)")
        if not market_a_orderbook or not market_b_orderbook:
            risk_factors.append("Missing orderbook data - using conservative estimates")
        if gross_spread_pct < min_required_spread_pct:
            risk_factors.append(f"Spread ({gross_spread_pct:.2f}%) below minimum required ({min_required_spread_pct:.2f}%)")

        # Recommendation
        if is_profitable:
            recommendation = f"✅ PROFITABLE - Execute trade (Net: {net_profit_pct:.2f}%)"
        elif gross_spread_pct >= break_even_spread_pct:
            recommendation = f"⚠️ BREAK-EVEN - Consider executing if spread improves (Net: {net_profit_pct:.2f}%)"
        else:
            recommendation = f"❌ NOT PROFITABLE - Skip trade (Net: {net_profit_pct:.2f}%, Need: {min_required_spread_pct:.2f}%)"

        return ProfitabilityAnalysis(
            gross_spread_usd=gross_spread,
            gross_spread_pct=gross_spread_pct,
            transaction_costs=transaction_costs,
            net_profit_usd=net_profit,
            net_profit_pct=net_profit_pct,
            is_profitable=is_profitable,
            break_even_spread_pct=break_even_spread_pct,
            min_required_spread_pct=min_required_spread_pct,
            recommendation=recommendation,
            risk_factors=risk_factors,
        )


# ========================
# UTILITY FUNCTIONS
# ========================

def get_enhanced_fee_calculator(
    min_profit_margin_pct: float = 2.5,
) -> EnhancedFeeCalculator:
    """Factory function for EnhancedFeeCalculator."""
    return EnhancedFeeCalculator(min_profit_margin_pct=min_profit_margin_pct)


if __name__ == "__main__":
    # Test the enhanced fee calculator
    calc = get_enhanced_fee_calculator()

    # Example analysis
    analysis = calc.analyze_profitability(
        market_a_price=0.52,
        market_b_price=0.48,
        market_a_orderbook=None,  # Would use real orderbook
        market_b_orderbook=None,
        position_size_usd=100.0,
        market_a_platform="polymarket",
        market_b_platform="kalshi",
    )

    print("\n" + "=" * 70)
    print("PROFITABILITY ANALYSIS")
    print("=" * 70)
    print(f"Gross Spread: ${analysis.gross_spread:.2f} ({analysis.gross_spread_pct:.2f}%)")
    print(f"Platform Fees: ${analysis.transaction_costs.platform_fees_usd:.2f}")
    print(f"Gas Costs: ${analysis.transaction_costs.gas_costs_usd:.2f}")
    print(f"Slippage Costs: ${analysis.transaction_costs.slippage_costs_usd:.2f}")
    print(f"Total Costs: ${analysis.transaction_costs.total_costs_usd:.2f} ({analysis.transaction_costs.total_costs_pct:.2f}%)")
    print(f"Net Profit: ${analysis.net_profit_usd:.2f} ({analysis.net_profit_pct:.2f}%)")
    print(f"Break-Even Spread: {analysis.break_even_spread_pct:.2f}%")
    print(f"Min Required Spread: {analysis.min_required_spread_pct:.2f}%")
    print(f"Status: {analysis.recommendation}")
    if analysis.risk_factors:
        print(f"Risk Factors: {', '.join(analysis.risk_factors)}")
    print("=" * 70)

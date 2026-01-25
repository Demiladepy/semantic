"""
Profit Calculator - Calculate actual profit after all fees and slippage

This module ensures the bot only executes trades that are profitable after:
- Polymarket fees (2% on winnings)
- Kalshi fees (taker fees based on contract price)
- Polygon gas costs (converted to USD)
- Order book slippage (L2/L3 depth analysis)
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import requests
from dotenv import load_dotenv

try:
    from web3 import Web3
except ImportError:
    logging.warning("web3 not installed")

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# ENUMS & DATA STRUCTURES
# ========================


class FeeType(Enum):
    """Fee calculation strategy."""
    MAKER = 0.00  # 0% maker fee (typically)
    TAKER = 0.02  # 2% taker fee (Polymarket)
    KALSHI_TAKER = 0.015  # Kalshi taker fee


@dataclass
class PriceLevel:
    """Represents an order book price level (L2/L3 data)."""
    price: float
    quantity: float


@dataclass
class TradeOpportunity:
    """Complete trade opportunity with profit analysis."""
    market_a_id: str
    market_a_price: float
    market_a_source: str  # "polymarket" or "kalshi"
    market_b_id: str
    market_b_price: float
    market_b_source: str
    position_size: float  # USD amount
    gross_spread: float  # Raw price difference
    gas_cost_usd: float
    fee_cost_usd: float
    net_profit_usd: float
    net_profit_pct: float
    is_profitable: bool
    reasoning: str


class ProfitCalculator:
    """
    Calculate actual profitability including all costs.
    """

    def __init__(self, min_profit_margin: float = 0.015):
        """
        Args:
            min_profit_margin: Minimum net profit required (default 1.5%)
        """
        self.min_profit_margin = min_profit_margin
        self.w3 = None

        if os.getenv("POLYGON_RPC_URL"):
            try:
                self.w3 = Web3(Web3.HTTPProvider(os.getenv("POLYGON_RPC_URL")))
            except Exception as e:
                logger.warning(f"Failed to initialize Web3: {e}")

    # ========================
    # GAS COST CALCULATION
    # ========================

    def get_polygon_gas_cost_usd(
        self, gas_units: int = 100000, gas_price_gwei: Optional[float] = None
    ) -> float:
        """
        Calculate gas cost in USD for a Polygon transaction.

        Args:
            gas_units: Estimated gas units (typical order: 100k-200k)
            gas_price_gwei: Current gas price in Gwei (fetches if not provided)

        Returns:
            Gas cost in USD
        """
        if gas_price_gwei is None:
            gas_price_gwei = self._fetch_polygon_gas_price_gwei()

        if gas_price_gwei is None:
            logger.warning("Could not fetch gas price, estimating 30 Gwei")
            gas_price_gwei = 30.0

        # Convert: gas_units * gas_price_gwei = cost in Gwei = cost_wei / 1e9
        # MATIC price assumed ~1 USD (simplification; could fetch from oracle)
        matic_price_usd = 1.0  # Typically around 0.8-1.2 USD

        cost_wei = gas_units * (gas_price_gwei * 1e9)
        cost_matic = cost_wei / 1e18
        cost_usd = cost_matic * matic_price_usd

        return cost_usd

    def _fetch_polygon_gas_price_gwei(self) -> Optional[float]:
        """Fetch current Polygon gas price from RPC."""
        if not self.w3 or not self.w3.is_connected():
            return None

        try:
            gas_price_wei = self.w3.eth.gas_price
            gas_price_gwei = self.w3.from_wei(gas_price_wei, "gwei")
            return float(gas_price_gwei)
        except Exception as e:
            logger.warning(f"Failed to fetch gas price: {e}")
            return None

    # ========================
    # FEE CALCULATION
    # ========================

    def calculate_polymarket_fees(
        self, position_size_usd: float, fee_rate: float = FeeType.TAKER.value
    ) -> float:
        """
        Calculate Polymarket taker fees (2% on winnings realized).

        Args:
            position_size_usd: Amount trading (USD)
            fee_rate: Fee percentage (default 2% taker)

        Returns:
            Fee amount in USD
        """
        return position_size_usd * fee_rate

    def calculate_kalshi_fees(
        self, position_size_usd: float, contract_price: float
    ) -> float:
        """
        Calculate Kalshi taker fees (varies by contract price).

        Args:
            position_size_usd: Amount trading (USD)
            contract_price: Current contract price (0-100 cents)

        Returns:
            Fee amount in USD
        """
        # Kalshi fee structure: higher fees near 50 cents, lower at extremes
        if contract_price < 20 or contract_price > 80:
            fee_rate = 0.005  # 0.5% at extremes
        else:
            fee_rate = 0.015  # 1.5% in the middle

        return position_size_usd * fee_rate

    # ========================
    # SLIPPAGE CALCULATION
    # ========================

    def calculate_slippage_cost(
        self,
        order_book: list[PriceLevel],
        order_size_usd: float,
        side: str = "BUY",
    ) -> Tuple[float, float]:
        """
        Calculate slippage cost by analyzing order book depth.

        Args:
            order_book: List of PriceLevel objects sorted by price
            order_size_usd: Size of order to execute
            side: "BUY" or "SELL"

        Returns:
            (average_execution_price, slippage_cost_usd)
        """
        if not order_book:
            logger.warning("Empty order book, assuming 0.5% slippage")
            return 1.0, order_size_usd * 0.005

        total_filled = 0.0
        weighted_price = 0.0

        for level in order_book:
            if total_filled >= order_size_usd:
                break

            fill_amount = min(level.quantity, order_size_usd - total_filled)
            weighted_price += level.price * fill_amount
            total_filled += fill_amount

        avg_price = weighted_price / total_filled if total_filled > 0 else 1.0

        # Slippage = (Avg Price - Best Price) * Quantity
        best_price = order_book[0].price if order_book else 1.0
        slippage_pct = abs(avg_price - best_price) / best_price if best_price != 0 else 0.0

        slippage_usd = order_size_usd * slippage_pct

        return avg_price, slippage_usd

    # ========================
    # ARBITRAGE PROFITABILITY CHECK
    # ========================

    def check_arbitrage_profitability(
        self,
        market_a_id: str,
        market_a_price: float,
        market_a_source: str,
        market_a_orderbook: Optional[list[PriceLevel]],
        market_b_id: str,
        market_b_price: float,
        market_b_source: str,
        market_b_orderbook: Optional[list[PriceLevel]],
        position_size_usd: float = 100.0,
        gas_price_gwei: Optional[float] = None,
    ) -> TradeOpportunity:
        """
        Comprehensive profitability check for an arbitrage opportunity.

        Args:
            market_a_id, market_a_price, market_a_source: First market
            market_a_orderbook: Order book for slippage calc
            market_b_id, market_b_price, market_b_source: Second market
            market_b_orderbook: Order book for slippage calc
            position_size_usd: Size of position (default $100)
            gas_price_gwei: Current gas price (fetches if not provided)

        Returns:
            TradeOpportunity with full profitability analysis
        """
        logger.info(f"📊 Analyzing arbitrage: {market_a_source}@${market_a_price} vs {market_b_source}@${market_b_price}")

        # 1. Calculate slippage for each leg
        if market_a_orderbook:
            market_a_exec_price, market_a_slippage = self.calculate_slippage_cost(
                market_a_orderbook, position_size_usd, side="BUY"
            )
        else:
            market_a_exec_price = market_a_price
            market_a_slippage = position_size_usd * 0.005  # Conservative 0.5%

        if market_b_orderbook:
            market_b_exec_price, market_b_slippage = self.calculate_slippage_cost(
                market_b_orderbook, position_size_usd, side="SELL"
            )
        else:
            market_b_exec_price = market_b_price
            market_b_slippage = position_size_usd * 0.005

        # 2. Calculate fees
        polymarket_fees = (
            self.calculate_polymarket_fees(position_size_usd)
            if market_a_source.lower() == "polymarket"
            else 0.0
        )
        kalshi_fees = (
            self.calculate_kalshi_fees(position_size_usd, market_a_price * 100)
            if market_a_source.lower() == "kalshi"
            else 0.0
        )

        total_fees = polymarket_fees + kalshi_fees
        total_slippage = market_a_slippage + market_b_slippage

        # 3. Calculate gas costs
        gas_cost = self.get_polygon_gas_cost_usd(
            gas_units=150000, gas_price_gwei=gas_price_gwei
        )

        # 4. Calculate gross and net profit
        gross_spread = abs(market_a_price - market_b_price) * position_size_usd

        total_costs = total_fees + total_slippage + gas_cost
        net_profit = gross_spread - total_costs
        net_profit_pct = (net_profit / position_size_usd) if position_size_usd > 0 else 0.0

        is_profitable = net_profit_pct >= self.min_profit_margin

        # Build reasoning
        reasoning = f"Gross: ${gross_spread:.2f} | Fees: ${total_fees:.2f} | Slippage: ${total_slippage:.2f} | Gas: ${gas_cost:.2f} | Net: ${net_profit:.2f}"

        logger.info(reasoning)
        logger.info(f"{'✅ PROFITABLE' if is_profitable else '❌ NOT PROFITABLE'} ({net_profit_pct*100:.2f}%)")

        return TradeOpportunity(
            market_a_id=market_a_id,
            market_a_price=market_a_price,
            market_a_source=market_a_source,
            market_b_id=market_b_id,
            market_b_price=market_b_price,
            market_b_source=market_b_source,
            position_size=position_size_usd,
            gross_spread=gross_spread,
            gas_cost_usd=gas_cost,
            fee_cost_usd=total_fees,
            net_profit_usd=net_profit,
            net_profit_pct=net_profit_pct,
            is_profitable=is_profitable,
            reasoning=reasoning,
        )


# ========================
# UTILITY FUNCTIONS
# ========================


def get_profit_calculator(min_profit_margin: float = 0.015) -> ProfitCalculator:
    """Factory function for ProfitCalculator."""
    return ProfitCalculator(min_profit_margin=min_profit_margin)


if __name__ == "__main__":
    # Test the profit calculator
    calc = ProfitCalculator()

    # Example: Analyze an arbitrage opportunity
    opportunity = calc.check_arbitrage_profitability(
        market_a_id="market_1",
        market_a_price=0.52,
        market_a_source="polymarket",
        market_a_orderbook=[
            PriceLevel(price=0.52, quantity=500),
            PriceLevel(price=0.51, quantity=1000),
        ],
        market_b_id="market_2",
        market_b_price=0.48,
        market_b_source="kalshi",
        market_b_orderbook=[
            PriceLevel(price=0.48, quantity=400),
            PriceLevel(price=0.47, quantity=800),
        ],
        position_size_usd=100.0,
    )

    print("\n" + "=" * 70)
    print("PROFIT ANALYSIS")
    print("=" * 70)
    print(f"Gross Spread: ${opportunity.gross_spread:.2f}")
    print(f"Gas Cost: ${opportunity.gas_cost_usd:.2f}")
    print(f"Fees: ${opportunity.fee_cost_usd:.2f}")
    print(f"Net Profit: ${opportunity.net_profit_usd:.2f} ({opportunity.net_profit_pct*100:.2f}%)")
    print(f"Status: {'✅ PROFITABLE' if opportunity.is_profitable else '❌ NOT PROFITABLE'}")
    print("=" * 70)

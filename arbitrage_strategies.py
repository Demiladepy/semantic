"""
Market Rebalancing & Combinatorial Arbitrage Strategies

Implements both strategies identified in research:
1. Market Rebalancing (simpler, 99.76% of profits):
   - Detect when YES + NO ≠ $1.00 within single market
   - Execute split/merge strategies

2. Combinatorial Arbitrage (complex, 0.24% of profits but higher per-trade):
   - Identify logically dependent market pairs
   - Example: "Trump wins presidency" vs. "Republican Senate majority"
   - Cross-market position management
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import numpy as np

from clob_orderbook_client import OrderbookSnapshot
from enhanced_nli_engine import EnhancedNLIEngine, RelationshipType, RelationshipAnalysis
from enhanced_fee_calculator import EnhancedFeeCalculator, ProfitabilityAnalysis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Types of arbitrage strategies."""
    MARKET_REBALANCING = "market_rebalancing"
    COMBINATORIAL = "combinatorial"


class RebalancingType(Enum):
    """Types of market rebalancing."""
    SPLIT = "split"  # Buy YES + NO when sum < 1.00
    MERGE = "merge"  # Sell YES + NO when sum > 1.00


@dataclass
class RebalancingOpportunity:
    """Market rebalancing opportunity."""
    market_id: str
    yes_price: float
    no_price: float
    price_sum: float
    deviation: float  # How far from $1.00
    rebalancing_type: RebalancingType
    expected_profit_pct: float
    orderbook: Optional[OrderbookSnapshot]
    timestamp: float


@dataclass
class CombinatorialOpportunity:
    """Combinatorial arbitrage opportunity."""
    market_a_id: str
    market_b_id: str
    market_a_price: float
    market_b_price: float
    relationship: RelationshipAnalysis
    expected_profit_pct: float
    market_a_orderbook: Optional[OrderbookSnapshot]
    market_b_orderbook: Optional[OrderbookSnapshot]
    timestamp: float


@dataclass
class StrategyExecution:
    """Strategy execution result."""
    strategy_type: StrategyType
    opportunity_id: str
    status: str  # "executed", "rejected", "pending"
    profit_usd: Optional[float]
    profit_pct: Optional[float]
    execution_time_ms: float
    details: Dict[str, Any]


class MarketRebalancingStrategy:
    """
    Market Rebalancing Strategy (99.76% of profits).
    
    Detects when YES + NO ≠ $1.00 within a single market and executes
    split/merge strategies to capture the spread.
    """

    def __init__(
        self,
        min_deviation_pct: float = 0.5,  # Minimum 0.5% deviation from $1.00
        fee_calculator: Optional[EnhancedFeeCalculator] = None,
    ):
        """
        Initialize market rebalancing strategy.
        
        Args:
            min_deviation_pct: Minimum deviation percentage to trigger
            fee_calculator: Fee calculator for profitability analysis
        """
        self.min_deviation_pct = min_deviation_pct
        self.fee_calculator = fee_calculator or EnhancedFeeCalculator()
        logger.info(f"✅ Market Rebalancing Strategy initialized (min deviation: {min_deviation_pct}%)")

    def detect_opportunity(
        self,
        market_id: str,
        yes_price: float,
        no_price: float,
        orderbook: Optional[OrderbookSnapshot] = None,
    ) -> Optional[RebalancingOpportunity]:
        """
        Detect rebalancing opportunity in a single market.
        
        Args:
            market_id: Market identifier
            yes_price: Current YES price
            no_price: Current NO price
            orderbook: Optional orderbook snapshot
            
        Returns:
            RebalancingOpportunity if found, None otherwise
        """
        price_sum = yes_price + no_price
        deviation = abs(price_sum - 1.0)
        deviation_pct = deviation * 100

        if deviation_pct < self.min_deviation_pct:
            return None

        # Determine rebalancing type
        if price_sum < 1.0:
            rebalancing_type = RebalancingType.SPLIT
            # Buy YES + NO at discount, sell when they converge to $1.00
            expected_profit_pct = deviation_pct
        else:
            rebalancing_type = RebalancingType.MERGE
            # Sell YES + NO at premium, buy back when they converge
            expected_profit_pct = deviation_pct

        # Check profitability after fees
        if orderbook:
            # Use fee calculator to verify profitability
            # For rebalancing, we're trading within the same market
            position_size = 100.0  # Default
            analysis = self.fee_calculator.analyze_profitability(
                market_a_price=yes_price,
                market_b_price=no_price,
                market_a_orderbook=orderbook,
                market_b_orderbook=None,  # Same market
                position_size_usd=position_size,
                market_a_platform="polymarket",
                market_b_platform="polymarket",
            )

            if not analysis.is_profitable:
                logger.debug(f"Rebalancing opportunity not profitable after fees: {deviation_pct:.2f}%")
                return None

            expected_profit_pct = analysis.net_profit_pct

        opportunity = RebalancingOpportunity(
            market_id=market_id,
            yes_price=yes_price,
            no_price=no_price,
            price_sum=price_sum,
            deviation=deviation,
            rebalancing_type=rebalancing_type,
            expected_profit_pct=expected_profit_pct,
            orderbook=orderbook,
            timestamp=datetime.now().timestamp(),
        )

        logger.info(
            f"💰 Rebalancing opportunity: {market_id} | "
            f"Type: {rebalancing_type.value} | "
            f"Deviation: {deviation_pct:.2f}% | "
            f"Expected Profit: {expected_profit_pct:.2f}%"
        )

        return opportunity

    def scan_markets(
        self,
        markets: List[Dict[str, Any]],
        orderbooks: Optional[Dict[str, OrderbookSnapshot]] = None,
    ) -> List[RebalancingOpportunity]:
        """
        Scan multiple markets for rebalancing opportunities.
        
        Args:
            markets: List of market dicts with 'id', 'yes_price', 'no_price'
            orderbooks: Optional dict mapping market_id to OrderbookSnapshot
            
        Returns:
            List of RebalancingOpportunity objects
        """
        opportunities = []

        for market in markets:
            market_id = market.get("id")
            yes_price = market.get("yes_price") or market.get("outcomes", [{}])[0].get("price", 0.5)
            no_price = market.get("no_price") or market.get("outcomes", [{}])[1].get("price", 0.5) if len(market.get("outcomes", [])) > 1 else (1.0 - yes_price)

            orderbook = orderbooks.get(market_id) if orderbooks else None

            opportunity = self.detect_opportunity(
                market_id=market_id,
                yes_price=yes_price,
                no_price=no_price,
                orderbook=orderbook,
            )

            if opportunity:
                opportunities.append(opportunity)

        logger.info(f"✅ Found {len(opportunities)} rebalancing opportunities")
        return opportunities


class CombinatorialArbitrageStrategy:
    """
    Combinatorial Arbitrage Strategy (0.24% of profits but higher per-trade).
    
    Identifies logically dependent market pairs and executes cross-market
    arbitrage positions.
    """

    def __init__(
        self,
        nli_engine: Optional[EnhancedNLIEngine] = None,
        fee_calculator: Optional[EnhancedFeeCalculator] = None,
        min_confidence: float = 0.85,
    ):
        """
        Initialize combinatorial arbitrage strategy.
        
        Args:
            nli_engine: Enhanced NLI engine for relationship detection
            fee_calculator: Fee calculator for profitability analysis
            min_confidence: Minimum confidence for relationship classification
        """
        self.nli_engine = nli_engine or EnhancedNLIEngine()
        self.fee_calculator = fee_calculator or EnhancedFeeCalculator()
        self.min_confidence = min_confidence
        logger.info(f"✅ Combinatorial Arbitrage Strategy initialized (min confidence: {min_confidence})")

    def detect_opportunity(
        self,
        market_a: Dict[str, Any],
        market_b: Dict[str, Any],
        market_a_orderbook: Optional[OrderbookSnapshot] = None,
        market_b_orderbook: Optional[OrderbookSnapshot] = None,
    ) -> Optional[CombinatorialOpportunity]:
        """
        Detect combinatorial arbitrage opportunity between two markets.
        
        Args:
            market_a: First market dict
            market_b: Second market dict
            market_a_orderbook: Optional orderbook for market A
            market_b_orderbook: Optional orderbook for market B
            
        Returns:
            CombinatorialOpportunity if found, None otherwise
        """
        # Classify relationship
        relationship = self.nli_engine.classify_relationship(market_a, market_b)

        # Check if relationship is suitable for arbitrage
        if not relationship.arbitrage_viability:
            logger.debug(
                f"Relationship not viable: {relationship.relationship_type.value} "
                f"(confidence: {relationship.confidence:.2f})"
            )
            return None

        if relationship.confidence < self.min_confidence:
            logger.debug(f"Confidence too low: {relationship.confidence:.2f}")
            return None

        # Extract prices
        market_a_price = market_a.get("price") or market_a.get("outcomes", [{}])[0].get("price", 0.5)
        market_b_price = market_b.get("price") or market_b.get("outcomes", [{}])[0].get("price", 0.5)

        # Calculate spread
        spread_pct = abs(market_a_price - market_b_price) / max(market_a_price, market_b_price) * 100

        # Check profitability
        position_size = 100.0  # Default
        analysis = self.fee_calculator.analyze_profitability(
            market_a_price=market_a_price,
            market_b_price=market_b_price,
            market_a_orderbook=market_a_orderbook,
            market_b_orderbook=market_b_orderbook,
            position_size_usd=position_size,
            market_a_platform=market_a.get("source", "polymarket"),
            market_b_platform=market_b.get("source", "polymarket"),
        )

        if not analysis.is_profitable:
            logger.debug(f"Combinatorial opportunity not profitable: {spread_pct:.2f}%")
            return None

        opportunity = CombinatorialOpportunity(
            market_a_id=market_a.get("id"),
            market_b_id=market_b.get("id"),
            market_a_price=market_a_price,
            market_b_price=market_b_price,
            relationship=relationship,
            expected_profit_pct=analysis.net_profit_pct,
            market_a_orderbook=market_a_orderbook,
            market_b_orderbook=market_b_orderbook,
            timestamp=datetime.now().timestamp(),
        )

        logger.info(
            f"🎯 Combinatorial opportunity: {market_a.get('id')} vs {market_b.get('id')} | "
            f"Relationship: {relationship.relationship_type.value} | "
            f"Spread: {spread_pct:.2f}% | "
            f"Expected Profit: {analysis.net_profit_pct:.2f}%"
        )

        return opportunity

    def scan_market_pairs(
        self,
        markets: List[Dict[str, Any]],
        orderbooks: Optional[Dict[str, OrderbookSnapshot]] = None,
    ) -> List[CombinatorialOpportunity]:
        """
        Scan market pairs for combinatorial arbitrage opportunities.
        
        Args:
            markets: List of market dicts
            orderbooks: Optional dict mapping market_id to OrderbookSnapshot
            
        Returns:
            List of CombinatorialOpportunity objects
        """
        opportunities = []

        # Cluster markets by topic first
        clusters = self.nli_engine.cluster_markets_by_topic(markets)

        # Check pairs within clusters
        for cluster in clusters:
            cluster_markets = cluster.markets
            if len(cluster_markets) < 2:
                continue

            # Pairwise comparison within cluster
            for i in range(len(cluster_markets)):
                for j in range(i + 1, len(cluster_markets)):
                    market_a = cluster_markets[i]
                    market_b = cluster_markets[j]

                    market_a_orderbook = orderbooks.get(market_a.get("id")) if orderbooks else None
                    market_b_orderbook = orderbooks.get(market_b.get("id")) if orderbooks else None

                    opportunity = self.detect_opportunity(
                        market_a=market_a,
                        market_b=market_b,
                        market_a_orderbook=market_a_orderbook,
                        market_b_orderbook=market_b_orderbook,
                    )

                    if opportunity:
                        opportunities.append(opportunity)

        logger.info(f"✅ Found {len(opportunities)} combinatorial opportunities")
        return opportunities


class ArbitrageStrategyManager:
    """
    Manager for both arbitrage strategies.
    
    Coordinates between market rebalancing and combinatorial arbitrage,
    prioritizing opportunities based on expected profit and risk.
    """

    def __init__(
        self,
        rebalancing_strategy: Optional[MarketRebalancingStrategy] = None,
        combinatorial_strategy: Optional[CombinatorialArbitrageStrategy] = None,
    ):
        """
        Initialize strategy manager.
        
        Args:
            rebalancing_strategy: Market rebalancing strategy instance
            combinatorial_strategy: Combinatorial arbitrage strategy instance
        """
        self.rebalancing_strategy = rebalancing_strategy or MarketRebalancingStrategy()
        self.combinatorial_strategy = combinatorial_strategy or CombinatorialArbitrageStrategy()
        logger.info("✅ Arbitrage Strategy Manager initialized")

    def scan_all_opportunities(
        self,
        markets: List[Dict[str, Any]],
        orderbooks: Optional[Dict[str, OrderbookSnapshot]] = None,
    ) -> Dict[str, List[Any]]:
        """
        Scan for all types of arbitrage opportunities.
        
        Args:
            markets: List of market dicts
            orderbooks: Optional dict mapping market_id to OrderbookSnapshot
            
        Returns:
            Dict with 'rebalancing' and 'combinatorial' opportunity lists
        """
        logger.info(f"🔍 Scanning {len(markets)} markets for arbitrage opportunities...")

        # Market rebalancing opportunities
        rebalancing_ops = self.rebalancing_strategy.scan_markets(markets, orderbooks)

        # Combinatorial opportunities
        combinatorial_ops = self.combinatorial_strategy.scan_market_pairs(markets, orderbooks)

        logger.info(
            f"✅ Scan complete: {len(rebalancing_ops)} rebalancing, "
            f"{len(combinatorial_ops)} combinatorial opportunities"
        )

        return {
            "rebalancing": rebalancing_ops,
            "combinatorial": combinatorial_ops,
        }

    def prioritize_opportunities(
        self,
        opportunities: Dict[str, List[Any]],
        max_opportunities: int = 10,
    ) -> List[Tuple[str, Any, float]]:
        """
        Prioritize opportunities by expected profit.
        
        Args:
            opportunities: Dict with opportunity lists
            max_opportunities: Maximum number to return
            
        Returns:
            List of (strategy_type, opportunity, expected_profit_pct) tuples, sorted by profit
        """
        prioritized = []

        # Add rebalancing opportunities
        for opp in opportunities.get("rebalancing", []):
            prioritized.append(("rebalancing", opp, opp.expected_profit_pct))

        # Add combinatorial opportunities
        for opp in opportunities.get("combinatorial", []):
            prioritized.append(("combinatorial", opp, opp.expected_profit_pct))

        # Sort by expected profit (descending)
        prioritized.sort(key=lambda x: x[2], reverse=True)

        return prioritized[:max_opportunities]


# ========================
# UTILITY FUNCTIONS
# ========================

def get_arbitrage_strategy_manager() -> ArbitrageStrategyManager:
    """Factory function for ArbitrageStrategyManager."""
    return ArbitrageStrategyManager()


if __name__ == "__main__":
    # Test the strategies
    manager = get_arbitrage_strategy_manager()

    # Mock markets for testing
    mock_markets = [
        {
            "id": "m1",
            "question": "Trump wins 2024",
            "yes_price": 0.48,
            "no_price": 0.49,  # Sum = 0.97 (rebalancing opportunity)
            "source": "polymarket",
        },
        {
            "id": "m2",
            "question": "Republican wins 2024",
            "price": 0.52,
            "source": "polymarket",
        },
    ]

    opportunities = manager.scan_all_opportunities(mock_markets)
    print(f"\nRebalancing opportunities: {len(opportunities['rebalancing'])}")
    print(f"Combinatorial opportunities: {len(opportunities['combinatorial'])}")

    prioritized = manager.prioritize_opportunities(opportunities)
    print(f"\nTop opportunities:")
    for strategy_type, opp, profit_pct in prioritized[:5]:
        print(f"  {strategy_type}: {profit_pct:.2f}% expected profit")

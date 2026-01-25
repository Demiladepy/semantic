"""
Production-Ready Arbitrage Finder

Full integration of:
- Market data ingestion (Polymarket + Kalshi)
- Semantic clustering and NLI analysis
- Semantic drift detection
- Profitability calculations
- Atomic execution
- Comprehensive logging

This is the main bot orchestration layer.
"""

import asyncio
import csv
import logging
from datetime import datetime
import os
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv

from market_client import PolymarketAdapter, KalshiAdapter, MarketAggregator
from nli_engine import NLIEngine
from profit_calculator import get_profit_calculator, PriceLevel
from execution_bot import get_execution_bot
from wallet_manager import get_wallet_manager

load_dotenv()
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ========================
# CONFIGURATION
# ========================

MIN_SPREAD_PCT = float(os.getenv("MIN_PROFIT_MARGIN", 0.015)) * 100  # 1.5%
MIN_NLI_CONFIDENCE = 0.80
MIN_RESOLUTION_RISK = 0.3  # Higher = riskier
SIMULATION_MODE = os.getenv("TRADING_MODE", "simulation") == "simulation"

# ========================
# TRADE LOGGING
# ========================


def log_opportunity(opportunity: Dict[str, Any]):
    """Log found arbitrage opportunity to CSV."""
    file_exists = os.path.isfile("arbitrage_opportunities.csv")
    with open("arbitrage_opportunities.csv", "a", newline="") as csvfile:
        fieldnames = [
            "timestamp",
            "market_a_id",
            "market_a_source",
            "market_a_price",
            "market_b_id",
            "market_b_source",
            "market_b_price",
            "spread_pct",
            "nli_confidence",
            "net_profit_usd",
            "net_profit_pct",
            "status",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": datetime.now().isoformat(),
                "market_a_id": opportunity.get("market_a_id", ""),
                "market_a_source": opportunity.get("market_a_source", ""),
                "market_a_price": opportunity.get("market_a_price", 0),
                "market_b_id": opportunity.get("market_b_id", ""),
                "market_b_source": opportunity.get("market_b_source", ""),
                "market_b_price": opportunity.get("market_b_price", 0),
                "spread_pct": opportunity.get("spread_pct", 0),
                "nli_confidence": opportunity.get("nli_confidence", 0),
                "net_profit_usd": opportunity.get("net_profit_usd", 0),
                "net_profit_pct": opportunity.get("net_profit_pct", 0),
                "status": opportunity.get("status", "found"),
            }
        )

    logger.info(f"✅ Logged opportunity to arbitrage_opportunities.csv")


def log_execution(execution_result: Dict[str, Any]):
    """Log trade execution result to CSV."""
    file_exists = os.path.isfile("execution_log.csv")
    with open("execution_log.csv", "a", newline="") as csvfile:
        fieldnames = [
            "timestamp",
            "market_a_id",
            "market_b_id",
            "execution_status",
            "net_pnl",
            "execution_time",
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(
            {
                "timestamp": datetime.now().isoformat(),
                "market_a_id": execution_result.get("market_a_id", ""),
                "market_b_id": execution_result.get("market_b_id", ""),
                "execution_status": execution_result.get("status", "unknown"),
                "net_pnl": execution_result.get("net_pnl", 0),
                "execution_time": execution_result.get("time_ms", 0),
            }
        )


# ========================
# MAIN ARBITRAGE FINDER
# ========================


class ArbitrageFinder:
    """
    Production-ready arbitrage finder with full integration.
    """

    def __init__(self):
        logger.info("=" * 70)
        logger.info("🤖 Initializing Arbitrage Finder")
        logger.info("=" * 70)

        # Initialize components
        self.aggregator = MarketAggregator(
            [PolymarketAdapter(), KalshiAdapter()]
        )
        self.nli_engine = NLIEngine()
        self.profit_calc = get_profit_calculator()
        self.execution_bot = get_execution_bot() if not SIMULATION_MODE else None
        self.wallet = get_wallet_manager()

        self.opportunities_found = 0
        self.opportunities_executed = 0

        logger.info(f"  Mode: {'SIMULATION' if SIMULATION_MODE else 'LIVE TRADING'}")
        logger.info(f"  Min Spread: {MIN_SPREAD_PCT:.2f}%")
        logger.info(f"  Min NLI Confidence: {MIN_NLI_CONFIDENCE:.2f}")

    async def run_scan(self) -> Dict[str, Any]:
        """
        Run a complete arbitrage scan.

        Returns:
            Summary dict with opportunities found and executed
        """
        logger.info("\n" + "=" * 70)
        logger.info("🔍 ARBITRAGE SCAN STARTED")
        logger.info("=" * 70)

        # Step 1: Ingest market data
        logger.info("\n[Step 1/5] Ingesting market data...")
        markets = self.aggregator.get_all_markets()
        logger.info(f"✅ Ingested {len(markets)} active markets")

        if len(markets) < 2:
            logger.warning("Not enough markets for arbitrage")
            return {"status": "failed", "reason": "Insufficient markets"}

        # Step 2: Semantic clustering
        logger.info("\n[Step 2/5] Semantic clustering...")
        clusters = self.nli_engine.cluster_questions(markets)
        logger.info(f"✅ Found {len(clusters)} semantic clusters")

        # Step 3: Analyze clusters for arbitrage
        logger.info("\n[Step 3/5] Analyzing clusters for arbitrage...")
        opportunities = []

        for cluster_idx, cluster in enumerate(clusters):
            if len(cluster) < 2:
                continue

            logger.info(f"\n  Cluster {cluster_idx + 1} (Size: {len(cluster)})")

            # Pairwise comparison within cluster
            for i in range(len(cluster)):
                for j in range(i + 1, len(cluster)):
                    m_a = cluster[i]
                    m_b = cluster[j]

                    opportunity = await self._analyze_market_pair(m_a, m_b)

                    if opportunity:
                        opportunities.append(opportunity)
                        self.opportunities_found += 1

        logger.info(f"\n✅ Found {len(opportunities)} potential opportunities")

        # Step 4: Profitability check and filtering
        logger.info("\n[Step 4/5] Profitability filtering...")
        profitable_ops = [op for op in opportunities if op.get("is_profitable")]
        logger.info(f"✅ {len(profitable_ops)} opportunities are profitable")

        # Step 5: Execution (if not in simulation)
        logger.info("\n[Step 5/5] Execution phase...")
        if not SIMULATION_MODE and self.execution_bot and profitable_ops:
            for opp in profitable_ops[:1]:  # Execute first opportunity as demo
                logger.info(f"\n  Executing opportunity: {opp['market_a_id']} vs {opp['market_b_id']}")
                execution_result = await self.execution_bot.execute_arbitrage(opp)
                if execution_result.get("status") == "success":
                    self.opportunities_executed += 1
                    log_execution(execution_result)
        else:
            logger.info("  Simulation mode - no execution")

        logger.info("\n" + "=" * 70)
        logger.info("✅ SCAN COMPLETE")
        logger.info(f"  Opportunities Found: {self.opportunities_found}")
        logger.info(f"  Opportunities Executed: {self.opportunities_executed}")
        logger.info("=" * 70)

        return {
            "status": "success",
            "opportunities_found": len(opportunities),
            "profitable_opportunities": len(profitable_ops),
            "executed": self.opportunities_executed,
        }

    async def _analyze_market_pair(
        self, market_a: Dict, market_b: Dict
    ) -> Optional[Dict]:
        """
        Analyze a pair of markets for arbitrage opportunity.

        Returns:
            Opportunity dict or None
        """
        # 1. Check entailment
        entailment = self.nli_engine.check_entailment(market_a, market_b)

        if not entailment:
            return None

        relationship = entailment.get("relationship", "none")
        direction = entailment.get("direction", "none")
        confidence = entailment.get("confidence", 0)

        if confidence < MIN_NLI_CONFIDENCE:
            logger.debug(f"    Low NLI confidence: {confidence:.2f}")
            return None

        # 2. Semantic drift check
        drift = self.nli_engine.check_semantic_drift(market_a, market_b)

        if drift.risk_score > 0.6:
            logger.warning(
                f"    High semantic drift risk: {drift.overall_risk.value}"
            )
            return None

        # 3. Extract prices
        price_a = market_a.get("outcomes", [{}])[0].get("price", 0.5)
        price_b = market_b.get("outcomes", [{}])[0].get("price", 0.5)
        spread_pct = abs(price_a - price_b) / max(price_a, price_b) * 100

        if spread_pct < MIN_SPREAD_PCT:
            return None

        # 4. Profitability check
        profit_analysis = self.profit_calc.check_arbitrage_profitability(
            market_a_id=market_a.get("id", ""),
            market_a_price=price_a,
            market_a_source=market_a.get("source", ""),
            market_a_orderbook=None,  # Would fetch from API
            market_b_id=market_b.get("id", ""),
            market_b_price=price_b,
            market_b_source=market_b.get("source", ""),
            market_b_orderbook=None,
            position_size_usd=100.0,
        )

        if not profit_analysis.is_profitable:
            return None

        # Build opportunity dict
        opportunity = {
            "market_a_id": market_a.get("id"),
            "market_a_source": market_a.get("source"),
            "market_a_price": price_a,
            "market_b_id": market_b.get("id"),
            "market_b_source": market_b.get("source"),
            "market_b_price": price_b,
            "relationship": relationship,
            "direction": direction,
            "nli_confidence": confidence,
            "spread_pct": spread_pct,
            "drift_risk": drift.overall_risk.value,
            "net_profit_usd": profit_analysis.net_profit_usd,
            "net_profit_pct": profit_analysis.net_profit_pct,
            "is_profitable": profit_analysis.is_profitable,
        }

        logger.info(
            f"    ✅ OPPORTUNITY FOUND: {spread_pct:.2f}% spread, "
            f"${profit_analysis.net_profit_usd:.2f} profit"
        )

        log_opportunity(opportunity)
        return opportunity


# ========================
# MAIN ENTRY POINT
# ========================


async def main():
    """Main entry point."""
    finder = ArbitrageFinder()

    # Run continuous scans
    try:
        while True:
            result = await finder.run_scan()
            await asyncio.sleep(30)  # Scan every 30 seconds

    except KeyboardInterrupt:
        logger.info("\n🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    # For testing, run a single scan
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        asyncio.run(main())
    else:
        # Single scan
        finder = ArbitrageFinder()
        asyncio.run(finder.run_scan())


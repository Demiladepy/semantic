"""
PNP Exchange Enhanced Integration

Privacy-preserving arbitrage execution with:
- Collateral optimization (ELUSIV/LIGHT/PNP selection)
- Multi-market creation from detected opportunities
- Agent-to-agent arbitrage support
- Real-time event handling
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

from pnp_sdk_adapter import PNPSDKAdapter
from pnp_infra.collateral_manager import CollateralManager
from pnp_infra.market_factory import MarketFactory
from pnp_infra.privacy_wrapper import PrivacyWrapper

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrivacyLevel(Enum):
    """Privacy levels for PNP markets."""
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    ANONYMOUS = "ANONYMOUS"


class CollateralToken(Enum):
    """Available collateral tokens."""
    ELUSIV = "ELUSIV"  # Highest privacy
    LIGHT = "LIGHT"    # Medium privacy
    PNP = "PNP"        # Standard privacy


@dataclass
class ArbitrageOpportunity:
    """Arbitrage opportunity for PNP market creation."""
    question: str
    outcomes: List[str]
    expected_profit_usd: float
    capital_required: float
    privacy_required: PrivacyLevel
    timestamp: datetime


class PNPEnhancedArbitrage:
    """
    Enhanced PNP Exchange integration for privacy-preserving arbitrage.
    
    Features:
    - Automatic collateral token selection
    - Privacy-preserving market creation
    - Multi-market arbitrage strategies
    - Agent-to-agent arbitrage support
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        use_realtime: bool = True,
    ):
        """
        Initialize enhanced PNP arbitrage system.
        
        Args:
            api_key: PNP API key (when available)
            use_realtime: Use real-time SDK features
        """
        self.api_key = api_key or os.getenv("PNP_API_KEY")
        self.use_realtime = use_realtime

        # Initialize adapters
        self.adapter = PNPSDKAdapter(
            api_key=self.api_key,
            use_realtime=use_realtime,
        )

        self.collateral_manager = CollateralManager()
        self.market_factory = MarketFactory()
        self.privacy_wrapper = PrivacyWrapper()

        logger.info("✅ PNP Enhanced Arbitrage initialized")

    def select_collateral_token(
        self,
        opportunity: ArbitrageOpportunity,
    ) -> CollateralToken:
        """
        Select optimal collateral token based on opportunity characteristics.
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Selected collateral token
        """
        # Decision logic:
        # - High profit (>$1000) → ELUSIV (highest privacy)
        # - Medium profit ($500-$1000) → LIGHT
        # - Low profit (<$500) → PNP (standard)

        if opportunity.expected_profit_usd > 1000:
            return CollateralToken.ELUSIV
        elif opportunity.expected_profit_usd > 500:
            return CollateralToken.LIGHT
        else:
            return CollateralToken.PNP

    async def create_privacy_market(
        self,
        opportunity: ArbitrageOpportunity,
    ) -> Dict[str, Any]:
        """
        Create privacy-preserving market from arbitrage opportunity.
        
        Args:
            opportunity: Arbitrage opportunity
            
        Returns:
            Market creation result
        """
        # Select collateral token
        collateral_token = self.select_collateral_token(opportunity)

        # Determine privacy level
        privacy_level = opportunity.privacy_required.value

        # Create market parameters
        market_params = {
            'question': opportunity.question,
            'outcomes': opportunity.outcomes,
            'collateral_token': collateral_token.value,
            'collateral_amount': opportunity.capital_required,
            'privacy_level': privacy_level,
            'resolution_criteria': 'Based on UMA Optimistic Oracle',
        }

        logger.info(
            f"📊 Creating privacy market: {opportunity.question[:50]}... "
            f"(Token: {collateral_token.value}, Privacy: {privacy_level})"
        )

        # Create market via adapter
        if self.use_realtime:
            await self.adapter.connect_realtime()

        market_result = self.adapter.create_market(market_params)

        # Subscribe to market updates
        if self.use_realtime and market_result.get('market_id'):
            await self.adapter.subscribe_market(market_result['market_id'])

        logger.info(f"✅ Market created: {market_result.get('market_id')}")

        return market_result

    async def create_multi_market_strategy(
        self,
        opportunities: List[ArbitrageOpportunity],
    ) -> List[Dict[str, Any]]:
        """
        Create multiple linked markets for complex arbitrage strategies.
        
        Args:
            opportunities: List of related opportunities
            
        Returns:
            List of created markets
        """
        created_markets = []

        for i, opp in enumerate(opportunities):
            # First market uses standard creation
            if i == 0:
                market = await self.create_privacy_market(opp)
                created_markets.append(market)
            else:
                # Subsequent markets can reference parent market
                parent_market_id = created_markets[0].get('market_id')

                market_params = {
                    'question': opp.question,
                    'outcomes': opp.outcomes,
                    'collateral_token': self.select_collateral_token(opp).value,
                    'collateral_amount': opp.capital_required,
                    'parent_market': parent_market_id,
                    'privacy_level': opp.privacy_required.value,
                }

                market = self.adapter.create_market(market_params)
                created_markets.append(market)

        logger.info(f"✅ Created {len(created_markets)} linked markets")

        return created_markets

    async def execute_private_arbitrage(
        self,
        opportunity: ArbitrageOpportunity,
        polymarket_price: float,
        kalshi_price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Execute privacy-preserving arbitrage across platforms.
        
        Args:
            opportunity: Arbitrage opportunity
            polymarket_price: Price on Polymarket
            kalshi_price: Price on Kalshi (if applicable)
            
        Returns:
            Execution result
        """
        # Create PNP market
        pnp_market = await self.create_privacy_market(opportunity)

        # Determine optimal position
        # Buy on cheaper platform, create PNP market, sell on expensive platform
        if kalshi_price and kalshi_price < polymarket_price:
            buy_platform = "Kalshi"
            buy_price = kalshi_price
            sell_platform = "Polymarket"
            sell_price = polymarket_price
        else:
            buy_platform = "Polymarket"
            buy_price = polymarket_price
            sell_platform = "Kalshi" if kalshi_price else "PNP"
            sell_price = kalshi_price or 0.5

        execution_result = {
            'pnp_market_id': pnp_market.get('market_id'),
            'buy_platform': buy_platform,
            'buy_price': buy_price,
            'sell_platform': sell_platform,
            'sell_price': sell_price,
            'expected_profit': opportunity.expected_profit_usd,
            'collateral_token': self.select_collateral_token(opportunity).value,
            'timestamp': datetime.now().isoformat(),
        }

        logger.info(
            f"💰 Private arbitrage execution: "
            f"Buy {buy_platform} @ {buy_price:.4f}, "
            f"Sell {sell_platform} @ {sell_price:.4f}"
        )

        return execution_result

    async def agent_to_agent_arbitrage(
        self,
        opportunity: ArbitrageOpportunity,
        competing_agents: List[str],
    ) -> Dict[str, Any]:
        """
        Execute agent-to-agent arbitrage where multiple AI agents compete.
        
        Args:
            opportunity: Arbitrage opportunity
            competing_agents: List of competing agent addresses/IDs
            
        Returns:
            Execution result
        """
        # Create market that allows multiple agents to participate
        market_params = {
            'question': opportunity.question,
            'outcomes': opportunity.outcomes,
            'collateral_token': CollateralToken.ELUSIV.value,  # Highest privacy for agent competition
            'collateral_amount': opportunity.capital_required,
            'privacy_level': PrivacyLevel.ANONYMOUS.value,
            'agent_competition': True,
            'competing_agents': competing_agents,
        }

        market = self.adapter.create_market(market_params)

        logger.info(
            f"🤖 Agent-to-agent arbitrage market created: {market.get('market_id')} "
            f"({len(competing_agents)} competing agents)"
        )

        return {
            'market_id': market.get('market_id'),
            'competing_agents': competing_agents,
            'competition_type': 'agent_to_agent',
            'timestamp': datetime.now().isoformat(),
        }

    def optimize_collateral_allocation(
        self,
        opportunities: List[ArbitrageOpportunity],
        total_capital: float,
    ) -> Dict[CollateralToken, float]:
        """
        Optimize collateral allocation across tokens.
        
        Args:
            opportunities: List of opportunities
            total_capital: Total capital available
            
        Returns:
            Dict mapping token to allocated amount
        """
        allocation = {
            CollateralToken.ELUSIV: 0.0,
            CollateralToken.LIGHT: 0.0,
            CollateralToken.PNP: 0.0,
        }

        # Allocate based on opportunity sizes and privacy requirements
        for opp in opportunities:
            token = self.select_collateral_token(opp)
            allocation[token] += opp.capital_required

        # Normalize to total capital
        total_allocated = sum(allocation.values())
        if total_allocated > total_capital:
            scale = total_capital / total_allocated
            allocation = {k: v * scale for k, v in allocation.items()}

        logger.info(
            f"📊 Collateral allocation optimized: "
            f"ELUSIV=${allocation[CollateralToken.ELUSIV]:,.2f}, "
            f"LIGHT=${allocation[CollateralToken.LIGHT]:,.2f}, "
            f"PNP=${allocation[CollateralToken.PNP]:,.2f}"
        )

        return allocation


# ========================
# UTILITY FUNCTIONS
# ========================

def get_pnp_enhanced(
    api_key: Optional[str] = None,
    use_realtime: bool = True,
) -> PNPEnhancedArbitrage:
    """Factory function for PNPEnhancedArbitrage."""
    return PNPEnhancedArbitrage(
        api_key=api_key,
        use_realtime=use_realtime,
    )


if __name__ == "__main__":
    # Test PNP enhanced integration
    pnp = get_pnp_enhanced(use_realtime=False)
    
    # Test opportunity
    test_opp = ArbitrageOpportunity(
        question="Will Bitcoin reach $100k by Dec 2025?",
        outcomes=["Yes", "No"],
        expected_profit_usd=750.0,
        capital_required=500.0,
        privacy_required=PrivacyLevel.PRIVATE,
        timestamp=datetime.now(),
    )
    
    # Test collateral selection
    token = pnp.select_collateral_token(test_opp)
    print(f"✅ Selected collateral token: {token.value}")
    
    # Test allocation optimization
    opportunities = [test_opp]
    allocation = pnp.optimize_collateral_allocation(opportunities, 1000.0)
    print(f"✅ Collateral allocation: {allocation}")

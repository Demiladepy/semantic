"""
PNP Exchange Integration Example
Demonstrates how to use the PNP Market Client for arbitrage detection.
"""

import os
import sys
from dotenv import load_dotenv
from pnp_market_client import PNPMarketClient
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main example function."""
    load_dotenv()
    
    # Initialize PNP client
    rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
    private_key = os.getenv('POLYGON_PRIVATE_KEY')  # Reusing for now
    
    logger.info("Initializing PNP Market Client...")
    client = PNPMarketClient(rpc_url=rpc_url, private_key=private_key)
    
    # Example 1: Fetch all markets
    logger.info("\n=== Fetching All Markets ===")
    markets = client.fetch_all_markets()
    logger.info(f"Found {len(markets)} markets on PNP Exchange")
    
    if markets:
        # Display first 3 markets
        for i, market in enumerate(markets[:3], 1):
            logger.info(f"\nMarket {i}:")
            logger.info(f"  Question: {market.get('question')}")
            logger.info(f"  Address: {market.get('address')}")
            logger.info(f"  End Time: {market.get('endTime')}")
            logger.info(f"  Resolved: {market.get('resolved')}")
    
    # Example 2: Get market prices
    if markets:
        logger.info("\n=== Fetching Market Prices ===")
        first_market = markets[0]
        market_address = first_market.get('address')
        
        price_data = client.get_market_price(market_address)
        
        if price_data:
            logger.info(f"\nMarket: {first_market.get('question')}")
            logger.info(f"YES Price: ${price_data['yesPrice']:.4f} ({price_data['yesMultiplier']:.2f}x)")
            logger.info(f"NO Price: ${price_data['noPrice']:.4f} ({price_data['noMultiplier']:.2f}x)")
            logger.info(f"Total Liquidity: ${price_data['marketReserves']:.2f}")
            logger.info(f"YES Supply: {price_data['yesTokenSupply']:.2f}")
            logger.info(f"NO Supply: {price_data['noTokenSupply']:.2f}")
    
    # Example 3: Format market for arbitrage engine
    if markets:
        logger.info("\n=== Formatting Market for Arbitrage ===")
        formatted = client.format_market_for_arbitrage(markets[0])
        
        if formatted:
            logger.info(f"Platform: {formatted['platform']}")
            logger.info(f"Market ID: {formatted['market_id']}")
            logger.info(f"Question: {formatted['question']}")
            logger.info(f"YES Price: ${formatted['yes_price']:.4f}")
            logger.info(f"NO Price: ${formatted['no_price']:.4f}")
            logger.info(f"Liquidity: ${formatted['liquidity']:.2f}")
    
    # Example 4: Simulate arbitrage detection
    logger.info("\n=== Simulating Arbitrage Detection ===")
    
    # Mock external market from Polymarket
    external_markets = [
        {
            'platform': 'polymarket',
            'question': markets[0].get('question') if markets else 'Test question',
            'yes_price': 0.65,  # Different price for arbitrage
            'no_price': 0.35,
            'liquidity': 50000
        }
    ]
    
    opportunities = client.find_arbitrage_opportunities(
        external_markets,
        min_profit_margin=0.01  # 1% minimum
    )
    
    logger.info(f"Found {len(opportunities)} arbitrage opportunities")
    
    for i, opp in enumerate(opportunities, 1):
        logger.info(f"\nOpportunity {i}:")
        logger.info(f"  Side: {opp['side']}")
        logger.info(f"  Buy on: {opp['buy_platform']} @ ${opp['buy_price']:.4f}")
        logger.info(f"  Sell on: {opp['sell_platform']} @ ${opp['sell_price']:.4f}")
        logger.info(f"  Spread: ${opp['spread']:.4f}")
        logger.info(f"  Profit Margin: {opp['profit_pct']:.2f}%")
    
    # Example 5: Get settlement criteria
    if markets:
        logger.info("\n=== Checking Settlement Criteria ===")
        market_address = markets[0].get('address')
        
        criteria = client.get_settlement_criteria(market_address)
        
        if criteria:
            logger.info(f"Resolvable: {criteria.get('resolvable')}")
            logger.info(f"Winning Token: {criteria.get('winning_token_id', 'N/A')}")
            if criteria.get('reasoning'):
                logger.info(f"Reasoning: {criteria.get('reasoning')}")
    
    logger.info("\n=== Example Complete ===")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nExample interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error running example: {e}", exc_info=True)
        sys.exit(1)

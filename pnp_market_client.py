"""
PNP Exchange Market Client
Integrates PNP Exchange (Solana prediction markets) with the semantic arbitrage engine.
"""

import json
import subprocess
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PNPMarketClient:
    """Client for interacting with PNP Exchange prediction markets on Solana."""
    
    def __init__(
        self,
        rpc_url: str = "https://api.mainnet-beta.solana.com",
        private_key: Optional[str] = None
    ):
        """
        Initialize PNP Market Client.
        
        Args:
            rpc_url: Solana RPC endpoint URL
            private_key: Base58 encoded private key (optional for read-only operations)
        """
        self.rpc_url = rpc_url
        self.private_key = private_key
        self.node_script_dir = os.path.join(os.path.dirname(__file__), 'pnp_infra')
        
        # Ensure the Node.js bridge scripts exist
        self._ensure_node_scripts()
    
    def _ensure_node_scripts(self):
        """Ensure Node.js bridge scripts are available."""
        os.makedirs(self.node_script_dir, exist_ok=True)
    
    def _run_node_script(self, script_name: str, args: List[str] = None) -> Dict:
        """
        Execute a Node.js script and return the result.
        
        Args:
            script_name: Name of the script to run
            args: Additional arguments to pass to the script
            
        Returns:
            Parsed JSON result from the script
        """
        script_path = os.path.join(self.node_script_dir, script_name)
        
        if not os.path.exists(script_path):
            raise FileNotFoundError(f"Node.js script not found: {script_path}")
        
        cmd = ['node', script_path]
        if args:
            cmd.extend(args)
        
        # Set environment variables
        env = os.environ.copy()
        env['RPC_URL'] = self.rpc_url
        if self.private_key:
            env['PNP_PRIVATE_KEY'] = self.private_key
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=env,
                timeout=60
            )
            
            if result.returncode != 0:
                logger.error(f"Node script error: {result.stderr}")
                raise RuntimeError(f"Node script failed: {result.stderr}")
            
            # Parse JSON output
            return json.loads(result.stdout)
        
        except subprocess.TimeoutExpired:
            logger.error(f"Node script timeout: {script_name}")
            raise TimeoutError(f"Script execution timeout: {script_name}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON output: {result.stdout}")
            raise ValueError(f"Invalid JSON response: {e}")
    
    def fetch_all_markets(self) -> List[Dict]:
        """
        Fetch all available markets from PNP Exchange.
        
        Returns:
            List of market dictionaries with details
        """
        try:
            result = self._run_node_script('fetch_markets.js')
            return result.get('markets', [])
        except Exception as e:
            logger.error(f"Error fetching markets: {e}")
            return []
    
    def fetch_market_addresses(self) -> List[str]:
        """
        Fetch all market addresses from the proxy server.
        
        Returns:
            List of market address strings
        """
        try:
            result = self._run_node_script('fetch_market_addresses.js')
            return result.get('addresses', [])
        except Exception as e:
            logger.error(f"Error fetching market addresses: {e}")
            return []
    
    def get_market_info(self, market_address: str) -> Optional[Dict]:
        """
        Get detailed information about a specific market.
        
        Args:
            market_address: The market's public key
            
        Returns:
            Market information dictionary or None
        """
        try:
            result = self._run_node_script('get_market_info.js', [market_address])
            return result.get('market')
        except Exception as e:
            logger.error(f"Error fetching market info for {market_address}: {e}")
            return None
    
    def get_market_price(self, market_address: str) -> Optional[Dict]:
        """
        Get real-time price data for a V2 AMM market.
        
        Args:
            market_address: The market's public key
            
        Returns:
            Price data with YES/NO prices and multipliers
        """
        try:
            result = self._run_node_script('get_market_price.js', [market_address])
            return result.get('priceData')
        except Exception as e:
            logger.error(f"Error fetching market price for {market_address}: {e}")
            return None
    
    def create_market(
        self,
        question: str,
        initial_liquidity_usdc: float,
        days_until_end: int = 30,
        market_type: str = "v2_amm"
    ) -> Optional[Dict]:
        """
        Create a new prediction market.
        
        Args:
            question: Market question
            initial_liquidity_usdc: Initial liquidity in USDC
            days_until_end: Number of days until market ends
            market_type: Type of market ("v2_amm" or "p2p")
            
        Returns:
            Market creation result with address and signature
        """
        if not self.private_key:
            raise ValueError("Private key required for market creation")
        
        try:
            # Convert USDC to base units (6 decimals)
            liquidity_base = int(initial_liquidity_usdc * 1_000_000)
            
            result = self._run_node_script('create_market.js', [
                question,
                str(liquidity_base),
                str(days_until_end),
                market_type
            ])
            
            return result.get('market')
        except Exception as e:
            logger.error(f"Error creating market: {e}")
            return None
    
    def buy_tokens(
        self,
        market_address: str,
        side: str,
        amount_usdc: float
    ) -> Optional[Dict]:
        """
        Buy YES or NO tokens in a market.
        
        Args:
            market_address: The market's public key
            side: "YES" or "NO"
            amount_usdc: Amount in USDC to spend
            
        Returns:
            Trade result with signature and tokens received
        """
        if not self.private_key:
            raise ValueError("Private key required for trading")
        
        try:
            # Convert USDC to base units
            amount_base = int(amount_usdc * 1_000_000)
            
            result = self._run_node_script('buy_tokens.js', [
                market_address,
                side.upper(),
                str(amount_base)
            ])
            
            return result.get('trade')
        except Exception as e:
            logger.error(f"Error buying tokens: {e}")
            return None
    
    def sell_tokens(
        self,
        market_address: str,
        side: str,
        token_amount: float
    ) -> Optional[Dict]:
        """
        Sell YES or NO tokens in a market.
        
        Args:
            market_address: The market's public key
            side: "YES" or "NO"
            token_amount: Amount of tokens to sell
            
        Returns:
            Trade result with signature and USDC received
        """
        if not self.private_key:
            raise ValueError("Private key required for trading")
        
        try:
            # Convert to base units
            amount_base = int(token_amount * 1_000_000)
            
            result = self._run_node_script('sell_tokens.js', [
                market_address,
                side.upper(),
                str(amount_base)
            ])
            
            return result.get('trade')
        except Exception as e:
            logger.error(f"Error selling tokens: {e}")
            return None
    
    def redeem_position(self, market_address: str) -> Optional[Dict]:
        """
        Redeem winning position in a resolved market.
        
        Args:
            market_address: The market's public key
            
        Returns:
            Redemption result with signature
        """
        if not self.private_key:
            raise ValueError("Private key required for redemption")
        
        try:
            result = self._run_node_script('redeem_position.js', [market_address])
            return result.get('redemption')
        except Exception as e:
            logger.error(f"Error redeeming position: {e}")
            return None
    
    def get_settlement_criteria(self, market_address: str) -> Optional[Dict]:
        """
        Get settlement criteria from the proxy server.
        
        Args:
            market_address: The market's public key
            
        Returns:
            Settlement criteria with resolvable status
        """
        try:
            result = self._run_node_script('get_settlement_criteria.js', [market_address])
            return result.get('criteria')
        except Exception as e:
            logger.error(f"Error fetching settlement criteria: {e}")
            return None
    
    def format_market_for_arbitrage(self, market_data: Dict) -> Dict:
        """
        Format PNP market data for the arbitrage engine.
        
        Args:
            market_data: Raw market data from PNP
            
        Returns:
            Formatted market data compatible with arbitrage engine
        """
        try:
            price_data = self.get_market_price(market_data.get('address'))
            
            if not price_data:
                return None
            
            return {
                'platform': 'pnp',
                'market_id': market_data.get('address'),
                'question': market_data.get('question', ''),
                'yes_price': price_data.get('yesPrice', 0),
                'no_price': price_data.get('noPrice', 0),
                'yes_multiplier': price_data.get('yesMultiplier', 0),
                'no_multiplier': price_data.get('noMultiplier', 0),
                'liquidity': price_data.get('marketReserves', 0),
                'end_time': market_data.get('endTime'),
                'resolved': market_data.get('resolved', False),
                'resolvable': market_data.get('resolvable', True),
                'volume': market_data.get('volume', 0),
                'last_updated': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error formatting market data: {e}")
            return None
    
    def find_arbitrage_opportunities(
        self,
        external_markets: List[Dict],
        min_profit_margin: float = 0.02
    ) -> List[Dict]:
        """
        Find arbitrage opportunities between PNP and external markets.
        
        Args:
            external_markets: List of markets from other platforms (Polymarket, Kalshi)
            min_profit_margin: Minimum profit margin to consider (default 2%)
            
        Returns:
            List of arbitrage opportunities
        """
        opportunities = []
        pnp_markets = self.fetch_all_markets()
        
        for pnp_market in pnp_markets:
            pnp_formatted = self.format_market_for_arbitrage(pnp_market)
            
            if not pnp_formatted:
                continue
            
            for ext_market in external_markets:
                # Simple question matching (can be enhanced with NLI)
                if self._questions_match(
                    pnp_formatted['question'],
                    ext_market.get('question', '')
                ):
                    # Calculate potential arbitrage
                    arb = self._calculate_arbitrage(pnp_formatted, ext_market)
                    
                    if arb and arb['profit_margin'] >= min_profit_margin:
                        opportunities.append(arb)
        
        return opportunities
    
    def _questions_match(self, q1: str, q2: str) -> bool:
        """Simple question matching (can be enhanced with NLI engine)."""
        # Normalize and compare
        q1_norm = q1.lower().strip()
        q2_norm = q2.lower().strip()
        
        # Simple similarity check
        return q1_norm == q2_norm or q1_norm in q2_norm or q2_norm in q1_norm
    
    def _calculate_arbitrage(self, market1: Dict, market2: Dict) -> Optional[Dict]:
        """
        Calculate arbitrage opportunity between two markets.
        
        Args:
            market1: First market data
            market2: Second market data
            
        Returns:
            Arbitrage opportunity details or None
        """
        try:
            # Buy YES on cheaper market, sell YES on expensive market
            yes_spread = market2['yes_price'] - market1['yes_price']
            no_spread = market2['no_price'] - market1['no_price']
            
            # Find best opportunity
            if abs(yes_spread) > abs(no_spread):
                side = 'YES'
                spread = yes_spread
                buy_platform = market1['platform'] if yes_spread > 0 else market2['platform']
                sell_platform = market2['platform'] if yes_spread > 0 else market1['platform']
                buy_price = min(market1['yes_price'], market2['yes_price'])
                sell_price = max(market1['yes_price'], market2['yes_price'])
            else:
                side = 'NO'
                spread = no_spread
                buy_platform = market1['platform'] if no_spread > 0 else market2['platform']
                sell_platform = market2['platform'] if no_spread > 0 else market1['platform']
                buy_price = min(market1['no_price'], market2['no_price'])
                sell_price = max(market1['no_price'], market2['no_price'])
            
            # Calculate profit margin (accounting for fees ~2%)
            fee_estimate = 0.02
            profit_margin = (spread / buy_price) - fee_estimate
            
            if profit_margin <= 0:
                return None
            
            return {
                'market1': market1,
                'market2': market2,
                'side': side,
                'buy_platform': buy_platform,
                'sell_platform': sell_platform,
                'buy_price': buy_price,
                'sell_price': sell_price,
                'spread': spread,
                'profit_margin': profit_margin,
                'profit_pct': profit_margin * 100,
                'detected_at': datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Error calculating arbitrage: {e}")
            return None


# Example usage
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize client
    rpc_url = os.getenv('SOLANA_RPC_URL', 'https://api.mainnet-beta.solana.com')
    private_key = os.getenv('POLYGON_PRIVATE_KEY')  # Using Polygon key for now
    
    client = PNPMarketClient(rpc_url=rpc_url, private_key=private_key)
    
    # Fetch markets
    print("Fetching PNP markets...")
    markets = client.fetch_all_markets()
    print(f"Found {len(markets)} markets")
    
    # Get price for first market
    if markets:
        first_market = markets[0]
        print(f"\nMarket: {first_market.get('question')}")
        
        price_data = client.get_market_price(first_market.get('address'))
        if price_data:
            print(f"YES Price: ${price_data['yesPrice']:.4f} ({price_data['yesMultiplier']:.2f}x)")
            print(f"NO Price: ${price_data['noPrice']:.4f} ({price_data['noMultiplier']:.2f}x)")

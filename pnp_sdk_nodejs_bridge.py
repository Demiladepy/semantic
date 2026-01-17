"""
PNP SDK Node.js Bridge

Python wrapper for the npm pnp-sdk package that allows Python code
to interact with the TypeScript/JavaScript PNP SDK via Node.js.
"""

import subprocess
import json
import os
import tempfile
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PNPSDKNodeJSBridge:
    """
    Python bridge to the npm pnp-sdk package.
    
    This class allows Python code to use the official PNP SDK (TypeScript/JavaScript)
    by executing Node.js scripts that use the npm package.
    """
    
    def __init__(self, 
                 api_key: Optional[str] = None,
                 node_path: Optional[str] = None,
                 sdk_path: Optional[str] = None):
        """
        Initialize the Node.js bridge.
        
        Args:
            api_key: PNP Exchange API key
            node_path: Path to Node.js executable (defaults to 'node')
            sdk_path: Path to directory with pnp-sdk installed (defaults to plugin-polymarket)
        """
        self.api_key = api_key or os.getenv('PNP_API_KEY') or os.getenv('PNP_EXCHANGE_API_KEY')
        self.node_path = node_path or 'node'
        self.sdk_path = sdk_path or Path(__file__).parent / 'plugin-polymarket'
        
        # Check if Node.js is available
        self._check_nodejs()
        
        # Check if pnp-sdk is installed
        self._check_sdk_installed()
    
    def _check_nodejs(self):
        """Check if Node.js is available."""
        try:
            result = subprocess.run(
                [self.node_path, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"Node.js available: {result.stdout.strip()}")
            else:
                raise RuntimeError("Node.js not found or not working")
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            raise RuntimeError(
                f"Node.js not available. Please install Node.js: {e}\n"
                "Visit https://nodejs.org/ to install."
            )
    
    def _check_sdk_installed(self):
        """Check if pnp-sdk is installed in the plugin directory."""
        package_json = self.sdk_path / 'package.json'
        if not package_json.exists():
            logger.warning(f"package.json not found at {package_json}")
            return False
        
        # Check if pnp-sdk is in dependencies
        try:
            with open(package_json, 'r') as f:
                pkg_data = json.load(f)
                deps = {**pkg_data.get('dependencies', {}), **pkg_data.get('devDependencies', {})}
                if 'pnp-sdk' in deps:
                    logger.info("pnp-sdk found in package.json")
                    return True
                else:
                    logger.warning("pnp-sdk not found in package.json dependencies")
                    return False
        except Exception as e:
            logger.error(f"Error checking package.json: {e}")
            return False
    
    def _run_node_script(self, script: str, input_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a Node.js script and return the result.
        
        Args:
            script: JavaScript code to execute
            input_data: Optional data to pass to the script
        
        Returns:
            Dictionary with the result
        """
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            script_path = f.name
            # Wrap script with error handling and JSON output
            full_script = f"""
const {{ PNPClient }} = require('pnp-sdk');

async function main() {{
    try {{
        const input = {json.dumps(input_data or {})};
        const apiKey = process.env.PNP_API_KEY || '{self.api_key or ''}';
        
        const client = new PNPClient({{
            apiKey: apiKey
        }});
        
        {script}
        
        // Output result as JSON
        if (typeof result !== 'undefined') {{
            console.log(JSON.stringify({{ success: true, data: result }}));
        }} else {{
            console.log(JSON.stringify({{ success: true }}));
        }}
    }} catch (error) {{
        console.error(JSON.stringify({{
            success: false,
            error: error.message,
            stack: error.stack
        }}));
        process.exit(1);
    }}
}}

main();
"""
            f.write(full_script)
        
        try:
            # Change to SDK directory and run
            env = os.environ.copy()
            if self.api_key:
                env['PNP_API_KEY'] = self.api_key
            
            result = subprocess.run(
                [self.node_path, script_path],
                cwd=str(self.sdk_path),
                capture_output=True,
                text=True,
                timeout=30,
                env=env
            )
            
            if result.returncode != 0:
                error_output = result.stderr or result.stdout
                try:
                    error_data = json.loads(error_output)
                    raise RuntimeError(f"Node.js error: {error_data.get('error', error_output)}")
                except json.JSONDecodeError:
                    raise RuntimeError(f"Node.js execution failed: {error_output}")
            
            # Parse JSON output
            output_lines = [line for line in result.stdout.split('\n') if line.strip()]
            if not output_lines:
                raise RuntimeError("No output from Node.js script")
            
            # Try to parse the last line as JSON (the result)
            try:
                result_data = json.loads(output_lines[-1])
                if not result_data.get('success'):
                    raise RuntimeError(f"Script failed: {result_data.get('error', 'Unknown error')}")
                return result_data.get('data', {})
            except json.JSONDecodeError:
                # If last line isn't JSON, try to find JSON in output
                for line in reversed(output_lines):
                    try:
                        result_data = json.loads(line)
                        if result_data.get('success'):
                            return result_data.get('data', {})
                    except json.JSONDecodeError:
                        continue
                raise RuntimeError(f"Could not parse JSON output: {result.stdout}")
        
        finally:
            # Clean up temp file
            try:
                os.unlink(script_path)
            except:
                pass
    
    def create_market(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a prediction market using the npm pnp-sdk.
        
        Args:
            params: Market creation parameters
        
        Returns:
            Market creation result
        """
        script = f"""
        const result = await client.createMarket({{
            question: {json.dumps(params.get('question'))},
            outcomes: {json.dumps(params.get('outcomes', []))},
            collateralToken: {json.dumps(params.get('collateral_token'))},
            collateralAmount: {params.get('collateral_amount', 0)},
            endDate: {json.dumps(params.get('end_date'))},
            resolutionCriteria: {json.dumps(params.get('resolution_criteria', ''))}
        }});
        """
        return self._run_node_script(script, params)
    
    def place_order(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Place an order using the npm pnp-sdk.
        
        Args:
            params: Order parameters
        
        Returns:
            Order placement result
        """
        script = f"""
        const result = await client.placeOrder({{
            marketId: {json.dumps(params.get('market_id'))},
            outcome: {json.dumps(params.get('outcome'))},
            side: {json.dumps(params.get('side', 'buy'))},
            amount: {params.get('amount', 0)},
            price: {params.get('price', 0.5)}
        }});
        """
        return self._run_node_script(script, params)
    
    def settle_market(self, market_id: str, outcome: str, resolver: Optional[str] = None) -> Dict[str, Any]:
        """
        Settle a market using the npm pnp-sdk.
        
        Args:
            market_id: Market identifier
            outcome: Winning outcome
            resolver: Optional resolver identifier
        
        Returns:
            Settlement result
        """
        script = f"""
        const result = await client.settleMarket(
            {json.dumps(market_id)},
            {json.dumps(outcome)},
            {json.dumps(resolver) if resolver else 'undefined'}
        );
        """
        return self._run_node_script(script, {'market_id': market_id, 'outcome': outcome, 'resolver': resolver})
    
    def get_market(self, market_id: str) -> Optional[Dict[str, Any]]:
        """Get market details."""
        script = f"""
        const result = await client.getMarket({json.dumps(market_id)});
        """
        try:
            return self._run_node_script(script, {'market_id': market_id})
        except RuntimeError:
            return None
    
    def list_markets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List markets."""
        script = f"""
        const result = await client.listMarkets({json.dumps(status) if status else 'undefined'});
        """
        result = self._run_node_script(script, {'status': status})
        return result if isinstance(result, list) else []


def get_nodejs_sdk(api_key: Optional[str] = None) -> PNPSDKNodeJSBridge:
    """
    Get a Node.js bridge instance for the npm pnp-sdk.
    
    Args:
        api_key: PNP Exchange API key
    
    Returns:
        PNPSDKNodeJSBridge instance
    """
    return PNPSDKNodeJSBridge(api_key=api_key)


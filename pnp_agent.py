"""
PNP AI Agent

An AI agent that autonomously creates prediction markets on PNP Exchange
using privacy-focused tokens as collateral. Integrates with OpenAI to generate
market questions based on real-time data or user prompts.
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

try:
    import openai
except ImportError:
    print("Warning: openai package not installed. Install with: pip install openai")
    openai = None

try:
    from pnp_sdk_adapter import get_sdk, PNPSDKAdapter
    SDK_ADAPTER_AVAILABLE = True
except ImportError:
    from pnp_sdk_mock import get_sdk
    SDK_ADAPTER_AVAILABLE = False
    PNPSDKAdapter = None

# Load environment variables
load_dotenv()


class PNPAgent:
    """
    AI agent for creating and managing prediction markets on PNP Exchange.
    
    Features:
    - Generates market questions using OpenAI
    - Handles privacy-focused token collateral
    - Creates markets via PNP SDK
    - Can process news headlines or user prompts
    """
    
    # Privacy-focused tokens supported as collateral
    PRIVACY_TOKENS = {
        'ELUSIV': {
            'name': 'Elusiv',
            'description': 'Privacy-focused token for private transactions',
            'default_amount': 100.0
        },
        'LIGHT': {
            'name': 'Light Protocol',
            'description': 'Privacy token for confidential transactions',
            'default_amount': 100.0
        },
        'PNP': {
            'name': 'PNP Token',
            'description': 'Native PNP Exchange token',
            'default_amount': 100.0
        }
    }
    
    def __init__(self, 
                 openai_api_key: Optional[str] = None,
                 default_collateral_token: str = 'ELUSIV',
                 agent_id: Optional[str] = None,
                 use_realtime: bool = False,
                 pnp_api_key: Optional[str] = None):
        """
        Initialize the PNP Agent.
        
        Args:
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            default_collateral_token: Default privacy token to use (ELUSIV, LIGHT, or PNP)
            agent_id: Unique identifier for this agent instance
            use_realtime: Whether to enable real-time WebSocket features
            pnp_api_key: PNP Exchange API key (for real SDK when available)
        """
        self.agent_id = agent_id or f"PNP-Agent-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Use adapter if available, otherwise fall back to mock
        if SDK_ADAPTER_AVAILABLE and use_realtime:
            from pnp_sdk_adapter import PNPSDKAdapter
            self.sdk = PNPSDKAdapter(api_key=pnp_api_key, use_realtime=True)
            self.realtime_enabled = True
        else:
            self.sdk = get_sdk()
            self.realtime_enabled = False
        
        self.default_collateral_token = default_collateral_token.upper()
        
        # Validate collateral token
        if self.default_collateral_token not in self.PRIVACY_TOKENS:
            raise ValueError(
                f"Invalid collateral token: {default_collateral_token}. "
                f"Supported tokens: {list(self.PRIVACY_TOKENS.keys())}"
            )
        
        # Initialize OpenAI client
        self.openai_client = None
        if openai:
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
            else:
                print("Warning: OpenAI API key not found. Market question generation will be limited.")
        else:
            print("Warning: OpenAI package not available. Market question generation will be limited.")
    
    def generate_market_question(self, 
                                 prompt: str,
                                 context: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a market question and outcomes using OpenAI.
        
        Args:
            prompt: User prompt or news headline to create a market from
            context: Optional additional context (e.g., news article text)
        
        Returns:
            Dictionary with:
                - question: str - The market question
                - outcomes: List[str] - Possible outcomes
                - resolution_criteria: str - How to resolve the market
        """
        if not self.openai_client:
            # Fallback: simple rule-based generation
            return self._fallback_question_generation(prompt)
        
        try:
            system_prompt = """You are an expert at creating prediction market questions. 
Given a prompt or news headline, create a clear, binary prediction market question with:
1. A specific, measurable question
2. Two outcomes: "Yes" and "No"
3. Clear resolution criteria

Format your response as JSON with keys: "question", "outcomes", "resolution_criteria".
The question should be answerable with Yes/No and have a clear resolution date or event."""
            
            user_prompt = f"""Create a prediction market question from this prompt:

{prompt}

{f'Additional context: {context}' if context else ''}

Return a JSON object with:
- "question": A clear Yes/No question
- "outcomes": ["Yes", "No"]
- "resolution_criteria": Specific criteria for how this market will be resolved"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",  # Using cost-effective model
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize
            if 'question' not in result:
                raise ValueError("OpenAI response missing 'question' field")
            if 'outcomes' not in result:
                result['outcomes'] = ['Yes', 'No']
            if 'resolution_criteria' not in result:
                result['resolution_criteria'] = 'To be determined by market resolution mechanism'
            
            return result
            
        except Exception as e:
            print(f"Error generating market question with OpenAI: {e}")
            print("Falling back to rule-based generation...")
            return self._fallback_question_generation(prompt)
    
    def _fallback_question_generation(self, prompt: str) -> Dict[str, Any]:
        """Fallback question generation when OpenAI is unavailable."""
        # Simple rule-based question generation
        prompt_lower = prompt.lower()
        
        # Try to extract a question or create one
        if '?' in prompt:
            question = prompt.strip()
        else:
            # Convert statement to question
            question = f"Will {prompt}?"
        
        return {
            'question': question,
            'outcomes': ['Yes', 'No'],
            'resolution_criteria': 'To be determined by market resolution mechanism'
        }
    
    def create_market_from_prompt(self,
                                  prompt: str,
                                  collateral_token: Optional[str] = None,
                                  collateral_amount: Optional[float] = None,
                                  context: Optional[str] = None,
                                  end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a prediction market from a user prompt or news headline.
        
        Args:
            prompt: User prompt or news headline
            collateral_token: Privacy token to use (defaults to agent's default)
            collateral_amount: Amount of collateral (defaults to token's default)
            context: Optional additional context
            end_date: Optional ISO format end date (defaults to 30 days from now)
        
        Returns:
            Dictionary with market creation result from SDK
        """
        # Generate market question
        market_data = self.generate_market_question(prompt, context)
        
        # Determine collateral token
        token = (collateral_token or self.default_collateral_token).upper()
        if token not in self.PRIVACY_TOKENS:
            token = self.default_collateral_token
        
        # Determine collateral amount
        amount = collateral_amount
        if amount is None:
            amount = self.PRIVACY_TOKENS[token]['default_amount']
        
        # Set end date
        if not end_date:
            end_date = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        # Create market via SDK
        market_params = {
            'question': market_data['question'],
            'outcomes': market_data['outcomes'],
            'collateral_token': token,
            'collateral_amount': amount,
            'end_date': end_date,
            'resolution_criteria': market_data.get('resolution_criteria', ''),
            'creator': self.agent_id
        }
        
        result = self.sdk.create_market(market_params)
        
        print(f"\n[PNP Agent] Market created successfully!")
        print(f"  Agent ID: {self.agent_id}")
        print(f"  Market ID: {result['market_id']}")
        print(f"  Question: {market_data['question']}")
        print(f"  Collateral: {amount} {token}")
        
        return {
            **result,
            'question': market_data['question'],
            'outcomes': market_data['outcomes'],
            'collateral_token': token,
            'collateral_amount': amount
        }
    
    def create_custom_market(self,
                            question: str,
                            outcomes: List[str],
                            collateral_token: Optional[str] = None,
                            collateral_amount: Optional[float] = None,
                            resolution_criteria: Optional[str] = None,
                            end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a market with custom question and outcomes.
        
        Args:
            question: Market question
            outcomes: List of outcome strings
            collateral_token: Privacy token to use
            collateral_amount: Amount of collateral
            resolution_criteria: How to resolve the market
            end_date: Optional ISO format end date
        
        Returns:
            Dictionary with market creation result
        """
        token = (collateral_token or self.default_collateral_token).upper()
        if token not in self.PRIVACY_TOKENS:
            token = self.default_collateral_token
        
        amount = collateral_amount
        if amount is None:
            amount = self.PRIVACY_TOKENS[token]['default_amount']
        
        if not end_date:
            end_date = (datetime.utcnow() + timedelta(days=30)).isoformat() + 'Z'
        
        market_params = {
            'question': question,
            'outcomes': outcomes,
            'collateral_token': token,
            'collateral_amount': amount,
            'end_date': end_date,
            'resolution_criteria': resolution_criteria or '',
            'creator': self.agent_id
        }
        
        result = self.sdk.create_market(market_params)
        
        print(f"\n[PNP Agent] Custom market created!")
        print(f"  Market ID: {result['market_id']}")
        print(f"  Question: {question}")
        print(f"  Outcomes: {', '.join(outcomes)}")
        
        return {
            **result,
            'question': question,
            'outcomes': outcomes,
            'collateral_token': token,
            'collateral_amount': amount
        }
    
    def list_created_markets(self) -> List[Dict[str, Any]]:
        """List all markets created by this agent."""
        all_markets = self.sdk.list_markets()
        agent_markets = [m for m in all_markets if m.get('creator') == self.agent_id]
        return agent_markets
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about this agent."""
        markets = self.list_created_markets()
        return {
            'agent_id': self.agent_id,
            'default_collateral_token': self.default_collateral_token,
            'markets_created': len(markets),
            'openai_available': self.openai_client is not None,
            'supported_tokens': list(self.PRIVACY_TOKENS.keys())
        }


def main():
    """Example usage of PNPAgent."""
    print("=" * 60)
    print("PNP AI Agent - Market Creation Demo")
    print("=" * 60)
    
    # Initialize agent
    agent = PNPAgent(default_collateral_token='ELUSIV')
    
    print(f"\nAgent initialized: {agent.agent_id}")
    print(f"Default collateral token: {agent.default_collateral_token}")
    print(f"OpenAI available: {agent.openai_client is not None}")
    
    # Example 1: Create market from news headline
    print("\n" + "-" * 60)
    print("Example 1: Creating market from news headline")
    print("-" * 60)
    headline = "Bitcoin reaches $100,000 by end of 2024"
    result1 = agent.create_market_from_prompt(
        headline,
        collateral_token='ELUSIV',
        collateral_amount=50.0
    )
    
    # Example 2: Create custom market
    print("\n" + "-" * 60)
    print("Example 2: Creating custom market")
    print("-" * 60)
    result2 = agent.create_custom_market(
        question="Will the next US presidential election be decided by less than 1% margin?",
        outcomes=['Yes', 'No'],
        collateral_token='LIGHT',
        collateral_amount=75.0,
        resolution_criteria="Based on official election results from all states"
    )
    
    # List created markets
    print("\n" + "-" * 60)
    print("Markets created by this agent:")
    print("-" * 60)
    markets = agent.list_created_markets()
    for market in markets:
        print(f"\n  Market ID: {market['market_id']}")
        print(f"  Question: {market['question']}")
        print(f"  Status: {market['status']}")
        print(f"  Collateral: {market['collateral_amount']} {market['collateral_token']}")
    
    # Agent info
    print("\n" + "-" * 60)
    print("Agent Information:")
    print("-" * 60)
    info = agent.get_agent_info()
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()


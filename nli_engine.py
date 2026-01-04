import os
import json
import numpy as np
# from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables (API keys)
load_dotenv()

class NLIEngine:
    def __init__(self, embedding_model='text-embedding-3-small'):
        print(f"Loading embedding model: {embedding_model} (OpenAI)...")
        # self.embedder = SentenceTransformer(embedding_model) # Removed due to DLL issues
        self.embedding_model = embedding_model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        print("Model loaded.")

    def get_embeddings(self, texts):
        if not texts:
            return []
        # OpenAI handles lists of strings
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.embedding_model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            print(f"Error getting embeddings: {e}")
            raise e

    def cluster_questions(self, markets, threshold=0.75):
        """
        Groups markets based on semantic similarity of their questions.
        markets: List of dicts {'id': ..., 'question': ...}
        """
        questions = [m['question'] for m in markets]
        embeddings = self.get_embeddings(questions)
        
        clusters = []
        visited = set()
        
        if not embeddings:
            return []

        similarity_matrix = cosine_similarity(embeddings)
        
        for i in range(len(markets)):
            if i in visited:
                continue
            
            cluster = [markets[i]]
            visited.add(i)
            
            for j in range(i + 1, len(markets)):
                if j in visited:
                    continue
                
                if similarity_matrix[i][j] >= threshold:
                    cluster.append(markets[j])
                    visited.add(j)
            
            if len(cluster) > 1:
                clusters.append(cluster)
                
        return clusters

    def check_entailment(self, market_a, market_b):
        """
        Uses LLM to check logical relationship between two market questions.
        """
        prompt = f"""
        You are a super-forecasting logic engine. Analyze the relationship between these two prediction market questions.

        Market A: "{market_a['question']}"
        Market B: "{market_b['question']}"
        
        Resolution Criteria A: "{market_a.get('resolution', 'Standard Logic')}"
        Resolution Criteria B: "{market_b.get('resolution', 'Standard Logic')}"

        Determine if there is a logical entailment or contradiction.
        - Entailment: If A happens, B MUST happen.
        - Mutual Exclusivity: If A happens, B CANNOT happen.
        - None: No strict logical dependency.

        Output ONLY valid JSON:
        {{
            "relationship": "entailment" | "mutual_exclusivity" | "none",
            "direction": "A_implies_B" | "B_implies_A" | "symmetric" | "none",
            "confidence": <float 0.0-1.0>,
            "reasoning": "<brief explanation>"
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a logical reasoning engine for prediction markets."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        content = response.choices[0].message.content
        return json.loads(content)

    def check_resolution_nuance(self, market_a, market_b):
        """
        Checks if the resolution criteria of two markets are compatible for arbitrage.
        Returns: { 'compatible': bool, 'risk_score': float (0-1), 'reason': str }
        """
        # Quick check for identical strings
        res_a = market_a.get('resolution_criteria', '').strip()
        res_b = market_b.get('resolution_criteria', '').strip()
        
        if res_a == res_b and res_a:
             return {'compatible': True, 'risk_score': 0.0, 'reason': "Identical resolution rules."}

        prompt = f"""
        Compare the Resolution Criteria for these two prediction markets.
        
        Market A Resolution: "{res_a}"
        Market B Resolution: "{res_b}"
        
        Are these compatible for arbitrage? 
        - "Compatible" means they resolve based on the same underlying truth (e.g., both use AP Call or same Date).
        - "Risky" means they use different sources (e.g., Fox vs CNN) or different dates (Inauguration vs Vote Certification).
        
        Output ONLY valid JSON:
        {{
            "compatible": true | false,
            "risk_score": <float 0.0 (safe) to 1.0 (very risky)>,
            "risk_factors": ["<factor1>", "<factor2>"],
            "reason": "<brief explanation>"
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a risk manager for prediction market arbitrage."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.0
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"Error in Resolution Check: {e}")
            return {'compatible': False, 'risk_score': 1.0, 'reason': f"API Error: {e}"}

# --- Demonstration ---
if __name__ == "__main__":
    # Mock Data
    mock_markets = [
        {"id": "p1", "question": "Donald Trump wins the 2024 US Presidential Election", "resolution": "Winner of 2024 election"},
        {"id": "k1", "question": "A Republican wins the 2024 US Presidential Election", "resolution": "Party of winner"},
        {"id": "p2", "question": "Joe Biden wins the 2024 US Presidential Election", "resolution": "Winner of 2024 election"},
        {"id": "x1", "question": "Will it rain in London tomorrow?", "resolution": "Met Office"},
    ]

    engine = NLIEngine()
    
    print("\n--- Step A: Semantic Clustering ---")
    clusters = engine.cluster_questions(mock_markets)
    for idx, cluster in enumerate(clusters):
        print(f"Cluster {idx+1}: {[m['question'] for m in cluster]}")

    print("\n--- Step B: NLI Analysis ---")
    # For demo, take the first cluster and compare the first two items
    if clusters:
        c = clusters[0]
        if len(c) >= 2:
            m1, m2 = c[0], c[1]
            print(f"Comparing:\n 1) {m1['question']}\n 2) {m2['question']}")
            result = engine.check_entailment(m1, m2)
            print(f"Result: {json.dumps(result, indent=2)}")

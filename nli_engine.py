import os
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# DATA STRUCTURES
# ========================


class RiskLevel(Enum):
    """Risk level for semantic drift."""
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SemanticDriftAnalysis:
    """Analysis of semantic drift between two markets."""
    market_a_id: str
    market_b_id: str
    text_similarity: float  # 0-1
    rule_similarity: float  # 0-1
    timestamp_compatible: bool
    source_compatible: bool
    overall_risk: RiskLevel
    risk_score: float  # 0-1
    issues: List[str]
    reasoning: str


class NLIEngine:
    """
    Natural Language Inference Engine for prediction markets.
    
    Features:
    - Semantic clustering of similar markets
    - Logical entailment checking
    - Resolution criteria compatibility
    - Semantic drift detection
    """

    def __init__(self, embedding_model="text-embedding-3-small"):
        logger.info(f"Loading embedding model: {embedding_model} (OpenAI)...")
        self.embedding_model = embedding_model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("✅ NLI Engine initialized")

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts."""
        if not texts:
            return []
        try:
            response = self.client.embeddings.create(
                input=texts, model=self.embedding_model
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Error getting embeddings: {e}")
            raise e

    # ========================
    # SEMANTIC CLUSTERING
    # ========================

    def cluster_questions(self, markets: List[Dict], threshold: float = 0.75) -> List[List[Dict]]:
        """
        Groups markets based on semantic similarity of their questions.

        Args:
            markets: List of market dicts with 'id' and 'question' fields
            threshold: Similarity threshold (0-1)

        Returns:
            List of clusters, where each cluster is a list of markets
        """
        questions = [m["question"] for m in markets]
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

    # ========================
    # ENTAILMENT CHECKING
    # ========================

    def check_entailment(self, market_a: Dict, market_b: Dict) -> Optional[Dict]:
        """
        Uses LLM to check logical relationship between two market questions.

        Args:
            market_a: Market dict with 'question' and optional 'resolution'
            market_b: Market dict with 'question' and optional 'resolution'

        Returns:
            Dict with relationship, direction, confidence, reasoning
        """
        prompt = f"""
        You are a super-forecasting logic engine. Analyze the relationship between these two prediction market questions.

        Market A: "{market_a.get('question', '')}"
        Market B: "{market_b.get('question', '')}"
        
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

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a logical reasoning engine for prediction markets."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Entailment check failed: {e}")
            return None

    # ========================
    # RESOLUTION CRITERIA CHECKING
    # ========================

    def check_resolution_nuance(self, market_a: Dict, market_b: Dict) -> Dict:
        """
        Checks if the resolution criteria of two markets are compatible for arbitrage.

        Returns:
            Dict with compatible, risk_score, risk_factors, reason
        """
        res_a = market_a.get("resolution_criteria", "").strip()
        res_b = market_b.get("resolution_criteria", "").strip()

        # Quick check for identical strings
        if res_a == res_b and res_a:
            return {
                "compatible": True,
                "risk_score": 0.0,
                "reason": "Identical resolution rules.",
            }

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
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error(f"Resolution nuance check failed: {e}")
            return {
                "compatible": False,
                "risk_score": 1.0,
                "reason": f"API Error: {e}",
            }

    # ========================
    # SEMANTIC DRIFT DETECTION
    # ========================

    def check_semantic_drift(
        self, market_a: Dict, market_b: Dict
    ) -> SemanticDriftAnalysis:
        """
        Comprehensive semantic drift check.

        Analyzes:
        - Text similarity of questions
        - Rule/resolution criteria similarity
        - Timestamp compatibility
        - Information source compatibility

        Args:
            market_a: First market dict
            market_b: Second market dict

        Returns:
            SemanticDriftAnalysis with risk assessment
        """
        logger.info(
            f"🔍 Checking semantic drift: {market_a.get('id')} vs {market_b.get('id')}"
        )

        issues = []
        risk_score = 0.0

        # 1. TEXT SIMILARITY
        logger.info("  1. Analyzing question text similarity...")
        q_a = market_a.get("question", "")
        q_b = market_b.get("question", "")

        q_embeddings = self.get_embeddings([q_a, q_b])
        text_similarity = (
            float(cosine_similarity([q_embeddings[0]], [q_embeddings[1]])[0][0])
            if len(q_embeddings) == 2
            else 0.0
        )

        if text_similarity < 0.90:
            issues.append(
                f"Low question text similarity ({text_similarity:.2f}) - may have different meanings"
            )
            risk_score += 0.3

        logger.info(f"     Text similarity: {text_similarity:.2f}")

        # 2. RESOLUTION CRITERIA SIMILARITY
        logger.info("  2. Analyzing resolution criteria...")
        rule_a = market_a.get("resolution_criteria", "")
        rule_b = market_b.get("resolution_criteria", "")

        if rule_a and rule_b:
            rule_embeddings = self.get_embeddings([rule_a, rule_b])
            rule_similarity = (
                float(cosine_similarity([rule_embeddings[0]], [rule_embeddings[1]])[0][0])
                if len(rule_embeddings) == 2
                else 0.0
            )

            if rule_similarity < 0.95:
                issues.append(
                    f"Low resolution criteria similarity ({rule_similarity:.2f}) - may resolve differently"
                )
                risk_score += 0.25
        else:
            rule_similarity = 0.5
            logger.warning("     Missing resolution criteria for one or both markets")

        logger.info(f"     Rule similarity: {rule_similarity:.2f}")

        # 3. TIMESTAMP COMPATIBILITY
        logger.info("  3. Checking timestamp compatibility...")
        timestamp_compatible = True
        timestamp_a = market_a.get("resolution_date")
        timestamp_b = market_b.get("resolution_date")

        if timestamp_a and timestamp_b and timestamp_a != timestamp_b:
            issues.append(
                f"Different resolution dates: {timestamp_a} vs {timestamp_b}"
            )
            risk_score += 0.2
            timestamp_compatible = False
            logger.warning(f"     Timestamps differ: {timestamp_a} vs {timestamp_b}")
        else:
            logger.info("     Timestamps compatible ✅")

        # 4. SOURCE COMPATIBILITY
        logger.info("  4. Checking information source compatibility...")
        source_compatible = True
        source_a = market_a.get("resolution_source", "")
        source_b = market_b.get("resolution_source", "")

        if source_a and source_b and source_a.lower() != source_b.lower():
            # Check if sources are substantially different
            if not self._are_sources_equivalent(source_a, source_b):
                issues.append(f"Different resolution sources: {source_a} vs {source_b}")
                risk_score += 0.2
                source_compatible = False
                logger.warning(f"     Sources differ: {source_a} vs {source_b}")
        else:
            logger.info("     Sources compatible ✅")

        # Determine overall risk level
        if risk_score >= 0.8:
            overall_risk = RiskLevel.CRITICAL
        elif risk_score >= 0.6:
            overall_risk = RiskLevel.HIGH
        elif risk_score >= 0.4:
            overall_risk = RiskLevel.MEDIUM
        elif risk_score >= 0.2:
            overall_risk = RiskLevel.LOW
        else:
            overall_risk = RiskLevel.SAFE

        reasoning = (
            f"Text similarity: {text_similarity:.2f} | "
            f"Rule similarity: {rule_similarity:.2f} | "
            f"Risk: {overall_risk.value} ({risk_score:.2f})"
        )

        analysis = SemanticDriftAnalysis(
            market_a_id=market_a.get("id"),
            market_b_id=market_b.get("id"),
            text_similarity=text_similarity,
            rule_similarity=rule_similarity,
            timestamp_compatible=timestamp_compatible,
            source_compatible=source_compatible,
            overall_risk=overall_risk,
            risk_score=risk_score,
            issues=issues,
            reasoning=reasoning,
        )

        logger.info(f"  Result: {overall_risk.value.upper()} - {reasoning}")
        return analysis

    def _are_sources_equivalent(self, source_a: str, source_b: str) -> bool:
        """
        Check if two sources are equivalent for resolution purposes.
        E.g., "AP News" and "AP" are equivalent.
        """
        # Normalize sources
        norm_a = source_a.lower().strip()
        norm_b = source_b.lower().strip()

        # Direct match
        if norm_a == norm_b:
            return True

        # Check for common equivalences
        equivalences = {
            "ap news": ["ap", "associated press"],
            "ap": ["ap news", "associated press"],
            "reuters": ["reuters news"],
            "bloomberg": ["bloomberg terminal"],
        }

        for key, values in equivalences.items():
            if norm_a == key and norm_b in values:
                return True
            if norm_b == key and norm_a in values:
                return True

        return False


# ========================
# DEMONSTRATION
# ========================

if __name__ == "__main__":
    # Mock Data
    mock_markets = [
        {
            "id": "p1",
            "question": "Donald Trump wins the 2024 US Presidential Election",
            "resolution": "Winner of 2024 election",
            "resolution_criteria": "Official AP News call",
            "resolution_date": "2024-11-05",
            "resolution_source": "AP News",
        },
        {
            "id": "k1",
            "question": "A Republican wins the 2024 US Presidential Election",
            "resolution": "Party of winner",
            "resolution_criteria": "Official AP News call",
            "resolution_date": "2024-11-05",
            "resolution_source": "AP News",
        },
        {
            "id": "p2",
            "question": "Joe Biden wins the 2024 US Presidential Election",
            "resolution": "Winner of 2024 election",
            "resolution_criteria": "Official Fox News call",
            "resolution_date": "2024-11-06",
            "resolution_source": "Fox News",
        },
        {
            "id": "x1",
            "question": "Will it rain in London tomorrow?",
            "resolution": "Met Office",
        },
    ]

    engine = NLIEngine()

    print("\n" + "=" * 70)
    print("--- Step A: Semantic Clustering ---")
    print("=" * 70)
    clusters = engine.cluster_questions(mock_markets)
    for idx, cluster in enumerate(clusters):
        print(f"Cluster {idx + 1}: {[m['question'] for m in cluster]}")

    print("\n" + "=" * 70)
    print("--- Step B: NLI Analysis ---")
    print("=" * 70)
    if clusters:
        c = clusters[0]
        if len(c) >= 2:
            m1, m2 = c[0], c[1]
            print(f"Comparing:\n 1) {m1['question']}\n 2) {m2['question']}")
            result = engine.check_entailment(m1, m2)
            print(f"Result: {json.dumps(result, indent=2)}")

    print("\n" + "=" * 70)
    print("--- Step C: Semantic Drift Analysis ---")
    print("=" * 70)
    if clusters and len(clusters[0]) >= 2:
        m1, m2 = clusters[0][0], clusters[0][1]
        drift = engine.check_semantic_drift(m1, m2)
        print(f"\nDrift Analysis:")
        print(f"  Text Similarity: {drift.text_similarity:.2f}")
        print(f"  Rule Similarity: {drift.rule_similarity:.2f}")
        print(f"  Risk Level: {drift.overall_risk.value}")
        print(f"  Issues: {drift.issues}")


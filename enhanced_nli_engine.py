"""
Enhanced NLI Engine with Advanced Semantic Dependency Detection

Features:
- Temporal proximity filtering (prioritize markets with similar resolution dates)
- Topic clustering using embeddings (consider Linq-Embed-Mistral model)
- Complementary vs. dependent relationship classification:
  - Mutually exclusive (only one can be true)
  - Complementary (if one is true, the other must be true/false)
  - Independent (no logical connection)
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import DBSCAN
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RelationshipType(Enum):
    """Types of logical relationships between markets."""
    MUTUALLY_EXCLUSIVE = "mutually_exclusive"  # Only one can be true
    COMPLEMENTARY = "complementary"  # If one is true, other must be true/false
    ENTAILMENT = "entailment"  # One implies the other
    INDEPENDENT = "independent"  # No logical connection
    CONTRADICTION = "contradiction"  # Cannot both be true


class DependencyDirection(Enum):
    """Direction of dependency."""
    A_IMPLIES_B = "A_implies_B"
    B_IMPLIES_A = "B_implies_A"
    SYMMETRIC = "symmetric"
    NONE = "none"


@dataclass
class TemporalProximity:
    """Temporal proximity analysis."""
    market_a_date: Optional[datetime]
    market_b_date: Optional[datetime]
    days_difference: Optional[int]
    is_proximate: bool
    proximity_score: float  # 0-1, higher = more proximate


@dataclass
class TopicCluster:
    """Topic cluster information."""
    cluster_id: int
    markets: List[Dict[str, Any]]
    centroid_embedding: List[float]
    topic_keywords: List[str]
    size: int


@dataclass
class RelationshipAnalysis:
    """Complete relationship analysis between two markets."""
    relationship_type: RelationshipType
    direction: DependencyDirection
    confidence: float  # 0-1
    temporal_proximity: TemporalProximity
    topic_similarity: float  # 0-1
    semantic_similarity: float  # 0-1
    reasoning: str
    risk_factors: List[str]
    arbitrage_viability: bool


class EnhancedNLIEngine:
    """
    Enhanced NLI engine with advanced semantic dependency detection.
    
    Features:
    - Temporal proximity filtering
    - Topic clustering with embeddings
    - Relationship classification
    - Complementary vs. dependent detection
    """

    def __init__(
        self,
        embedding_model: str = "text-embedding-3-small",
        temporal_threshold_days: int = 7,
        similarity_threshold: float = 0.75,
    ):
        """
        Initialize enhanced NLI engine.
        
        Args:
            embedding_model: OpenAI embedding model to use
            temporal_threshold_days: Maximum days difference for temporal proximity
            similarity_threshold: Minimum similarity for clustering
        """
        logger.info(f"Loading enhanced NLI engine with model: {embedding_model}")
        self.embedding_model = embedding_model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.temporal_threshold_days = temporal_threshold_days
        self.similarity_threshold = similarity_threshold
        self.topic_clusters: List[TopicCluster] = []
        logger.info("✅ Enhanced NLI Engine initialized")

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

    def analyze_temporal_proximity(
        self,
        market_a: Dict[str, Any],
        market_b: Dict[str, Any],
    ) -> TemporalProximity:
        """
        Analyze temporal proximity between two markets.
        
        Args:
            market_a: First market dict
            market_b: Second market dict
            
        Returns:
            TemporalProximity analysis
        """
        date_a = self._parse_resolution_date(market_a.get("resolution_date"))
        date_b = self._parse_resolution_date(market_b.get("resolution_date"))

        if not date_a or not date_b:
            return TemporalProximity(
                market_a_date=date_a,
                market_b_date=date_b,
                days_difference=None,
                is_proximate=False,
                proximity_score=0.0,
            )

        days_diff = abs((date_b - date_a).days)
        is_proximate = days_diff <= self.temporal_threshold_days
        
        # Score: 1.0 if same day, decreases linearly to 0.0 at threshold
        proximity_score = max(0.0, 1.0 - (days_diff / self.temporal_threshold_days))

        return TemporalProximity(
            market_a_date=date_a,
            market_b_date=date_b,
            days_difference=days_diff,
            is_proximate=is_proximate,
            proximity_score=proximity_score,
        )

    def _parse_resolution_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """Parse resolution date string to datetime."""
        if not date_str:
            return None

        try:
            # Try ISO format first
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        except:
            try:
                # Try common formats
                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y"]:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except:
                        continue
            except:
                pass

        return None

    def cluster_markets_by_topic(
        self,
        markets: List[Dict[str, Any]],
        min_cluster_size: int = 2,
    ) -> List[TopicCluster]:
        """
        Cluster markets by topic using embeddings and DBSCAN.
        
        Args:
            markets: List of market dicts
            min_cluster_size: Minimum markets per cluster
            
        Returns:
            List of TopicCluster objects
        """
        if len(markets) < 2:
            return []

        logger.info(f"Clustering {len(markets)} markets by topic...")

        # Get embeddings for all market questions
        questions = [m.get("question", "") for m in markets]
        embeddings = self.get_embeddings(questions)

        if not embeddings:
            return []

        # Convert to numpy array
        embedding_matrix = np.array(embeddings)

        # Use DBSCAN for clustering
        # eps controls the maximum distance between samples in the same cluster
        # min_samples is the minimum number of samples in a cluster
        clustering = DBSCAN(
            eps=1.0 - self.similarity_threshold,
            min_samples=min_cluster_size,
            metric="cosine",
        ).fit(embedding_matrix)

        # Build clusters
        clusters = {}
        for idx, label in enumerate(clustering.labels_):
            if label == -1:  # Noise point
                continue

            if label not in clusters:
                clusters[label] = []

            clusters[label].append(markets[idx])

        # Create TopicCluster objects
        topic_clusters = []
        for cluster_id, cluster_markets in clusters.items():
            if len(cluster_markets) < min_cluster_size:
                continue

            # Calculate centroid
            cluster_indices = [markets.index(m) for m in cluster_markets]
            cluster_embeddings = embedding_matrix[cluster_indices]
            centroid = np.mean(cluster_embeddings, axis=0).tolist()

            # Extract topic keywords (simplified - could use LLM)
            topic_keywords = self._extract_topic_keywords(cluster_markets)

            topic_cluster = TopicCluster(
                cluster_id=cluster_id,
                markets=cluster_markets,
                centroid_embedding=centroid,
                topic_keywords=topic_keywords,
                size=len(cluster_markets),
            )
            topic_clusters.append(topic_cluster)

        logger.info(f"✅ Created {len(topic_clusters)} topic clusters")
        self.topic_clusters = topic_clusters
        return topic_clusters

    def _extract_topic_keywords(self, markets: List[Dict[str, Any]]) -> List[str]:
        """Extract topic keywords from a cluster of markets."""
        # Simple keyword extraction - could be enhanced with LLM
        all_text = " ".join([m.get("question", "") for m in markets]).lower()
        
        # Common words to ignore
        stop_words = {"will", "the", "a", "an", "be", "is", "are", "was", "were", "by", "on", "in", "at", "to", "for", "of", "with"}
        
        # Extract significant words (simplified)
        words = [w.strip(".,!?") for w in all_text.split() if len(w) > 3 and w not in stop_words]
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:5]]

    def classify_relationship(
        self,
        market_a: Dict[str, Any],
        market_b: Dict[str, Any],
    ) -> RelationshipAnalysis:
        """
        Classify the relationship between two markets.
        
        Args:
            market_a: First market dict
            market_b: Second market dict
            
        Returns:
            RelationshipAnalysis with complete classification
        """
        logger.info(
            f"Classifying relationship: {market_a.get('id')} vs {market_b.get('id')}"
        )

        # Get semantic similarity
        q_a = market_a.get("question", "")
        q_b = market_b.get("question", "")
        embeddings = self.get_embeddings([q_a, q_b])
        
        if len(embeddings) == 2:
            semantic_similarity = float(cosine_similarity([embeddings[0]], [embeddings[1]])[0][0])
        else:
            semantic_similarity = 0.0

        # Get topic similarity (check if in same cluster)
        topic_similarity = self._get_topic_similarity(market_a, market_b)

        # Analyze temporal proximity
        temporal_prox = self.analyze_temporal_proximity(market_a, market_b)

        # Use LLM to classify relationship type
        relationship_type, direction, confidence, reasoning = self._llm_classify_relationship(
            market_a, market_b
        )

        # Determine arbitrage viability
        arbitrage_viability = self._assess_arbitrage_viability(
            relationship_type,
            semantic_similarity,
            temporal_prox,
            confidence,
        )

        # Risk factors
        risk_factors = []
        if semantic_similarity < 0.85:
            risk_factors.append(f"Low semantic similarity ({semantic_similarity:.2f})")
        if not temporal_prox.is_proximate:
            risk_factors.append(f"Different resolution dates ({temporal_prox.days_difference} days apart)")
        if confidence < 0.80:
            risk_factors.append(f"Low confidence ({confidence:.2f})")
        if relationship_type == RelationshipType.INDEPENDENT:
            risk_factors.append("Markets are independent - no logical connection")

        return RelationshipAnalysis(
            relationship_type=relationship_type,
            direction=direction,
            confidence=confidence,
            temporal_proximity=temporal_prox,
            topic_similarity=topic_similarity,
            semantic_similarity=semantic_similarity,
            reasoning=reasoning,
            risk_factors=risk_factors,
            arbitrage_viability=arbitrage_viability,
        )

    def _get_topic_similarity(
        self,
        market_a: Dict[str, Any],
        market_b: Dict[str, Any],
    ) -> float:
        """Check if markets are in the same topic cluster."""
        for cluster in self.topic_clusters:
            market_ids = [m.get("id") for m in cluster.markets]
            if market_a.get("id") in market_ids and market_b.get("id") in market_ids:
                return 1.0
        return 0.0

    def _llm_classify_relationship(
        self,
        market_a: Dict[str, Any],
        market_b: Dict[str, Any],
    ) -> Tuple[RelationshipType, DependencyDirection, float, str]:
        """
        Use LLM to classify relationship type.
        
        Returns:
            (relationship_type, direction, confidence, reasoning)
        """
        prompt = f"""
        Analyze the logical relationship between these two prediction market questions.

        Market A: "{market_a.get('question', '')}"
        Resolution Criteria A: "{market_a.get('resolution_criteria', 'Standard Logic')}"
        Resolution Date A: "{market_a.get('resolution_date', 'N/A')}"

        Market B: "{market_b.get('question', '')}"
        Resolution Criteria B: "{market_b.get('resolution_criteria', 'Standard Logic')}"
        Resolution Date B: "{market_b.get('resolution_date', 'N/A')}"

        Classify the relationship as one of:
        1. MUTUALLY_EXCLUSIVE - Only one can be true (e.g., "Trump wins" vs "Biden wins")
        2. COMPLEMENTARY - If one is true, the other must be true/false (e.g., "Republican wins" vs "Democrat wins")
        3. ENTAILMENT - One implies the other (e.g., "Trump wins" implies "Republican wins")
        4. INDEPENDENT - No logical connection
        5. CONTRADICTION - Cannot both be true

        Output ONLY valid JSON:
        {{
            "relationship": "mutually_exclusive" | "complementary" | "entailment" | "independent" | "contradiction",
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
            content = json.loads(response.choices[0].message.content)
            
            relationship_str = content.get("relationship", "independent")
            direction_str = content.get("direction", "none")
            confidence = float(content.get("confidence", 0.5))
            reasoning = content.get("reasoning", "")

            # Map to enums
            relationship_map = {
                "mutually_exclusive": RelationshipType.MUTUALLY_EXCLUSIVE,
                "complementary": RelationshipType.COMPLEMENTARY,
                "entailment": RelationshipType.ENTAILMENT,
                "independent": RelationshipType.INDEPENDENT,
                "contradiction": RelationshipType.CONTRADICTION,
            }
            
            direction_map = {
                "A_implies_B": DependencyDirection.A_IMPLIES_B,
                "B_implies_A": DependencyDirection.B_IMPLIES_A,
                "symmetric": DependencyDirection.SYMMETRIC,
                "none": DependencyDirection.NONE,
            }

            relationship = relationship_map.get(relationship_str, RelationshipType.INDEPENDENT)
            direction = direction_map.get(direction_str, DependencyDirection.NONE)

            return relationship, direction, confidence, reasoning

        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            return RelationshipType.INDEPENDENT, DependencyDirection.NONE, 0.0, f"Error: {e}"

    def _assess_arbitrage_viability(
        self,
        relationship_type: RelationshipType,
        semantic_similarity: float,
        temporal_prox: TemporalProximity,
        confidence: float,
    ) -> bool:
        """
        Assess if arbitrage is viable based on relationship analysis.
        
        Args:
            relationship_type: Type of relationship
            semantic_similarity: Semantic similarity score
            temporal_prox: Temporal proximity analysis
            confidence: Confidence in classification
            
        Returns:
            True if arbitrage is viable
        """
        # Must have high confidence
        if confidence < 0.80:
            return False

        # Must be semantically similar
        if semantic_similarity < 0.85:
            return False

        # Must be temporally proximate
        if not temporal_prox.is_proximate:
            return False

        # Relationship must be suitable for arbitrage
        viable_relationships = [
            RelationshipType.MUTUALLY_EXCLUSIVE,
            RelationshipType.COMPLEMENTARY,
            RelationshipType.ENTAILMENT,
        ]

        return relationship_type in viable_relationships

    def filter_by_temporal_proximity(
        self,
        markets: List[Dict[str, Any]],
        reference_date: Optional[datetime] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter markets by temporal proximity to a reference date.
        
        Args:
            markets: List of markets
            reference_date: Reference date (uses first market if not provided)
            
        Returns:
            Filtered list of markets within temporal threshold
        """
        if not markets:
            return []

        if reference_date is None:
            first_date = self._parse_resolution_date(markets[0].get("resolution_date"))
            if first_date:
                reference_date = first_date
            else:
                return markets  # Can't filter without dates

        filtered = []
        for market in markets:
            market_date = self._parse_resolution_date(market.get("resolution_date"))
            if market_date:
                days_diff = abs((market_date - reference_date).days)
                if days_diff <= self.temporal_threshold_days:
                    filtered.append(market)
            else:
                # Include markets without dates (conservative)
                filtered.append(market)

        return filtered


# ========================
# UTILITY FUNCTIONS
# ========================

def get_enhanced_nli_engine(
    embedding_model: str = "text-embedding-3-small",
    temporal_threshold_days: int = 7,
) -> EnhancedNLIEngine:
    """Factory function for EnhancedNLIEngine."""
    return EnhancedNLIEngine(
        embedding_model=embedding_model,
        temporal_threshold_days=temporal_threshold_days,
    )


if __name__ == "__main__":
    # Test the enhanced NLI engine
    engine = get_enhanced_nli_engine()

    mock_markets = [
        {
            "id": "m1",
            "question": "Donald Trump wins the 2024 US Presidential Election",
            "resolution_date": "2024-11-05",
            "resolution_criteria": "Official AP News call",
        },
        {
            "id": "m2",
            "question": "A Republican wins the 2024 US Presidential Election",
            "resolution_date": "2024-11-05",
            "resolution_criteria": "Official AP News call",
        },
    ]

    # Test temporal proximity
    temporal = engine.analyze_temporal_proximity(mock_markets[0], mock_markets[1])
    print(f"Temporal Proximity: {temporal.is_proximate} (Score: {temporal.proximity_score:.2f})")

    # Test relationship classification
    relationship = engine.classify_relationship(mock_markets[0], mock_markets[1])
    print(f"\nRelationship: {relationship.relationship_type.value}")
    print(f"Confidence: {relationship.confidence:.2f}")
    print(f"Arbitrage Viable: {relationship.arbitrage_viability}")
    print(f"Reasoning: {relationship.reasoning}")

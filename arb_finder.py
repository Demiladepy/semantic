import csv
from datetime import datetime
import os
import time
from market_client import PolymarketAdapter, KalshiAdapter, MarketAggregator
from nli_engine import NLIEngine

def log_trade(market_a, market_b, spread, action):
    file_exists = os.path.isfile("paper_trades.csv")
    with open("paper_trades.csv", "a", newline="") as csvfile:
        fieldnames = ["timestamp", "market_a_id", "market_a_source", "market_a_price", "market_b_id", "market_b_source", "market_b_price", "spread", "action"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow({
            "timestamp": datetime.now().isoformat(),
            "market_a_id": market_a['id'],
            "market_a_source": market_a['source'],
            "market_a_price": market_a['outcomes'][0]['price'],
            "market_b_id": market_b['id'],
            "market_b_source": market_b['source'],
            "market_b_price": market_b['outcomes'][0]['price'],
            "spread": round(spread, 4),
            "action": action
        })

def main():
    # 1. Initialize Components
    print("Initializing Market Adapters...")
    # In real usage, we might pass API keys here
    aggregator = MarketAggregator([
        PolymarketAdapter(),
        KalshiAdapter()
    ])
    
    # 2. Initialize NLI Logic Brain
    # Note: efficient loading might check if model is already in memory
    engine = NLIEngine()

    # 3. Main Loop (Simulated)
    print("\n--- Starting Arbitrage Scan ---\n")
    
    # Step A: Ingest Data
    markets = aggregator.get_all_markets()
    print(f"Ingested {len(markets)} active markets.")

    # Step B: Semantic Clustering
    print("Clustering markets by semantic similarity...")
    clusters = engine.cluster_questions(markets)
    print(f"Found {len(clusters)} clusters.")

    # Step C: Analyze Clusters for Arbitrage
    for cluster_idx, cluster in enumerate(clusters):
        if len(cluster) < 2:
            continue
            
        print(f"\nChecking Cluster {cluster_idx + 1} (Size: {len(cluster)})")
        
        # Naive pairwise comparison within cluster
        # In production, optimize to avoid N^2 calls if cluster is large
        for i in range(len(cluster)):
            for j in range(i + 1, len(cluster)):
                m_a = cluster[i]
                m_b = cluster[j]
                
                # Check Logic
                print(f"  Comparing '{m_a['question']}' vs '{m_b['question']}'...")
                analysis = engine.check_entailment(m_a, m_b)
                
                if not analysis:
                    continue

                rel = analysis.get("relationship")
                direction = analysis.get("direction")
                confidence = analysis.get("confidence", 0)

                if confidence < 0.8:
                    continue # Skip low confidence

                print(f"    -> Relationship: {rel} ({direction})")

                # Step D: Check Prices (Arbitrage Math)
                # Assuming Outcome[0] is 'Yes' for both. 
                # REALITY CHECK: Need to normalize 'Yes'/'No' indices.
                price_a = m_a['outcomes'][0]['price']
                price_b = m_b['outcomes'][0]['price']

                if rel == "entailment":
                    # Check Resolution Risk before proceeding
                    print(f"    Checking Resolution Nuance...")
                    risk_analysis = engine.check_resolution_nuance(m_a, m_b)
                    risk_score = risk_analysis.get('risk_score', 1.0)
                    
                    if risk_score > 0.3: # Threshold for "Safe" Arb
                        print(f"    [SKIP] Resolution Risk too high ({risk_score}): {risk_analysis.get('reason')}")
                        continue
                        
                    print(f"    [PASS] Resolution Risk: {risk_score}")

                    # If A implies B, then Price(A) should be <= Price(B)
                    # Arb opportunity: Price(A) > Price(B) (Buy B, Short A)
                    if direction == "A_implies_B":
                        if price_a > price_b:
                            spread = price_a - price_b
                            print(f"    $$$ ARBITRAGE FOUND $$$")
                            print(f"    Logic: {m_a['source']} -> {m_b['source']}")
                            print(f"    Spread: {spread:.2f} ({price_a} > {price_b})")
                            print(f"    Action: Sell {m_a['source']} (A), Buy {m_b['source']} (B)")
                            log_trade(m_a, m_b, spread, f"Sell {m_a['source']}, Buy {m_b['source']}")
                    elif direction == "B_implies_A":
                         if price_b > price_a:
                            spread = price_b - price_a
                            print(f"    $$$ ARBITRAGE FOUND $$$")
                            print(f"    Logic: {m_b['source']} -> {m_a['source']}")
                            print(f"    Spread: {spread:.2f} ({price_b} > {price_a})")
                            print(f"    Action: Sell {m_b['source']} (B), Buy {m_a['source']} (A)")
                            log_trade(m_a, m_b, spread, f"Sell {m_b['source']}, Buy {m_a['source']}")
                
                elif rel == "mutual_exclusivity":
                    # If A and B are mutually exclusive, P(A) + P(B) <= 1
                    # Arb opportunity: P(A) + P(B) > 1 (Short Both)
                    if price_a + price_b > 1.05: # Threshold for fees
                        print(f"    $$$ ARBITRAGE FOUND $$$")
                        print(f"    Logic: Mutually Exclusive")
                        print(f"    Sum: {price_a + price_b:.2f} > 1.0")
                        print(f"    Action: Sell/No both A and B")
                        log_trade(m_a, m_b, (price_a + price_b) - 1.0, "Short Both")

if __name__ == "__main__":
    main()

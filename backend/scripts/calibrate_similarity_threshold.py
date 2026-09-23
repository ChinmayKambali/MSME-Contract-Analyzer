import sys
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.db import SessionLocal
from app.services.retrieval import retrieve_benchmark_clauses
from app.services.llm_client import get_embedding

logging.basicConfig(level=logging.INFO)

TEST_QUERIES = [
    {
        "category": "payment_terms",
        "text": "Payment shall be made within 45 days from invoice date in accordance with MSMED Act 2006."
    },
    {
        "category": "liability",
        "text": "The aggregate liability of either party shall not exceed the total fees paid under this agreement in the preceding 12 months."
    },
    {
        "category": "penalty_ld",
        "text": "Liquidated damages for delay shall be capped at 0.5% per week up to a maximum of 5% of PO value."
    },
    {
        "category": "dispute_resolution",
        "text": "Disputes shall be referred to arbitration in Mumbai under the Arbitration and Conciliation Act 1996 or MSME Facilitation Council."
    },
    {
        "category": "termination",
        "text": "Either party may terminate this agreement by giving 30 days written notice."
    },
    {
        "category": "payment_terms",
        "text": "Random irrelevant text about weather and coffee recipes in the office kitchen."
    }
]

def main():
    print("\n========================================================")
    print("   SIMILARITY THRESHOLD CALIBRATION TEST")
    print("========================================================")
    db = SessionLocal()
    try:
        for idx, item in enumerate(TEST_QUERIES, 1):
            print(f"\n--- Query {idx} [{item['category']}]: \"{item['text'][:70]}...\" ---")
            results = retrieve_benchmark_clauses(
                db=db,
                query_text=item["text"],
                category=item["category"],
                top_k=5,
                threshold=0.0  # Retrieve raw top scores without filtering to see full score range
            )
            if not results:
                print("  No matches returned from database.")
                continue

            for rank, res in enumerate(results, 1):
                print(f"  Rank {rank}: Score = {res['similarity']:.4f} | Doc: {res['source_doc']} | Heading: {res['heading']}")

    finally:
        db.close()

if __name__ == "__main__":
    main()

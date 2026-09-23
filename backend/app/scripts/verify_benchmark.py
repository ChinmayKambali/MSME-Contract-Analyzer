from sqlalchemy import func
from app.db import SessionLocal
from app.models import BenchmarkClause
from app.services.retrieval import retrieve_benchmark_clauses

def verify():
    db = SessionLocal()
    try:
        total = db.query(BenchmarkClause).count()
        print(f"\n==========================================")
        print(f"   MSME BENCHMARK LIBRARY VERIFICATION")
        print(f"==========================================")
        print(f"Total Benchmark Clauses in Database: {total}\n")

        # Counts by category
        cat_counts = (
            db.query(BenchmarkClause.category, func.count(BenchmarkClause.id))
            .group_by(BenchmarkClause.category)
            .all()
        )
        print("--- CLAUSE COUNTS PER CATEGORY ---")
        for cat, cnt in cat_counts:
            print(f"  • {cat:<20}: {cnt} clauses")

        # Counts by source doc
        doc_counts = (
            db.query(BenchmarkClause.source_doc, func.count(BenchmarkClause.id))
            .group_by(BenchmarkClause.source_doc)
            .order_by(BenchmarkClause.source_doc)
            .all()
        )
        print(f"\n--- CLAUSE COUNTS PER SOURCE DOC ({len(doc_counts)} files) ---")
        for doc, cnt in doc_counts:
            print(f"  • {doc:<25}: {cnt} clauses")

        # Sample retrieval queries
        sample_queries = [
            ("Payment delay shall incur interest under MSMED Act", "payment_terms"),
            ("Vendor liability shall be capped at total fees paid", "liability"),
            ("Either party may terminate with 30 days prior written notice", "termination")
        ]

        print(f"\n==========================================")
        print(f"   SAMPLE VECTOR RETRIEVAL TEST")
        print(f"==========================================")
        for query_text, cat in sample_queries:
            print(f"\nQuery ({cat}): '{query_text}'")
            results = retrieve_benchmark_clauses(db, query_text=query_text, category=cat, top_k=3, threshold=0.0)
            if not results:
                print("  No matches found (Check GEMINI_API_KEY or embeddings).")
            else:
                for idx, r in enumerate(results, 1):
                    print(f"  {idx}. [{r['source_doc']}] {r['heading']} (Similarity: {r['similarity']:.4f})")
                    snippet = r['text'].replace('\n', ' ')[:100]
                    print(f"     \"{snippet}...\"")

    finally:
        db.close()

if __name__ == "__main__":
    verify()

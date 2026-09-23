import logging
from app.db import init_db, SessionLocal
from app.services.benchmark_ingestion import seed_benchmark_library

logging.basicConfig(level=logging.INFO)

def main():
    print("Initializing Database...")
    init_db()
    db = SessionLocal()
    try:
        print("Seeding MSME Benchmark Library...")
        count = seed_benchmark_library(db)
        print(f"Done! {count} new clauses added to benchmark library.")
    finally:
        db.close()

if __name__ == "__main__":
    main()

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.config import settings
from app.db import init_db, SessionLocal
from app.api.router import router as api_router
from app.services.benchmark_ingestion import seed_benchmark_library

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup DB initialization & auto-seeding
    logger.info("Initializing database and pgvector extension...")
    try:
        init_db()
        db = SessionLocal()
        try:
            # Try to acquire Postgres advisory lock for safe idempotent seeding
            lock_acquired = False
            try:
                result = db.execute(text("SELECT pg_try_advisory_lock(84920482);")).scalar()
                lock_acquired = bool(result)
            except Exception:
                lock_acquired = True

            if lock_acquired:
                logger.info("Checking MSME Benchmark Library auto-seeding...")
                seed_benchmark_library(db)
                try:
                    db.execute(text("SELECT pg_advisory_unlock(84920482);"))
                except Exception:
                    pass
        finally:
            db.close()
    except Exception as e:
        logger.warning(f"Startup DB auto-seeding notice: {e}")

    yield
    logger.info("Shutting down API server.")

app = FastAPI(
    title="Automated MSME Contract Risk Analyzer API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "MSME Contract Analyzer API"}

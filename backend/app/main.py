import logging
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text
from app.config import settings
from app.db import init_db, SessionLocal
from app.api.router import router as api_router
from app.services.benchmark_ingestion import seed_benchmark_library

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _seed_benchmarks() -> None:
    """Idempotently seed the benchmark library, guarded by a Postgres advisory lock."""
    db = SessionLocal()
    try:
        try:
            lock_acquired = bool(db.execute(text("SELECT pg_try_advisory_lock(84920482);")).scalar())
        except Exception:
            lock_acquired = True

        if lock_acquired:
            logger.info("Checking MSME Benchmark Library auto-seeding...")
            seed_benchmark_library(db)
            try:
                db.execute(text("SELECT pg_advisory_unlock(84920482);"))
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Benchmark auto-seeding notice: {e}")
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database and pgvector extension...")
    try:
        init_db()
        # Seeding embeds hundreds of clauses on a fresh database, so run it in the
        # background: the server starts accepting requests immediately.
        threading.Thread(target=_seed_benchmarks, daemon=True).start()
    except Exception as e:
        logger.warning(f"Startup DB initialization notice: {e}")

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


# ---------------------------------------------------------------------------
# Optional: serve the built React app (single-container deployment)
# ---------------------------------------------------------------------------
if settings.FRONTEND_DIST_DIR:
    _dist = Path(settings.FRONTEND_DIST_DIR).resolve()
    if (_dist / "index.html").exists():
        logger.info(f"Serving frontend from {_dist}")

        @app.get("/{full_path:path}", include_in_schema=False)
        def serve_frontend(full_path: str):
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404, detail="Not Found")
            candidate = (_dist / full_path).resolve()
            if full_path and candidate.is_file() and _dist in candidate.parents:
                return FileResponse(candidate)
            # Client-side routes (React Router) fall back to index.html
            return FileResponse(_dist / "index.html")
    else:
        logger.warning(f"FRONTEND_DIST_DIR set but no index.html in {_dist}")

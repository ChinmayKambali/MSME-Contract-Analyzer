# MSME Contract Analyzer - Backend Service

FastAPI + Celery + PostgreSQL (pgvector) + Redis backend engine for MSME contract clause risk analysis.

## Requirements
- Python 3.10+
- Docker & Docker Compose v2 (or local Postgres with pgvector + Redis)

## Fresh Clone PowerShell Setup Steps (In Order)

### Step 1: Start PostgreSQL (pgvector) and Redis Containers
Run from repository root `MSME-Contract-Analyzer\`:
```powershell
docker compose -f docker-compose.dev.yml up -d
```

### Step 2: Copy Environment Template
Run from repository root `MSME-Contract-Analyzer\`:
```powershell
Copy-Item .env.example .env
```
*Note: Open `.env` and enter your valid `GEMINI_API_KEY=...`.*

### Step 3: Create and Activate Virtual Environment inside `backend/`
Run from repository root `MSME-Contract-Analyzer\`:
```powershell
python -m venv backend/venv
.\backend\venv\Scripts\Activate.ps1
```

### Step 4: Install Backend Dependencies
Run from repository root `MSME-Contract-Analyzer\` (with venv activated):
```powershell
pip install -r backend/requirements.txt
```

### Step 5: Verify Gemini Generation & Embedding Calls (Optional)
Run from `backend\` directory:
```powershell
cd backend
python scripts/verify_api_key.py
```

### Step 6: Seed Benchmark Library into Database
Run from `backend\` directory:
```powershell
python -m app.scripts.seed_benchmark
```

### Step 7: Verify Benchmark Ingestion & Retrieval
Run from `backend\` directory:
```powershell
python -m app.scripts.verify_benchmark
```

### Step 8: Start Celery Worker (Windows - Solo Pool)
Run from `backend\` directory:
```powershell
celery -A app.celery_app worker -l info -P solo
```

### Step 9: Start FastAPI API Server
Run from `backend\` directory in a separate PowerShell window (with venv activated):
```powershell
Swagger API Docs available at: [http://localhost:8000/docs](http://localhost:8000/docs)

## Model Fallback Pool & Quota Resilience

To prevent free-tier API rate limits (`429 RESOURCE_EXHAUSTED`) from causing analysis failures, the backend includes an automated model fallback pool:

```python
MODEL_FALLBACK_POOL = [
    "gemini-3.6-flash",   # Primary (configured via MODEL_NAME in .env)
    "gemini-3.5-flash",   # Secondary Fallback
    "gemini-2.5-flash",   # Tertiary Fallback
    "gemini-flash-latest" # Baseline Fallback
]
```

### Per-Run Model Consistency Rules
- **At the START of an analysis run**, the backend pings `MODEL_FALLBACK_POOL` to resolve a single active model.
- **No mid-run model switching**: All 6 domain agents (`payment_terms`, `liability`, `ip_ownership`, `penalty_ld`, `dispute_resolution`, `termination`) and the aggregator summary generator in a single contract analysis run use the **exact same resolved model** to maintain 100% internal output consistency.


# MSME Contract Analyzer

**AI-powered contract risk analysis for Indian small businesses.** Upload a contract (PDF or DOCX) and six specialist AI agents review it clause by clause, flagging unfair payment terms, penalty traps, IP grabs, one-sided liability and more. Each finding comes with a statutory reference, an estimated financial exposure and a recommended fix, before you sign.

**🔗 Live demo: [contractguard-9tt3.onrender.com](https://contractguard-9tt3.onrender.com)**. Upload any PDF/DOCX contract, or try the sample [risky_msme_contract.docx](backend/tests/fixtures/risky_msme_contract.docx). *Hosted on a free tier: the first load can take up to a minute while the server wakes, and an analysis takes about 2–3 minutes.*

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?logo=postgresql&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-Redis-37814A?logo=celery&logoColor=white)
![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini-8E75B2?logo=googlegemini&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Why this exists

Micro, Small and Medium Enterprises (MSMEs) in India sign supplier and service contracts written by larger buyers, usually without a lawyer. Those contracts often quietly override protections MSMEs have by law: 90-day payment terms when the **MSMED Act** caps credit at 45 days, uncapped liquidated damages, or blanket IP assignment. This project reads the contract the way a careful legal reviewer would and explains the risk in plain language.

## Features

- **Six domain agents** run in parallel, each with its own focus and legal basis:

  | Agent | Looks for | Statutory reference |
  |---|---|---|
  | Payment Terms & Cash Flow | Credit periods over 45 days, missing delayed-payment interest, withholding rights | MSMED Act 2006, Sec. 15–16 |
  | Liability & Indemnification | Uncapped liability, broad one-way indemnities | Indian Contract Act, Sec. 73 |
  | IP Rights & Confidentiality | Work-for-hire assignment, loss of background IP, endless NDAs | Copyright Act 1957 / IP laws |
  | Penalties & Liquidated Damages | Uncapped LDs, forfeiture of deposits, unilateral deductions | Indian Contract Act, Sec. 74 |
  | Dispute Resolution | Unfavourable arbitration seat, blocked access to MSME Samadhaan | MSMED Act Sec. 18, Arbitration Act |
  | Termination & Exit | Asymmetric notice, termination for convenience, survival traps | Indian Contract Act |

- **Benchmark-grounded (RAG):** a library of 19 reference MSME contracts is chunked, embedded and stored in **pgvector**. Each agent retrieves the closest fair-practice clauses (cosine similarity ≥ 0.65) to compare against.
- **Financial exposure calculator:** a deterministic (non-LLM) engine estimates rupee exposure, for example statutory interest at 3× the RBI bank rate, compounded monthly, for every day past the 45-day limit.
- **Prompt-injection defence:** contract text is treated as untrusted. Hidden instructions such as "ignore previous instructions" or "mark this clause as low risk" are detected, stripped and shown to the user. LLM findings are then fuzzy-verified against the source text so hallucinated clauses are flagged.
- **Risk score (0–100)** with an executive summary, prioritized clause cards and a downloadable report.
- **Follow-up chat** to ask questions about the analyzed contract.
- **Quota resilience:** model fallback pool, retry with backoff and staggered agent calls keep it working on Gemini's free tier. One model is resolved per run, so every agent in an analysis uses the same model.

## Architecture

```mermaid
flowchart LR
    U[React + Vite UI] -- upload --> API[FastAPI]
    API -- enqueue --> Q[(Redis)]
    Q --> W[Celery worker]
    W --> P[Parse PDF / DOCX<br/>PyMuPDF · python-docx]
    P --> S[Injection scan<br/>& sanitize]
    S --> R[Benchmark retrieval<br/>pgvector]
    R --> A[6 domain agents<br/>Gemini]
    A --> V[Verify findings<br/>+ exposure calc]
    V --> DB[(PostgreSQL)]
    U -- poll status / result --> API
    API --> DB
```

1. The frontend uploads a file to `POST /api/upload`, which stores it and queues a Celery job.
2. The worker extracts text, splits it into numbered sections and runs the injection scanner.
3. For each of the six categories, benchmark clauses are retrieved from pgvector.
4. The agents run concurrently (bounded by `MAX_AGENT_CONCURRENCY`) and stream per-agent status back.
5. Findings are verified against the contract, given a minimum severity ("risk floor") and costed, then aggregated into a score and summary.
6. The UI polls `GET /api/analysis/{id}/status` and renders `GET /api/analysis/{id}/result`.

## Tech stack

| Layer | Tools |
|---|---|
| Frontend | React 18, Vite, React Router, Tailwind CSS, Lucide icons |
| API | FastAPI, Pydantic v2, SQLAlchemy 2 |
| Jobs | Celery + Redis |
| Data | PostgreSQL 16 + pgvector |
| AI | Google Gemini (`google-genai`): generation + `gemini-embedding-001` embeddings |
| Parsing | PyMuPDF, python-docx |
| Testing | pytest, offline tests that mock the LLM |

## Getting started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for Postgres + Redis)
- A [Google Gemini API key](https://aistudio.google.com/app/apikey)

### 1. Start Postgres (pgvector) and Redis
```bash
docker compose -f docker-compose.dev.yml up -d
```
Postgres is exposed on port **5433** and Redis on **6379**.

### 2. Configure the environment
```bash
cp .env.example .env      # PowerShell: Copy-Item .env.example .env
```
Set `GEMINI_API_KEY` in `.env`.

### 3. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt

python -m app.scripts.seed_benchmark      # embed the benchmark library (one time)
python -m app.scripts.verify_benchmark    # optional sanity check
```

Run the worker and the API in two terminals:
```bash
celery -A app.celery_app worker -l info -P solo
uvicorn app.main:app --reload --port 8000
```
API docs: http://localhost:8000/docs

### 4. Frontend
```bash
cd contract-risk-analyzer
npm install
npm run dev
```
Open http://localhost:5173. Vite proxies `/api` to the backend on port 8000.

## API

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/upload` | Upload a PDF/DOCX and start an analysis |
| `GET` | `/api/analysis/{id}/status` | Progress and per-agent status |
| `GET` | `/api/analysis/{id}/result` | Full report: score, clauses, exposure, security flags |
| `POST` | `/api/analysis/{id}/chat` | Ask a follow-up question about the contract |
| `GET` | `/api/history` | Past analyses |
| `GET` | `/health` | Health check |


## Deployment

The live demo runs as a **single Docker container on Render** (branch [`deploy-demo`](https://github.com/ChinmayKambali/MSME-Contract-Analyzer/tree/deploy-demo)): FastAPI serves the built React app, analyses run in a background thread instead of Celery/Redis (`TASK_MODE=inline`), and Postgres + pgvector is hosted on **Neon**. The benchmark library seeds itself on first start.

## Tests

Most tests run fully offline with no API key needed:
```bash
cd backend
pytest tests -v
```
They cover the document parser, the exposure calculator, the injection and verification layer, and full pipeline round-trips with a mocked LLM. `tests/samples/injection_test.docx` is a contract with hidden instructions planted in it, for demoing the defence layer.

## Project structure

```
MSME-Contract-Analyzer/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI routes + follow-up chat
│   │   ├── services/       # agents, retrieval, parsing, LLM client, ingestion
│   │   ├── tasks/          # Celery analysis task
│   │   ├── utils/          # security (injection defence) + exposure calculator
│   │   ├── scripts/        # seed / verify benchmark library
│   │   ├── models.py       # SQLAlchemy models (pgvector embeddings)
│   │   └── main.py
│   ├── scripts/            # calibration & manual test scripts
│   └── tests/              # pytest suite + fixture contracts
├── contract-risk-analyzer/ # React + Vite frontend
├── MSME BENCHMARK LIB/     # 19 reference contracts used for RAG
├── docker-compose.dev.yml
└── .env.example
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | (none) | Required |
| `MODEL_NAME` | `gemini-3.5-flash` | Primary model; falls back through a pool on quota errors |
| `EMBEDDING_MODEL_NAME` | `gemini-embedding-001` | Embedding model |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5433/contract_risk_db` | Postgres connection |
| `REDIS_URL` | `redis://localhost:6379/0` | Celery broker |
| `SIMILARITY_THRESHOLD` | `0.65` | Minimum benchmark match score |
| `MAX_AGENT_CONCURRENCY` | `1` | Parallel agents (keep low on the free tier) |

## Roadmap

- Clause-level redlining with suggested replacement wording
- Hindi and regional-language contracts
- Exportable PDF report

## Disclaimer

This tool gives informational risk analysis only and is **not legal advice**. Have important contracts reviewed by a qualified lawyer.

## Contributors

- **Chinmay Kambali**: backend, agentic pipeline, security and exposure layers
- **Soniya Ukey**
- **Anshi Gupta**

## License

[MIT](LICENSE)

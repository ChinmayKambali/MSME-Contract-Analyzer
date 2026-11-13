# ContractGuard AI: Frontend

React + Vite frontend for the [MSME Contract Analyzer](../README.md).

## Flow

`Upload` → `Scan` (text extraction) → `Analysis` (live status of the 6 agents) → `Results` (risk score, clause cards, exposure, injection warnings, follow-up chat, report download)

## Run

```bash
npm install
npm run dev      # http://localhost:5173
```

The dev server proxies `/api` to the FastAPI backend at `http://localhost:8000` (see `vite.config.js`), so start the backend first. See the root README.

```bash
npm run build    # production build into dist/
```

## Structure

```
src/
├── pages/        # Upload, Scan, Analysis, Results, Combine, NotFound
├── components/   # upload/, scan/, analysis/, results/, combine/, common/
├── context/      # Upload, Contract and Analysis state
├── hooks/        # useUpload, useScan, useAnalysis, useDownload
├── utils/        # apiClient, risk colours, helpers
└── routes/       # AppRoutes
```

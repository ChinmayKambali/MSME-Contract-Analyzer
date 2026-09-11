# ContractGuard AI

ContractGuard AI is a React and Vite application for reviewing contracts and highlighting clauses that may create legal, financial, privacy, or operational risk.

## Features

- Upload PDF, DOC, and DOCX contract files
- Simulated document scanning and text extraction flow
- Multi-agent contract review workflow
- Risk score and overall risk summary
- Prioritized clause findings with recommended actions
- Downloadable text report
- Responsive interface for desktop and mobile screens

## Tech Stack

- React
- Vite
- React Router
- Tailwind CSS
- Lucide React

## Getting Started

### Requirements

- Node.js 18 or newer
- npm

### Install dependencies

```bash
npm install
```

### Start the development server

```bash
npm run dev
```

Open the local URL displayed by Vite in your browser.

### Create a production build

```bash
npm run build
```

### Preview the production build

```bash
npm run preview
```

## Workflow

1. Upload a contract.
2. Scan the document.
3. Review the specialist analysis progress.
4. Combine the findings into one report.
5. Review prioritized risks and recommended actions.

The current application uses local mock report data and simulated analysis progress. No backend or external API is required to run the interface.

## Project Structure

```text
public/                 Static files and public assets
src/
  assets/               Application assets, icons, images, and fonts
  components/           Reusable UI and workflow components
  context/              Contract, upload, and analysis state
  data/                 Local mock report data
  hooks/                 Upload, scan, analysis, and download hooks
  layouts/              Application shell, navigation, and footer
  pages/                Upload, scan, analysis, combine, and results pages
  routes/               React Router configuration
  styles/               Global styles
  utils/                Shared constants and helpers
```

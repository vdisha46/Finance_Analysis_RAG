# Financial Statement Analysis RAG Application

A complete enterprise-grade financial statement analysis platform built with FastAPI, SQLite, LangChain, Gemini, FAISS, and Bootstrap.

## Features

- Direct dashboard access without login credentials
- Multi-company document upload
- Financial ratio computation
- RAG-powered financial analysis using Gemini + FAISS
- Comparable Company Analysis (CCA)
- Valuation analysis and investment scoring
- Dashboard with charts and executive dashboards
- PDF report generation
- Responsive Bootstrap frontend

## Project Structure

```text
financial_statement_rag/
├── backend/
│   ├── app.py
│   ├── auth.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   └── services/
│       ├── company_comparison.py
│       ├── document_processor.py
│       ├── financial_ratios.py
│       ├── gemini_service.py
│       ├── investment_engine.py
│       ├── report_generator.py
│       ├── valuation.py
│       └── vector_store.py
├── frontend/
│   ├── dashboard.html
│   ├── upload.html
│   ├── documents.html
│   ├── ratios.html
│   ├── insights.html
│   ├── financial_dashboard.html
│   ├── chat.html
│   ├── reports.html
│   ├── comparison.html
│   ├── valuation.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── chart.js
│       ├── chat.js
│       ├── comparison.js
│       ├── dashboard.js
│       ├── insight.js
│       ├── ratio.js
│       ├── upload.js
│       └── valuation.js
├── data/
│   └── sample_financial_data.csv
├── uploads/
├── vectorstore/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation

```bash
cd financial_statement_rag
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Update `.env` with your Gemini API key.

## Run the application

```bash
uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000/

## Notes

- If Gemini API is not configured, the system falls back to a safe mock analysis mode without hallucinating numbers.
- Authentication is disabled. All API routes are open, so only run this app on a trusted local network and do not expose it publicly as-is.
- The app is designed for demo and enterprise prototype use with retrieval-based analysis and document processing.

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

import pandas as pd
from fastapi import Depends, FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sqlalchemy.orm import Session

from backend.config import FRONTEND_DIR, GEMINI_API_KEY, UPLOAD_DIR
from backend.database import get_db, init_db
from backend.models import ChatHistory, Company, Comparison, Document as DbDocument, Insight, Ratio, User
from backend.services.company_comparison import CompanyComparisonEngine
from backend.services.document_processor import DocumentProcessor
from backend.services.financial_ratios import FinancialRatioEngine
from backend.services.gemini_service import generate_response
from backend.services.investment_engine import InvestmentDecisionEngine
from backend.services.report_generator import ReportGenerator
from backend.services.valuation import ValuationEngine
from backend.services.vector_store import VectorStoreManager


def seed_demo_data(db: Session) -> None:
    if db.query(User).count() == 0:
        demo_user = User(
            full_name="Demo Analyst",
            email="analyst@example.com",
            username="demoanalyst",
            password_hash="disabled",
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)

    if db.query(Company).count() == 0:
        tata = Company(company_name="Tata Power", industry="Power", sector="Utilities", ticker="TATAPOWER")
        adani = Company(company_name="Adani Power", industry="Power", sector="Utilities", ticker="ADANIPOWER")
        db.add_all([tata, adani])
        db.commit()

        for company in [tata, adani]:
            doc = DbDocument(
                company_id=company.id,
                file_name=f"{company.company_name.lower().replace(' ', '_')}.pdf",
                file_type="application/pdf",
                financial_year="2024",
                document_type="annual_report",
            )
            db.add(doc)
            db.commit()
            db.refresh(doc)

            ratio = Ratio(
                document_id=doc.id,
                current_ratio=1.67 if company.company_name.startswith("Tata") else 1.72,
                quick_ratio=1.14 if company.company_name.startswith("Tata") else 1.17,
                cash_ratio=0.43 if company.company_name.startswith("Tata") else 0.40,
                gross_margin=0.34 if company.company_name.startswith("Tata") else 0.33,
                operating_margin=0.20 if company.company_name.startswith("Tata") else 0.19,
                net_margin=0.14 if company.company_name.startswith("Tata") else 0.13,
                ebitda_margin=0.28 if company.company_name.startswith("Tata") else 0.26,
                roe=0.18 if company.company_name.startswith("Tata") else 0.15,
                roa=0.08 if company.company_name.startswith("Tata") else 0.07,
                debt_to_equity=0.82 if company.company_name.startswith("Tata") else 0.77,
            )
            insight = Insight(
                document_id=doc.id,
                summary="Strong operating cash generation with steady utility demand profile and improving margin structure.",
                strengths="Consistent revenue, healthy liquidity, disciplined cost management.",
                weaknesses="Exposure to regulatory shifts and capex intensity.",
                risks="Commodity pricing, policy changes, interest rate sensitivity.",
                recommendations="Prioritize operating leverage and balance sheet efficiency while monitoring capex discipline.",
            )
            db.add_all([ratio, insight])
            db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    db = next(get_db())
    init_db()
    seed_demo_data(db)
    db.close()
    yield


app = FastAPI(title="Financial Statement Analysis RAG", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)))


def get_guest_user(db: Session = Depends(get_db)) -> dict[str, Any]:
    user = db.query(User).order_by(User.id).first()
    if user is None:
        raise HTTPException(status_code=503, detail="Guest profile is not available")
    return {"id": user.id, "username": user.username}


@app.get("/")
def root() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/login.html")
def login_page() -> RedirectResponse:
    return RedirectResponse(url="/dashboard.html", status_code=303)


@app.get("/register.html")
def register_page() -> RedirectResponse:
    return RedirectResponse(url="/dashboard.html", status_code=303)


@app.get("/dashboard.html")
def dashboard_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "dashboard.html")


@app.get("/upload.html")
def upload_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "upload.html")


@app.get("/documents.html")
def documents_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "documents.html")


@app.get("/ratios.html")
def ratios_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "ratios.html")


@app.get("/insights.html")
def insights_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "insights.html")


@app.get("/financial_dashboard.html")
def financial_dashboard_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "financial_dashboard.html")


@app.get("/chat.html")
def chat_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "chat.html")


@app.get("/reports.html")
def reports_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "reports.html")


@app.get("/comparison.html")
def comparison_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "comparison.html")


@app.get("/valuation.html")
def valuation_page() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "valuation.html")


@app.post("/api/upload")
async def upload_document(
    company_name: str = Form(...),
    industry: str = Form(""),
    sector: str = Form(""),
    financial_year: str = Form(""),
    report_type: str = Form("annual_report"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user=Depends(get_guest_user),
):
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name is required")
    if file.filename is None or not file.filename.strip():
        raise HTTPException(status_code=400, detail="A file is required")

    company = db.query(Company).filter(Company.company_name == company_name).first()
    if not company:
        company = Company(company_name=company_name, industry=industry, sector=sector, ticker="")
        db.add(company)
        db.commit()
        db.refresh(company)

    safe_name = file.filename.replace(" ", "_")
    file_path = UPLOAD_DIR / safe_name
    file_content = await file.read()
    if not file_content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    document = DbDocument(
        company_id=company.id,
        file_name=safe_name,
        file_type=file.content_type or file.filename.split(".")[-1],
        financial_year=financial_year,
        document_type=report_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    extracted_text = DocumentProcessor.extract_text(file_path)
    split_text = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = split_text.split_text(extracted_text or "No text extracted from the uploaded file.")
    docs = [
        Document(
            page_content=chunk,
            metadata={
                "company_name": company_name,
                "industry": industry,
                "sector": sector,
                "financial_year": financial_year,
                "document_type": report_type,
                "file_name": safe_name,
            },
        )
        for chunk in chunks
    ]

    indexed = False
    if GEMINI_API_KEY:
        vector_store_manager = VectorStoreManager()
        vector_store_manager.add_documents(docs)
        indexed = True

    message = "Document uploaded and indexed successfully" if indexed else "Document uploaded; indexing skipped because GEMINI_API_KEY is not configured."
    return {
        "message": message,
        "document_id": document.id,
        "chunks": len(docs),
        "indexed": indexed,
    }


@app.get("/api/documents")
def get_documents(db: Session = Depends(get_db), user=Depends(get_guest_user)):
    documents = db.query(DbDocument).all()
    result = []
    for item in documents:
        company = db.query(Company).filter(Company.id == item.company_id).first()
        result.append({
            "id": item.id,
            "company_name": company.company_name if company else "Unknown",
            "file_name": item.file_name,
            "file_type": item.file_type,
            "financial_year": item.financial_year,
            "document_type": item.document_type,
        })
    return result


@app.delete("/api/document/{document_id}")
def delete_document(document_id: int, db: Session = Depends(get_db), user=Depends(get_guest_user)):
    document = db.query(DbDocument).filter(DbDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    db.delete(document)
    db.commit()
    return {"message": "Document deleted"}


@app.get("/api/dashboard")
def get_dashboard(db: Session = Depends(get_db), user=Depends(get_guest_user)):
    total_documents = db.query(DbDocument).count()
    total_companies = db.query(Company).count()
    ratios = db.query(Ratio).all()
    avg_roe = round(sum(r.roe for r in ratios if r.roe is not None) / max(len([r for r in ratios if r.roe is not None]), 1), 2) if ratios else 0
    avg_ebitda_margin = round(sum(r.ebitda_margin for r in ratios if r.ebitda_margin is not None) / max(len([r for r in ratios if r.ebitda_margin is not None]), 1), 2) if ratios else 0
    score = 0
    if ratios:
        scores = [
            InvestmentDecisionEngine.compute_financial_health_score({
                "profitability": r.gross_margin if r.gross_margin is not None else 0,
                "liquidity": r.current_ratio if r.current_ratio is not None else 0,
                "solvency": 100 / max((r.debt_to_equity or 0) + 1, 1),
                "cash_flow": 60,
                "growth": 50,
                "valuation": 70,
            })
            for r in ratios
        ]
        score = round(sum(scores) / len(scores), 2)

    return {
        "documents_uploaded": total_documents,
        "companies_analyzed": total_companies,
        "average_roe": avg_roe,
        "average_ebitda_margin": avg_ebitda_margin,
        "financial_health_score": score,
        "recent_uploads": ["sample upload"],
        "recent_queries": ["What is the current ratio?"],
        "recent_comparisons": ["Tata Power vs Adani Power"],
    }


@app.get("/api/ratios")
def get_ratios(db: Session = Depends(get_db), user=Depends(get_guest_user)):
    rows = (
        db.query(Ratio, DbDocument, Company)
        .join(DbDocument, Ratio.document_id == DbDocument.id)
        .outerjoin(Company, DbDocument.company_id == Company.id)
        .order_by(Company.company_name, DbDocument.financial_year, DbDocument.id, Ratio.id)
        .all()
    )
    return [{
        "id": ratio.id,
        "document_id": document.id,
        "company_name": company.company_name if company else "Unknown",
        "financial_year": document.financial_year,
        "file_name": document.file_name,
        "current_ratio": ratio.current_ratio,
        "quick_ratio": ratio.quick_ratio,
        "cash_ratio": ratio.cash_ratio,
        "gross_margin": ratio.gross_margin,
        "operating_margin": ratio.operating_margin,
        "net_margin": ratio.net_margin,
        "ebitda_margin": ratio.ebitda_margin,
        "roe": ratio.roe,
        "roa": ratio.roa,
        "debt_to_equity": ratio.debt_to_equity,
    } for ratio, document, company in rows]


@app.get("/api/insights")
def get_insights(db: Session = Depends(get_db), user=Depends(get_guest_user)):
    rows = db.query(Insight).all()
    return [{
        "id": row.id,
        "summary": row.summary,
        "strengths": row.strengths,
        "weaknesses": row.weaknesses,
        "risks": row.risks,
        "recommendations": row.recommendations,
    } for row in rows]


@app.post("/api/chat")
def chat_with_rag(payload: dict, db: Session = Depends(get_db), user=Depends(get_guest_user)):
    question = str(payload.get("question", "")).strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    vector_store_manager = VectorStoreManager()
    docs = vector_store_manager.search_documents(question, k=5)
    answer = generate_response(question, docs)
    db.add(ChatHistory(user_id=user["id"], question=question, answer=answer))
    db.commit()
    return {"answer": answer, "sources": [{"page_content": doc.page_content[:200], "metadata": doc.metadata} for doc in docs]}


@app.post("/api/compare/upload")
def upload_comparison(payload: dict, db: Session = Depends(get_db), user=Depends(get_guest_user)):
    company_a = str(payload.get("company_a", "")).strip()
    company_b = str(payload.get("company_b", "")).strip()
    if not company_a or not company_b:
        raise HTTPException(status_code=400, detail="Both company names are required")

    comparison = Comparison(company_a=company_a, company_b=company_b)
    db.add(comparison)
    db.commit()
    db.refresh(comparison)
    return {"message": "Comparison created", "id": comparison.id}


@app.post("/api/compare/analyze")
def analyze_comparison(payload: dict, db: Session = Depends(get_db), user=Depends(get_guest_user)):
    company_a = payload.get("company_a", {})
    company_b = payload.get("company_b", {})
    comparison_engine = CompanyComparisonEngine()

    result = {
        "revenue": comparison_engine.compare_revenue(company_a, company_b),
        "profitability": comparison_engine.compare_profitability(company_a, company_b),
        "liquidity": comparison_engine.compare_liquidity(company_a, company_b),
        "solvency": comparison_engine.compare_solvency(company_a, company_b),
        "efficiency": comparison_engine.compare_efficiency(company_a, company_b),
        "cash_flow": comparison_engine.compare_cash_flow(company_a, company_b),
        "growth": comparison_engine.compare_growth(company_a, company_b),
        "valuation": comparison_engine.compare_valuation(company_a, company_b),
        "winner": comparison_engine.generate_winner(company_a, company_b),
        "recommendation": comparison_engine.generate_investment_recommendation(company_a, company_b),
    }
    return result


@app.get("/api/compare/report/{comparison_id}")
def get_comparison_report(comparison_id: int, db: Session = Depends(get_db), user=Depends(get_guest_user)):
    comparison = db.query(Comparison).filter(Comparison.id == comparison_id).first()
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    return {
        "id": comparison.id,
        "company_a": comparison.company_a,
        "company_b": comparison.company_b,
        "winner": comparison.winner,
        "recommendation": comparison.recommendation,
    }


@app.get("/api/compare/history")
def get_comparison_history(db: Session = Depends(get_db), user=Depends(get_guest_user)):
    comparisons = db.query(Comparison).all()
    return [{"id": item.id, "company_a": item.company_a, "company_b": item.company_b, "winner": item.winner} for item in comparisons]


@app.get("/api/profile")
def get_profile(db: Session = Depends(get_db), user=Depends(get_guest_user)):
    db_user = db.query(User).filter(User.id == int(user["id"])).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": db_user.id,
        "full_name": db_user.full_name,
        "email": db_user.email,
        "username": db_user.username,
    }


@app.get("/api/companies")
def get_companies(db: Session = Depends(get_db), user=Depends(get_guest_user)):
    companies = db.query(Company).all()
    return [{"id": c.id, "company_name": c.company_name, "industry": c.industry, "sector": c.sector} for c in companies]


@app.get("/api/valuation")
def get_valuation_metrics() -> dict:
    return {
        "pe_ratio": ValuationEngine.calculate_pe_ratio(120, 15),
        "pb_ratio": ValuationEngine.calculate_pb_ratio(120, 25),
        "ev_ebitda": ValuationEngine.calculate_ev_ebitda(1200, 80),
        "ev_sales": ValuationEngine.calculate_ev_sales(1200, 200),
        "peg_ratio": ValuationEngine.calculate_peg_ratio(15, 0.12),
        "dcf": ValuationEngine.dcf_valuation(150, 0.08, 0.04),
    }


def build_report_data(db: Session) -> dict[str, Any]:
    documents = db.query(DbDocument).order_by(DbDocument.upload_date.desc(), DbDocument.id.desc()).all()
    rows = []
    companies = set()

    for document in documents:
        company = db.get(Company, document.company_id) if document.company_id else None
        company_name = company.company_name if company else "Unknown"
        companies.add(company_name)
        ratio = db.query(Ratio).filter(Ratio.document_id == document.id).order_by(Ratio.id.desc()).first()
        insight = db.query(Insight).filter(Insight.document_id == document.id).order_by(Insight.id.desc()).first()
        rows.append({
            "company_name": company_name,
            "industry": company.industry if company else "",
            "sector": company.sector if company else "",
            "file_name": document.file_name,
            "file_type": document.file_type,
            "financial_year": document.financial_year or "",
            "document_type": document.document_type or "",
            "uploaded_at": document.upload_date.isoformat() if document.upload_date else "",
            "ratios": {
                "current_ratio": ratio.current_ratio if ratio else None,
                "quick_ratio": ratio.quick_ratio if ratio else None,
                "cash_ratio": ratio.cash_ratio if ratio else None,
                "gross_margin": ratio.gross_margin if ratio else None,
                "operating_margin": ratio.operating_margin if ratio else None,
                "net_margin": ratio.net_margin if ratio else None,
                "ebitda_margin": ratio.ebitda_margin if ratio else None,
                "roe": ratio.roe if ratio else None,
                "roa": ratio.roa if ratio else None,
                "debt_to_equity": ratio.debt_to_equity if ratio else None,
            },
            "insights": {
                "summary": insight.summary if insight else "",
                "strengths": insight.strengths if insight else "",
                "weaknesses": insight.weaknesses if insight else "",
                "risks": insight.risks if insight else "",
                "recommendations": insight.recommendations if insight else "",
            },
        })

    return {
        "report_name": "Financial Statement Analysis Report",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "summary": {"document_count": len(rows), "company_count": len(companies)},
        "documents": rows,
    }


@app.get("/api/reports")
def get_reports(
    export_format: str = Query("preview", alias="format", pattern="^(preview|pdf|xlsx)$"),
    db: Session = Depends(get_db),
    user=Depends(get_guest_user),
):
    report = build_report_data(db)
    if export_format == "preview":
        return report

    if export_format == "pdf":
        lines = [
            f"Generated: {report['generated_at']}",
            f"Companies analyzed: {report['summary']['company_count']}",
            f"Documents included: {report['summary']['document_count']}",
            "",
            "Document Analysis",
        ]
        for row in report["documents"]:
            lines.extend([
                "",
                f"Company: {escape(row['company_name'])}",
                f"File: {escape(row['file_name'])}",
                f"Financial year: {escape(row['financial_year'] or 'Not specified')}",
                f"Document type: {escape(row['document_type'] or 'Not specified')}",
            ])
            for metric, value in row["ratios"].items():
                if value is not None:
                    lines.append(f"{escape(metric.replace('_', ' ').title())}: {value}")
            for label, value in row["insights"].items():
                if value:
                    lines.append(f"{escape(label.title())}: {escape(value)}")

        pdf_bytes = ReportGenerator.generate_pdf_report(report["report_name"], "\n".join(lines))
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": 'attachment; filename="financial_statement_analysis.pdf"'},
        )

    document_columns = [
        "company_name", "industry", "sector", "file_name", "file_type",
        "financial_year", "document_type", "uploaded_at",
    ]
    ratio_columns = list(report["documents"][0]["ratios"]) if report["documents"] else []
    insight_columns = list(report["documents"][0]["insights"]) if report["documents"] else []
    document_rows = [{key: row[key] for key in document_columns} for row in report["documents"]]
    ratio_rows = [
        {"company_name": row["company_name"], "financial_year": row["financial_year"], **row["ratios"]}
        for row in report["documents"]
    ]
    insight_rows = [
        {"company_name": row["company_name"], "financial_year": row["financial_year"], **row["insights"]}
        for row in report["documents"]
    ]
    workbook = BytesIO()
    with pd.ExcelWriter(workbook, engine="openpyxl") as writer:
        pd.DataFrame(document_rows, columns=document_columns).to_excel(writer, sheet_name="Documents", index=False)
        pd.DataFrame(ratio_rows, columns=["company_name", "financial_year", *ratio_columns]).to_excel(writer, sheet_name="Ratios", index=False)
        pd.DataFrame(insight_rows, columns=["company_name", "financial_year", *insight_columns]).to_excel(writer, sheet_name="Insights", index=False)
    workbook.seek(0)
    return StreamingResponse(
        workbook,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="financial_statement_analysis.xlsx"'},
    )

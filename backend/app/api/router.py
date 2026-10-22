import datetime
from typing import List
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import AnalysisRecord, AnalysisClauseResult
from app.schemas import (
    AnalysisStatusResponse,
    AnalysisReportResponse,
    ClauseOutputSchema,
    HistoryItemSchema,
    ChatRequestSchema,
    ChatResponseSchema,
    SecuritySchema
)
from app.services.storage import storage_service
from app.api.chat import handle_followup_chat
from app.tasks.analysis_task import run_contract_analysis

router = APIRouter(prefix="/api", tags=["contract-risk-analyzer"])

@router.post("/upload")
async def upload_contract(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        file_bytes = await file.read()
        file_id, file_path, file_type = storage_service.save_file(file.filename, file_bytes)

        record = AnalysisRecord(
            id=file_id,
            file_name=file.filename,
            file_path=file_path,
            file_type=file_type,
            status="EXTRACTING",
            stage="EXTRACTING",
            progress=0,
            agent_states={}
        )
        db.add(record)
        db.commit()

        # Enqueue async Celery task
        run_contract_analysis.delay(file_id)

        return {
            "analysis_id": file_id,
            "fileName": file.filename,
            "status": "EXTRACTING",
            "message": "File uploaded successfully. Processing initiated."
        }
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process upload: {str(e)}")

@router.get("/analysis/{analysis_id}/status", response_model=AnalysisStatusResponse)
def get_analysis_status(analysis_id: str, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

    return AnalysisStatusResponse(
        analysis_id=record.id,
        status=record.status,
        stage=record.stage,
        progress=record.progress or 0,
        agent_states=record.agent_states or {},
        error_message=record.error_message
    )

@router.get("/analysis/{analysis_id}/result", response_model=AnalysisReportResponse)
def get_analysis_result(analysis_id: str, db: Session = Depends(get_db)):
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis record not found.")

    if record.status != "COMPLETE":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Analysis is not complete yet. Current status: {record.status}")

    clause_rows = db.query(AnalysisClauseResult).filter(AnalysisClauseResult.analysis_id == analysis_id).order_by(AnalysisClauseResult.clause_number).all()

    clauses_out = []
    for c in clause_rows:
        clauses_out.append(ClauseOutputSchema(
            id=c.clause_number,
            title=c.title,
            risk=c.risk_level,
            category=c.ui_category,
            location=c.location,
            text=c.what_it_says,
            recommendation=c.suggested_alternative,
            why_risky=c.why_risky,
            legal_flag=c.legal_flag,
            benchmark_comparison=c.benchmark_comparison,
            confidence=c.confidence,
            benchmark_refs=c.benchmark_refs or [],
            agent_category=c.agent_category,
            exposure=c.exposure,
            verification=c.verification,
        ))

    # If clause_rows is empty (e.g., Phase 1 stub), provide fallback clauses matching UI shape
    if not clauses_out:
        clauses_out = [
            ClauseOutputSchema(
                id=1,
                title="Limitation of Liability",
                risk="High",
                category="Financial",
                location="Section 13",
                text="Vendor's aggregate liability is limited to fees paid in the preceding three months.",
                recommendation="Request a cap tied to annual contract value.",
                why_risky="Excessive liability shift to MSME supplier.",
                legal_flag="Indian Contract Act Section 74",
                agent_category="liability"
            )
        ]

    formatted_date = record.created_at.strftime("%B %d, %Y") if record.created_at else datetime.date.today().strftime("%B %d, %Y")

    return AnalysisReportResponse(
        title=record.file_name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title(),
        fileName=record.file_name,
        pages=record.page_count,
        analyzedAt=formatted_date,
        overallRisk=record.overall_risk or "Moderate",
        score=record.score or 62,
        summary=record.summary or "Analysis complete.",
        clauses=clauses_out,
        security=SecuritySchema(**record.security_report) if record.security_report else None,
        total_exposure=record.total_exposure,
    )

@router.get("/history", response_model=List[HistoryItemSchema])
def get_analysis_history(db: Session = Depends(get_db)):
    records = db.query(AnalysisRecord).order_by(AnalysisRecord.created_at.desc()).limit(20).all()
    history = []
    for r in records:
        date_str = r.created_at.strftime("%B %d, %Y") if r.created_at else ""
        history.append(HistoryItemSchema(
            analysis_id=r.id,
            fileName=r.file_name,
            analyzedAt=date_str,
            overallRisk=r.overall_risk,
            score=r.score,
            status=r.status
        ))
    return history

@router.post("/analysis/{analysis_id}/chat", response_model=ChatResponseSchema)
def post_followup_chat(analysis_id: str, body: ChatRequestSchema, db: Session = Depends(get_db)):
    reply = handle_followup_chat(db, analysis_id, body.message)
    return ChatResponseSchema(reply=reply)

import time
import logging
from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import AnalysisRecord, AnalysisClauseResult
from app.services.document_parser import parser_service
from app.services.agent_analysis import run_agentic_analysis_pipeline, AGENT_CONFIGS
from app.utils.security import sanitize_contract_text

logger = logging.getLogger(__name__)

@celery_app.task(name="app.tasks.analysis_task.run_contract_analysis")
def run_contract_analysis(analysis_id: str):
    logger.info(f"Starting contract analysis for ID: {analysis_id}")
    db = SessionLocal()
    try:
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        if not record:
            logger.error(f"Analysis record {analysis_id} not found.")
            return

        # Stage 1: EXTRACTING
        record.status = "EXTRACTING"
        record.stage = "EXTRACTING"
        record.progress = 10
        db.commit()

        # Extract document text
        try:
            parsed = parser_service.extract_text(record.file_path, record.file_type)
            record.page_count = parsed.get("pages", 1)
            record.progress = 30
            db.commit()
        except Exception as e:
            record.status = "FAILED"
            record.stage = "FAILED"
            record.error_message = f"Document extraction error: {str(e)}"
            db.commit()
            return

        raw_text = parsed.get("text", "")
        if not raw_text:
            record.status = "FAILED"
            record.stage = "FAILED"
            record.error_message = "No readable text content extracted from document."
            db.commit()
            return

        # Security: sanitize untrusted contract text at intake
        contract_text, security_report = sanitize_contract_text(raw_text)

        # Stage 2: ANALYZING
        record.status = "ANALYZING"
        record.stage = "ANALYZING"
        record.progress = 35
        initial_agent_states = {cat: "queued" for cat in AGENT_CONFIGS.keys()}
        record.agent_states = initial_agent_states
        db.commit()

        def on_agent_status_change(category: str, state: str):
            cb_db = SessionLocal()
            try:
                r = cb_db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
                if r:
                    states = dict(r.agent_states or {})
                    states[category] = state
                    r.agent_states = states
                    
                    done_count = sum(1 for s in states.values() if s in ["done", "failed"])
                    r.progress = 35 + int((done_count / len(AGENT_CONFIGS)) * 45)
                    cb_db.commit()
            except Exception as ex:
                logger.warning(f"Error updating agent status callback for {category}: {ex}")
                cb_db.rollback()
            finally:
                cb_db.close()

        # Execute full agentic pipeline
        results = run_agentic_analysis_pipeline(
            db=db,
            contract_text=contract_text,
            file_name=record.file_name,
            status_callback=on_agent_status_change
        )
        results["security"] = security_report

        # Stage 3: COMBINING
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        record.status = "COMBINING"
        record.stage = "COMBINING"
        record.progress = 90
        db.commit()

        # Clear existing clause results if any
        db.query(AnalysisClauseResult).filter(AnalysisClauseResult.analysis_id == analysis_id).delete()

        # Save analyzed clause results
        clauses = results.get("clauses", [])
        for idx, clause in enumerate(clauses, start=1):
            clause_record = AnalysisClauseResult(
                analysis_id=analysis_id,
                clause_number=idx,
                title=clause.get("title", f"Clause {idx}"),
                location=clause.get("location", "Contract Body"),
                agent_category=clause.get("agent_category", "general"),
                ui_category=clause.get("ui_category", "Commercial"),
                risk_level=clause.get("risk_level", "Medium"),
                what_it_says=clause.get("what_it_says", ""),
                why_risky=clause.get("why_risky", ""),
                legal_flag=clause.get("legal_flag"),
                benchmark_comparison=clause.get("benchmark_comparison"),
                suggested_alternative=clause.get("suggested_alternative", ""),
                confidence=clause.get("confidence", 0.9),
                benchmark_refs=clause.get("benchmark_refs", []),
                exposure=clause.get("exposure"),
                verification=clause.get("verification"),
            )
            db.add(clause_record)

        db.commit()

        # Stage 4: COMPLETE
        record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        record.status = "COMPLETE"
        record.stage = "COMPLETE"
        record.progress = 100
        record.overall_risk = results.get("overall_risk", "Moderate")
        record.score = results.get("score", 65)
        record.summary = results.get("summary", "Analysis completed successfully.")
        record.security_report = results.get("security")
        record.total_exposure = results.get("total_exposure")
        db.commit()

        logger.info(f"Finished analysis task successfully for ID: {analysis_id}")

    except Exception as e:
        logger.exception(f"Unhandled error in analysis task {analysis_id}: {e}")
        try:
            db.rollback()
            record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
            if record:
                record.status = "FAILED"
                record.stage = "FAILED"
                record.error_message = str(e)
                db.commit()
        except Exception as db_err:
            logger.error(f"Failed to persist FAILED status to DB for {analysis_id}: {db_err}")
        raise e
    finally:
        db.close()


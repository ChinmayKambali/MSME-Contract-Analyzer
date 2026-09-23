import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal
from app.models import AnalysisRecord, AnalysisClauseResult
from app.tasks.analysis_task import run_contract_analysis
from app.api.router import get_analysis_status, get_analysis_result

def test_success_flow():
    db = SessionLocal()
    try:
        # Create a test analysis record
        record = AnalysisRecord(
            file_name="test_success.docx",
            file_type="docx",
            file_path=str(Path(__file__).resolve().parent.parent / "tests" / "fixtures" / "risky_msme_contract.docx"),
            status="QUEUED",
            stage="QUEUED"
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        
        analysis_id = record.id
        print(f"Created Test Record ID: {analysis_id}")
        
        # Run Celery task directly (synchronously in-process)
        print("Executing run_contract_analysis task with stubbed success...")
        run_contract_analysis(analysis_id)
            
        # Re-query record from DB
        db.expire_all()
        updated = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        
        print("\n--- POSTGRES DB STATE AFTER SUCCESS ---")
        print(f"Record Status: {updated.status}")
        print(f"Record Stage:  {updated.stage}")
        print(f"Progress:      {updated.progress}%")
        print(f"Overall Risk:  {updated.overall_risk}")
        print(f"Score:         {updated.score}")
        print(f"Agent States:  {updated.agent_states}")
        
        # Test API Status & Result Endpoints
        api_status = get_analysis_status(analysis_id=analysis_id, db=db)
        api_result = get_analysis_result(analysis_id=analysis_id, db=db)
        
        print("\n--- API STATUS ENDPOINT RESPONSE ---")
        print(f"API status response: {api_status.model_dump()}")
        
        print("\n--- API RESULT ENDPOINT RESPONSE ---")
        print(f"API report summary: {api_result.summary}")
        print(f"Clauses returned: {len(api_result.clauses)}")
        
        # Assertions
        assert updated.status == "COMPLETE", f"Expected COMPLETE status, got {updated.status}"
        assert updated.stage == "COMPLETE", f"Expected COMPLETE stage, got {updated.stage}"
        assert updated.progress == 100, f"Expected progress 100, got {updated.progress}"
        assert len(api_result.clauses) == 1, "Expected 1 clause from stub"
        
        print("\n========================================================")
        print("   SUCCESS! Zero-Quota Success Handling Verified.")
        print("========================================================")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_success_flow()

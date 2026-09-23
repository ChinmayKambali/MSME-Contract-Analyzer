import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import SessionLocal
from app.models import AnalysisRecord
from app.tasks.analysis_task import run_contract_analysis
from app.api.router import get_analysis_status

def test_failure_flow():
    db = SessionLocal()
    try:
        # Create a test analysis record
        record = AnalysisRecord(
            file_name="test_failure.docx",
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
        print("Executing run_contract_analysis task with simulated failure...")
        try:
            run_contract_analysis(analysis_id)
        except Exception as task_err:
            print(f"Caught re-raised task exception as expected: {task_err}")
            
        # Re-query record from DB
        db.expire_all()
        updated = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        
        print("\n--- POSTGRES DB STATE AFTER FAILURE ---")
        print(f"Record Status: {updated.status}")
        print(f"Record Stage:  {updated.stage}")
        print(f"Error Message: {updated.error_message}")
        
        # Test API Status Response
        api_status = get_analysis_status(analysis_id=analysis_id, db=db)
        print("\n--- API STATUS ENDPOINT RESPONSE ---")
        print(f"API status response: {api_status.model_dump()}")
        
        # Assertions
        assert updated.status == "FAILED", f"Expected FAILED status, got {updated.status}"
        assert updated.stage == "FAILED", f"Expected FAILED stage, got {updated.stage}"
        assert "Simulated pipeline failure" in updated.error_message, "Error message not persisted!"
        print("\n========================================================")
        print("   SUCCESS! Zero-Quota Failure Handling Verified.")
        print("========================================================")
        
    finally:
        db.close()

if __name__ == "__main__":
    test_failure_flow()

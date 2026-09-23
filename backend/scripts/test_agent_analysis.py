import sys
import uuid
import logging
from pathlib import Path

# Add backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.db import SessionLocal
from app.models import AnalysisRecord, AnalysisClauseResult
from app.tasks.analysis_task import run_contract_analysis

logging.basicConfig(level=logging.INFO)

def main():
    print("\n========================================================")
    print("   PHASE 2: AGENTIC ANALYSIS END-TO-END VERIFICATION")
    print("========================================================")

    # Locate sample docx benchmark file for testing
    benchmark_dir = ROOT_DIR.parent / "MSME BENCHMARK LIB"
    sample_files = list(benchmark_dir.glob("MSME-BENCHMARK-*.docx"))
    if not sample_files:
        print(f"[ERROR] No benchmark docx files found in {benchmark_dir}")
        sys.exit(1)

    sample_file = sample_files[0]
    print(f"Testing Analysis Pipeline on contract file: {sample_file.name}")

    db = SessionLocal()
    try:
        # Create test analysis record
        analysis_id = str(uuid.uuid4())
        record = AnalysisRecord(
            id=analysis_id,
            file_name=sample_file.name,
            file_path=str(sample_file),
            file_type="docx",
            status="EXTRACTING",
            stage="EXTRACTING",
            progress=0,
            agent_states={}
        )
        db.add(record)
        db.commit()

        print(f"Created Test AnalysisRecord ID: {analysis_id}")
        print("Running full agentic analysis task synchronously...\n")

        # Run task synchronously
        run_contract_analysis(analysis_id)

        # Retrieve resulting record
        updated_record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        print(f"Final Status:      {updated_record.status}")
        print(f"Final Stage:       {updated_record.stage}")
        print(f"Final Progress:    {updated_record.progress}%")
        print(f"Overall Risk:      {updated_record.overall_risk}")
        print(f"Contract Score:    {updated_record.score}/100")
        print(f"Agent States:      {updated_record.agent_states}")
        print(f"Executive Summary: \"{updated_record.summary}\"\n")

        assert updated_record.status == "COMPLETE", f"Expected COMPLETE, got {updated_record.status}"
        assert updated_record.overall_risk == "Low", f"Expected Low risk for benchmark contract, got {updated_record.overall_risk}"
        assert 0 <= updated_record.score <= 30, f"Expected low risk score (0-30), got {updated_record.score}"

        # Check analyzed clauses
        clause_results = db.query(AnalysisClauseResult).filter(AnalysisClauseResult.analysis_id == analysis_id).order_by(AnalysisClauseResult.clause_number).all()
        print(f"Total Detected Risk Clauses: {len(clause_results)}")

        for idx, clause in enumerate(clause_results, start=1):
            print(f"\n--- Clause {idx}: {clause.title} [{clause.risk_level} Risk] ---")
            print(f"  UI Category:  {clause.ui_category} (Agent: {clause.agent_category})")
            print(f"  Location:     {clause.location}")
            print(f"  What it says: {clause.what_it_says[:120]}...")
            print(f"  Why risky:    {clause.why_risky[:120]}...")
            print(f"  Legal Flag:   {clause.legal_flag}")
            print(f"  Alternative:  {clause.suggested_alternative[:120]}...")

        print("\n========================================================")
        print("   SUCCESS! Agentic Analysis verification passed.")
        print("========================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    main()

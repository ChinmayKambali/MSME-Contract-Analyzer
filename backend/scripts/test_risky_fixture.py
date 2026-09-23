import sys
import json
import uuid
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.db import SessionLocal
from app.models import AnalysisRecord, AnalysisClauseResult
from app.tasks.analysis_task import run_contract_analysis

logging.basicConfig(level=logging.INFO)

def main():
    print("\n========================================================")
    print("   RISKY FIXTURE CONTRACT END-TO-END VERIFICATION")
    print("========================================================")

    fixture_path = ROOT_DIR / "tests" / "fixtures" / "risky_msme_contract.docx"
    assert fixture_path.exists(), f"Fixture file not found: {fixture_path}"

    print(f"Testing Analysis Pipeline on Risky Fixture: {fixture_path.name}")

    db = SessionLocal()
    try:
        analysis_id = str(uuid.uuid4())
        record = AnalysisRecord(
            id=analysis_id,
            file_name=fixture_path.name,
            file_path=str(fixture_path),
            file_type="docx",
            status="EXTRACTING",
            stage="EXTRACTING",
            progress=0,
            agent_states={}
        )
        db.add(record)
        db.commit()

        print(f"Created AnalysisRecord ID: {analysis_id}")
        print("Executing full agentic pipeline...\n")

        run_contract_analysis(analysis_id)

        updated_record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
        clause_results = db.query(AnalysisClauseResult).filter(AnalysisClauseResult.analysis_id == analysis_id).order_by(AnalysisClauseResult.clause_number).all()

        formatted_clauses = []
        for c in clause_results:
            formatted_clauses.append({
                "id": c.clause_number,
                "title": c.title,
                "risk": c.risk_level,
                "category": c.ui_category,
                "agent_category": c.agent_category,
                "location": c.location,
                "text": c.what_it_says,
                "why_risky": c.why_risky,
                "legal_flag": c.legal_flag,
                "benchmark_comparison": c.benchmark_comparison,
                "recommendation": c.suggested_alternative,
                "confidence": c.confidence,
                "benchmark_refs": c.benchmark_refs or []
            })

        output_json = {
            "title": "Abusive Master Services Agreement For MSME Vendor",
            "fileName": updated_record.file_name,
            "pages": updated_record.page_count,
            "status": updated_record.status,
            "overallRisk": updated_record.overall_risk,
            "score": updated_record.score,
            "summary": updated_record.summary,
            "agent_states": updated_record.agent_states,
            "clauses": formatted_clauses
        }

        print("-------------------- ACTUAL OUTPUT JSON --------------------")
        print(json.dumps(output_json, indent=2))
        print("------------------------------------------------------------\n")

        print(f"Final Status:       {updated_record.status}")
        print(f"Overall Risk Level: {updated_record.overall_risk}")
        print(f"Contract Score:     {updated_record.score}/100")
        print(f"Detected Clauses:   {len(formatted_clauses)}")

        assert updated_record.status == "COMPLETE", "Analysis task failed"
        assert updated_record.overall_risk == "High", f"Expected High risk, got {updated_record.overall_risk}"
        assert 70 <= updated_record.score <= 100, f"Expected high risk score (70-100) for risky contract, got {updated_record.score}"
        assert len(formatted_clauses) >= 4, f"Expected at least 4 detected risk clauses, got {len(formatted_clauses)}"

        print("\n========================================================")
        print("   SUCCESS! Risky Fixture contract verification passed.")
        print("========================================================\n")

    finally:
        db.close()

if __name__ == "__main__":
    main()

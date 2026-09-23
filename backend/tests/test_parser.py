from pathlib import Path
from app.services.document_parser import parser_service
from app.services.benchmark_ingestion import parse_docx_clauses, classify_heading

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
BENCHMARK_FILE = ROOT_DIR / "MSME BENCHMARK LIB" / "MSME-BENCHMARK-1.docx"

def test_docx_parser():
    assert BENCHMARK_FILE.exists(), f"Benchmark file should exist at {BENCHMARK_FILE}"
    
    parsed = parser_service.extract_text(str(BENCHMARK_FILE), "docx")
    assert "text" in parsed
    assert parsed["pages"] > 0
    assert len(parsed["sections"]) > 0

def test_clause_splitting_and_classification():
    clauses = parse_docx_clauses(BENCHMARK_FILE)
    assert len(clauses) > 5
    
    categories = [c["category"] for c in clauses]
    assert "payment_terms" in categories
    assert "liability" in categories
    assert "termination" in categories

def test_heading_classifier():
    assert classify_heading("6. PAYMENT TERMS") == "payment_terms"
    assert classify_heading("13. LIMITATION OF LIABILITY") == "liability"
    assert classify_heading("11. INTELLECTUAL PROPERTY") == "ip_ownership"
    assert classify_heading("14. PENALTY AND LIQUIDATED DAMAGES") == "penalty_ld"
    assert classify_heading("17. DISPUTE RESOLUTION") == "dispute_resolution"
    assert classify_heading("15. TERM AND TERMINATION") == "termination"

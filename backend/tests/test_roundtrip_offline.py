"""
Offline roundtrip test: exposure, verification, total_exposure survive
the full path from saved DB row values → API response schema.
No database or network calls are made.
"""
import datetime
import pytest
from app.schemas import (
    AnalysisReportResponse,
    ClauseOutputSchema,
    ExposureSchema,
    VerificationSchema,
)


# ---------------------------------------------------------------------------
# Fake "DB row" objects – simple namespaces that mirror model attributes
# ---------------------------------------------------------------------------

class FakeClauseRow:
    def __init__(self, exposure, verification):
        self.clause_number = 1
        self.title = "Payment Terms"
        self.risk_level = "High"
        self.ui_category = "Financial"
        self.location = "Section 4"
        self.what_it_says = "Payment within 90 days."
        self.suggested_alternative = "Reduce to 45 days per MSMED Act."
        self.why_risky = "Violates MSMED 45-day limit."
        self.legal_flag = "MSMED Act Section 15"
        self.benchmark_comparison = None
        self.confidence = 0.95
        self.benchmark_refs = []
        self.agent_category = "payment"
        self.exposure = exposure          # dict or None
        self.verification = verification  # dict or None


class FakeRecord:
    def __init__(self, total_exposure):
        self.id = "fake-id-001"
        self.file_name = "test_contract.pdf"
        self.page_count = 5
        self.created_at = datetime.datetime(2025, 1, 1)
        self.status = "COMPLETE"
        self.overall_risk = "High"
        self.score = 72
        self.summary = "Risky contract."
        self.security_report = None
        self.total_exposure = total_exposure  # dict or None


# ---------------------------------------------------------------------------
# Helper: mimic exactly what router.get_analysis_result builds
# ---------------------------------------------------------------------------

def build_response(record: FakeRecord, clause_rows) -> AnalysisReportResponse:
    formatted_date = record.created_at.strftime("%B %d, %Y")
    clauses_out = [
        ClauseOutputSchema(
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
        )
        for c in clause_rows
    ]
    return AnalysisReportResponse(
        title=record.file_name.rsplit(".", 1)[0].replace("-", " ").replace("_", " ").title(),
        fileName=record.file_name,
        pages=record.page_count,
        analyzedAt=formatted_date,
        overallRisk=record.overall_risk or "Moderate",
        score=record.score or 62,
        summary=record.summary or "Analysis complete.",
        clauses=clauses_out,
        security=None,
        total_exposure=record.total_exposure,
    )


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

SAMPLE_EXPOSURE = {
    "mode": "actual",
    "amount_inr": 12500.0,
    "basis": "3 MCA compound rate on INR 50000 for 90 days",
    "contract_days": 90,
    "statutory_days": 45,
    "extra_days": 45,
    "rate_used_pct": 10.25,
    "rate_date": "2025-04-01",
    "note": "Buyer owes compound interest on delayed payment.",
}

SAMPLE_VERIFICATION = {
    "quote_verified": True,
    "benchmark_verified": True,
    "confidence": "high",
    "flags": [],
}

SAMPLE_TOTAL_EXPOSURE = {
    "mode": "actual",
    "clause_count": 1,
    "total_amount_inr": 12500.0,
    "note": "Sum of per-clause exposures.",
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestExposureRoundtrip:
    """per-clause exposure survives fake row → response schema"""

    def test_clause_exposure_is_present(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        clause = resp.clauses[0]
        assert clause.exposure is not None, "exposure must not be None"

    def test_clause_exposure_mode(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        # exposure may come back as ExposureSchema or plain dict depending on Pydantic coercion
        exp = resp.clauses[0].exposure
        mode = exp.mode if hasattr(exp, "mode") else exp["mode"]
        assert mode == "actual"

    def test_clause_exposure_amount_inr(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        exp = resp.clauses[0].exposure
        amount = exp.amount_inr if hasattr(exp, "amount_inr") else exp["amount_inr"]
        assert amount == pytest.approx(12500.0)


class TestVerificationRoundtrip:
    """per-clause verification survives fake row → response schema"""

    def test_clause_verification_is_present(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        assert resp.clauses[0].verification is not None, "verification must not be None"

    def test_clause_verification_quote_verified(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        ver = resp.clauses[0].verification
        qv = ver.quote_verified if hasattr(ver, "quote_verified") else ver["quote_verified"]
        assert qv is True

    def test_clause_verification_confidence(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        ver = resp.clauses[0].verification
        conf = ver.confidence if hasattr(ver, "confidence") else ver["confidence"]
        assert conf == "high"


class TestTotalExposureRoundtrip:
    """summary-level total_exposure survives fake record → response schema"""

    def test_total_exposure_is_present(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=SAMPLE_TOTAL_EXPOSURE)
        resp = build_response(record, [row])
        assert resp.total_exposure is not None, "total_exposure must not be None"

    def test_total_exposure_amount(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=SAMPLE_TOTAL_EXPOSURE)
        resp = build_response(record, [row])
        assert resp.total_exposure["total_amount_inr"] == pytest.approx(12500.0)

    def test_total_exposure_mode(self):
        row = FakeClauseRow(exposure=SAMPLE_EXPOSURE, verification=SAMPLE_VERIFICATION)
        record = FakeRecord(total_exposure=SAMPLE_TOTAL_EXPOSURE)
        resp = build_response(record, [row])
        assert resp.total_exposure["mode"] == "actual"

    def test_total_exposure_none_when_absent(self):
        row = FakeClauseRow(exposure=None, verification=None)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        assert resp.total_exposure is None

    def test_clause_exposure_none_when_absent(self):
        row = FakeClauseRow(exposure=None, verification=None)
        record = FakeRecord(total_exposure=None)
        resp = build_response(record, [row])
        assert resp.clauses[0].exposure is None
        assert resp.clauses[0].verification is None

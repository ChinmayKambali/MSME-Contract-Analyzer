"""
Tests for the MSMED financial exposure calculator.
No network calls; no LLM calls.
"""
import math
import pytest
from unittest.mock import patch


# ------------------------------------------------------------------ #
# Helpers – compute expected value independently using the same formula
# ------------------------------------------------------------------ #
_BANK_RATE_PCT = 5.75
_RATE_USED_PCT = 3 * _BANK_RATE_PCT          # 17.25 %
_STATUTORY_DAYS = 45
_NORMALIZED_BASE = 100_000.0


def _expected_interest(base: float, rate_pct: float, extra_days: int) -> float:
    months = extra_days / 30.0
    monthly_rate = rate_pct / 12.0 / 100.0
    return base * ((1.0 + monthly_rate) ** months - 1.0)


# ------------------------------------------------------------------ #
# Unit tests – compute_exposure
# ------------------------------------------------------------------ #

def test_payment_90_normalized():
    """payment_days=90, no contract value → normalized mode, amount ≈ expected formula."""
    from app.utils.exposure import compute_exposure

    result = compute_exposure(payment_days=90)
    assert result["mode"] == "normalized"
    assert result["extra_days"] == 45

    extra_days = 90 - _STATUTORY_DAYS          # 45
    expected = _expected_interest(_NORMALIZED_BASE, _RATE_USED_PCT, extra_days)
    # Report if it differs from the spec's stated ~2164
    spec_stated = 2164.0
    diff_from_spec = abs(expected - spec_stated)
    print(
        f"\n[test_payment_90_normalized] independently computed: {expected:.4f}; "
        f"spec states ~{spec_stated}; diff={diff_from_spec:.4f}"
    )

    # Primary assertion: our implementation matches the formula (within Rs 1)
    assert abs(result["amount_inr"] - expected) < 1.0, (
        f"amount_inr={result['amount_inr']:.4f} differs from formula {expected:.4f}"
    )


def test_payment_30_within_limit():
    """payment_days=30 → amount 0 (within statutory limit)."""
    from app.utils.exposure import compute_exposure

    result = compute_exposure(payment_days=30)
    assert result["amount_inr"] == 0.0
    assert result["extra_days"] == 0
    assert "within" in result["note"].lower() or "limit" in result["note"].lower()


def test_payment_null_not_computable():
    """payment_days=None → not_computable."""
    from app.utils.exposure import compute_exposure

    result = compute_exposure(payment_days=None)
    assert result["mode"] == "not_computable"
    assert result["amount_inr"] is None
    assert "null" in result["note"].lower() or "payment_days" in result["note"].lower()


def test_actual_mode_five_lakh():
    """contract_value_inr=500000, payment_days=90 → actual mode, amount == 5× per-lakh."""
    from app.utils.exposure import compute_exposure

    result_actual = compute_exposure(payment_days=90, contract_value_inr=500_000)
    result_norm = compute_exposure(payment_days=90)  # per lakh

    assert result_actual["mode"] == "actual"
    assert result_norm["mode"] == "normalized"

    # 5 lakh = 5 × 1 lakh → amounts must be proportional
    assert abs(result_actual["amount_inr"] - 5 * result_norm["amount_inr"]) < 1.0, (
        f"actual={result_actual['amount_inr']:.4f}, 5×norm={5*result_norm['amount_inr']:.4f}"
    )


def test_penalty_pct_no_contract_value():
    """penalty_pct=10 with no contract value → Rs 10,000 per lakh noted."""
    from app.utils.exposure import compute_exposure

    result = compute_exposure(payment_days=45, penalty_pct=10.0)
    # 10% of 1,00,000 = 10,000
    assert "10000" in result["note"].replace(",", "") or "10,000" in result["note"], (
        f"Penalty not found in note: {result['note']}"
    )


# ------------------------------------------------------------------ #
# Pipeline integration test
# ------------------------------------------------------------------ #

def test_pipeline_exposure_attached_to_payment_finding():
    """
    Run the agentic pipeline with generate_json monkeypatched to return fixed JSON.
    Assert that the payment_terms finding has exposure attached.
    """
    fixed_payment_clause = {
        "clauses": [
            {
                "title": "90-day payment terms",
                "risk_level": "High",
                "location": "Clause 5.1",
                "what_it_says": "Payment within 90 days of invoice.",
                "why_risky": "Exceeds MSMED Act 45-day limit.",
                "legal_flag": "MSMED Act 2006 Sec 15",
                "benchmark_comparison": "Standard is 45 days.",
                "suggested_alternative": "Reduce to 45 days.",
                "confidence": 0.95,
                "payment_days": 90,
                "penalty_pct": None,
                "liability_cap_multiple": None,
                "contract_value_inr": None,
            }
        ]
    }
    empty_clauses = {"clauses": []}

    import json
    import importlib

    # Map category → response JSON
    _responses = {
        "payment_terms": json.dumps(fixed_payment_clause),
    }
    _default = json.dumps(empty_clauses)

    call_count = {"n": 0}

    def _fake_generate_json(prompt, system_instruction=None, model_name=None):
        # Determine which category this call is for via system_instruction content
        for cat_key, response in _responses.items():
            if cat_key.replace("_", " ") in (system_instruction or "").lower() or \
               cat_key in (system_instruction or "").lower():
                return response
        return _default

    def _fake_generate_text(prompt, system_instruction=None, model_name=None):
        return "Monkeypatched summary."

    def _fake_retrieve(db, query_text, category, top_k, threshold):
        return []

    # Create a minimal fake DB session
    class _FakeDB:
        pass

    with patch("app.services.agent_analysis.generate_json", side_effect=_fake_generate_json), \
         patch("app.services.agent_analysis.generate_text", side_effect=_fake_generate_text), \
         patch("app.services.agent_analysis.retrieve_benchmark_clauses", side_effect=_fake_retrieve), \
         patch("app.services.agent_analysis.resolve_active_model", return_value="fake-model"), \
         patch("app.services.agent_analysis._GEMINI_SEMAPHORE"):  # skip semaphore acquire

        import app.services.agent_analysis as aa

        result = aa.run_agentic_analysis_pipeline(
            db=_FakeDB(),
            contract_text="Payment shall be made within 90 days of invoice date.",
            file_name="test_contract.pdf",
        )

    # Find the payment_terms finding
    payment_clauses = [
        c for c in result["clauses"]
        if c.get("agent_category") == "payment_terms"
    ]
    assert payment_clauses, "No payment_terms finding found in pipeline output."

    pf = payment_clauses[0]
    assert "exposure" in pf, "exposure not attached to payment finding"
    assert pf["exposure"] is not None, "exposure is None"
    assert pf["exposure"]["mode"] in ("normalized", "actual"), (
        f"unexpected mode: {pf['exposure']['mode']}"
    )
    assert pf["exposure"]["extra_days"] == 45, (
        f"expected 45 extra days, got {pf['exposure']['extra_days']}"
    )

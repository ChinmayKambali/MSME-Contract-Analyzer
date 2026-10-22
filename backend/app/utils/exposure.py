"""
MSMED-aware financial exposure calculator.

Statutory basis: MSMED Act 2006 Section 15 & 16.
  - Payment must be made within 45 days.
  - Interest on delayed payment = 3 × RBI Bank Rate, compounded monthly.

No LLM calls are made here.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from app.config import settings

STATUTORY_DAYS: int = 45
_MSME_MULTIPLIER: int = 3           # Section 16: three times the bank rate
_NORMALIZED_BASE: float = 100_000.0  # Rs 1,00,000 for illustrative mode


def _interest_amount(base: float, rate_pct_annual: float, extra_days: int) -> float:
    """Compound-monthly interest on *base* for *extra_days* days."""
    months = extra_days / 30.0
    monthly_rate = rate_pct_annual / 12.0 / 100.0
    return base * ((1.0 + monthly_rate) ** months - 1.0)


def compute_exposure(
    *,
    payment_days: Optional[int] = None,
    penalty_pct: Optional[float] = None,
    liability_cap_multiple: Optional[float] = None,
    contract_value_inr: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Compute MSMED financial exposure and return a dict compatible with ExposureSchema.

    Parameters
    ----------
    payment_days:
        Credit period stated in the contract (days). None → not_computable.
    penalty_pct:
        Contractual penalty as a percentage of contract value (0-100).
    liability_cap_multiple:
        Liability cap expressed as a multiple of contract value (e.g. 1.0 = 1×).
    contract_value_inr:
        Actual contract value in INR. When present → actual mode; absent → normalized.

    Returns
    -------
    dict matching ExposureSchema fields.
    """
    rate_used_pct: float = _MSME_MULTIPLIER * settings.BANK_RATE_PCT   # e.g. 17.25 %
    rate_date: str = settings.BANK_RATE_DATE

    # ------------------------------------------------------------------ #
    # NULL / not-computable guard
    # ------------------------------------------------------------------ #
    if payment_days is None:
        return {
            "mode": "not_computable",
            "amount_inr": None,
            "basis": "Insufficient data",
            "contract_days": None,
            "statutory_days": STATUTORY_DAYS,
            "extra_days": None,
            "rate_used_pct": rate_used_pct,
            "rate_date": rate_date,
            "note": (
                "payment_days is null; cannot compute statutory interest. "
                "Extract the credit period from the contract and re-run."
            ),
        }

    # ------------------------------------------------------------------ #
    # Mode selection
    # ------------------------------------------------------------------ #
    if contract_value_inr is not None:
        mode = "actual"
        base = float(contract_value_inr)
        basis = f"Actual contract value: Rs {contract_value_inr:,.0f}"
    else:
        mode = "normalized"
        base = _NORMALIZED_BASE
        basis = "Illustrative, per Rs 1,00,000 of invoice value"

    # ------------------------------------------------------------------ #
    # Payment interest
    # ------------------------------------------------------------------ #
    extra_days = max(0, payment_days - STATUTORY_DAYS)

    if extra_days == 0:
        interest_amount: float = 0.0
        note = (
            f"Payment period ({payment_days} days) is within the 45-day "
            "statutory limit under MSMED Act Section 15. No interest liability."
        )
    else:
        interest_amount = _interest_amount(base, rate_used_pct, extra_days)
        note = (
            f"Statutory interest at {rate_used_pct:.2f}% p.a. (3× RBI Bank Rate "
            f"{settings.BANK_RATE_PCT}% as at {rate_date}) on {mode} base "
            f"for {extra_days} excess days."
        )

    result: Dict[str, Any] = {
        "mode": mode,
        "amount_inr": round(interest_amount, 2),
        "basis": basis,
        "contract_days": payment_days,
        "statutory_days": STATUTORY_DAYS,
        "extra_days": extra_days,
        "rate_used_pct": rate_used_pct,
        "rate_date": rate_date,
        "note": note,
    }

    # ------------------------------------------------------------------ #
    # Penalty (optional)
    # ------------------------------------------------------------------ #
    if penalty_pct is not None:
        penalty_amount = penalty_pct / 100.0 * base
        if mode == "actual":
            result["note"] += (
                f" Penalty: Rs {penalty_amount:,.2f} "
                f"({penalty_pct}% of contract value)."
            )
        else:
            result["note"] += (
                f" Penalty: Rs {penalty_amount:,.2f} per Rs 1,00,000 "
                f"({penalty_pct}% of invoice value)."
            )

    # ------------------------------------------------------------------ #
    # Liability cap (optional)
    # ------------------------------------------------------------------ #
    if liability_cap_multiple is not None:
        if mode == "actual":
            cap_inr = liability_cap_multiple * base
            result["note"] += f" Liability cap: Rs {cap_inr:,.2f} ({liability_cap_multiple}× contract value)."
        else:
            # In normalized mode report only the multiple, not a rupee figure
            result["note"] += f" Liability cap: {liability_cap_multiple}× contract value (rupee amount only shown in actual mode)."

    return result

import time
import json
import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.config import settings
from app.services.llm_client import generate_json, generate_text, resolve_active_model
from app.services.retrieval import retrieve_benchmark_clauses
from app.utils.security import wrap_untrusted, verify_finding, enforce_risk_floor

logger = logging.getLogger(__name__)

# Hard cap: at most 2 threads may be inside a Gemini API call at the same time.
_GEMINI_SEMAPHORE = threading.Semaphore(2)

AGENT_CONFIGS = {
    "payment_terms": {
        "ui_category": "Financial",
        "title": "Payment Terms & Cash Flow",
        "focus": "Payment credit period (MSMED Act 45-day statutory limit), interest on delayed payments (3x RBI rate under Sec 16), withholding rights, advance payments, and fee deductions.",
        "statutory_reference": "MSMED Act 2006 (Section 15 & 16)"
    },
    "liability": {
        "ui_category": "Financial",
        "title": "Liability & Indemnification",
        "focus": "Limitation of liability caps, aggregate liability balance, consequential damage waivers, broad MSME indemnities, and uncapped third-party claims.",
        "statutory_reference": "Indian Contract Act 1872 (Section 73)"
    },
    "ip_ownership": {
        "ui_category": "Privacy",
        "title": "IP Rights & Confidentiality",
        "focus": "Intellectual property ownership, work-for-hire assignment, background vs foreground IP retention, NDA duration, and trade secret protection.",
        "statutory_reference": "Indian Copyright Act 1957 / IP Laws"
    },
    "penalty_ld": {
        "ui_category": "Commercial",
        "title": "Penalties & Liquidated Damages",
        "focus": "Liquidated damages caps, unreasonable delay fines, forfeiture of earnest money/security deposits, and unilateral deduction rights.",
        "statutory_reference": "Indian Contract Act 1872 (Section 74)"
    },
    "dispute_resolution": {
        "ui_category": "Commercial",
        "title": "Dispute Resolution & Governing Law",
        "focus": "Arbitration seat/venue, costs of dispute resolution, governing jurisdiction, and statutory recourse to MSME Samadhaan Facilitation Council.",
        "statutory_reference": "MSMED Act 2006 (Section 18) & Arbitration and Conciliation Act"
    },
    "termination": {
        "ui_category": "Exit",
        "title": "Termination & Exit Terms",
        "focus": "Termination for convenience, notice period symmetry, demobilization costs, survival clauses, and post-termination transition obligations.",
        "statutory_reference": "Indian Contract Act 1872"
    }
}

def analyze_domain_category(
    category: str,
    contract_text: str,
    benchmark_clauses: List[Dict[str, Any]],
    file_name: str = "",
    model_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Executes a domain-specific agent LLM call for a given contract category.
    Strictly grounded against contract text and benchmark comparison.
    Uses model_name resolved for the run to guarantee internal model consistency.
    """
    agent_meta = AGENT_CONFIGS.get(category, {
        "ui_category": "Commercial",
        "title": category.replace("_", " ").title(),
        "focus": "General contract terms",
        "statutory_reference": "Applicable Laws"
    })

    filtered_benchmarks = [
        c for c in benchmark_clauses
        if not file_name or c.get("source_doc") != file_name
    ]

    benchmark_context = ""
    if filtered_benchmarks:
        benchmark_context = "\n".join([
            f"- Standard Benchmark [{c.get('source_doc', 'Library')} - {c.get('heading', '')}]: {c.get('text', '')[:300]}"
            for c in filtered_benchmarks[:3]
        ])
    else:
        benchmark_context = "Standard safe MSME reference baseline applicable."

    system_instruction = (
        f"You are an objective legal risk auditor analyzing MSME agreements for the domain '{agent_meta['title']}'. "
        f"Focus Area: {agent_meta['focus']}. Statutory Baseline: {agent_meta['statutory_reference']}.\n\n"
        "STRICT AUDIT RULES:\n"
        "1. Base your analysis STRICTLY on the actual provided contract text. Do NOT invent, assume, or hallucinate sections or terms that do not exist.\n"
        "2. Compare the contract text against the RETRIEVED BENCHMARK REFERENCE CLAUSES. If the contract text is fair, balanced, standard, or accords with MSME protection norms (e.g. 45-day payment, capped liability, mutual termination, local arbitration), IT IS NOT A RISK. You MUST return an empty array: {\"clauses\": []}.\n"
        "3. Only flag genuine, explicit risks, unfair obligations, or statutory violations against the MSME vendor.\n"
        "4. Return strictly valid JSON with key 'clauses':\n"
        "{\n"
        '  "clauses": [\n'
        '    {\n'
        '      "title": "Concise Risk Title",\n'
        '      "risk_level": "High" | "Medium" | "Low",\n'
        '      "location": "Exact Section / Paragraph from text",\n'
        '      "what_it_says": "Exact quote or precise summary from text",\n'
        '      "why_risky": "Clear explanation of financial/legal risk to MSME",\n'
        '      "legal_flag": "Statutory reference e.g. MSMED Act 2006 Sec 15",\n'
        '      "benchmark_comparison": "How this deviates from the standard benchmark clause",\n'
        '      "suggested_alternative": "Actionable safer draft clause",\n'
        '      "confidence": 0.90\n'
        '    }\n'
        '  ]\n'
        "}"
    )

    prompt = (
        f"CONTRACT TEXT TO AUDIT:\n\"\"\"\n{wrap_untrusted(contract_text)[:8100]}\n\"\"\"\n\n"
        f"RETRIEVED BENCHMARK REFERENCE CLAUSES:\n{benchmark_context}\n\n"
        f"Audit the contract text for '{agent_meta['title']}' risks and output structured JSON."
    )

    try:
        with _GEMINI_SEMAPHORE:
            json_raw = generate_json(prompt, system_instruction=system_instruction, model_name=model_name)
        parsed = json.loads(json_raw)
        clauses = parsed.get("clauses", []) if isinstance(parsed, dict) else []

        formatted_clauses = []
        for item in clauses:
            if not isinstance(item, dict):
                continue
            formatted_clauses.append({
                "title": item.get("title") or f"{agent_meta['title']} Risk",
                "risk_level": item.get("risk_level", "Medium") if item.get("risk_level") in ["High", "Medium", "Low"] else "Medium",
                "agent_category": category,
                "ui_category": agent_meta["ui_category"],
                "location": item.get("location") or "Contract Section",
                "what_it_says": item.get("what_it_says") or "",
                "why_risky": item.get("why_risky") or "Unfavorable clause terms for MSME.",
                "legal_flag": item.get("legal_flag") or agent_meta["statutory_reference"],
                "benchmark_comparison": item.get("benchmark_comparison") or "Deviates from standard MSME benchmark norms.",
                "suggested_alternative": item.get("suggested_alternative") or "Negotiate fair standard terms.",
                "confidence": float(item.get("confidence", 0.9)),
                "benchmark_refs": [
                    {"source_doc": b.get("source_doc"), "heading": b.get("heading")}
                    for b in filtered_benchmarks[:2]
                ] if filtered_benchmarks else []
            })

        return formatted_clauses

    except Exception as e:
        logger.error(f"Error in agent analysis for {category}: {e}")
        raise RuntimeError(f"Agent '{category}' failed: {e}") from e

def calculate_overall_risk_and_score(clauses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes overall score (0-100) and overall risk level based on detected clause risks.
    Higher score = Higher risk (Phase 1 calibration):
    - 0 to 30: Low Risk
    - 31 to 70: Moderate Risk
    - 71 to 100: High Risk
    """
    score = 0
    high_count = sum(1 for c in clauses if c.get("risk_level") == "High")
    med_count = sum(1 for c in clauses if c.get("risk_level") == "Medium")
    low_count = sum(1 for c in clauses if c.get("risk_level") == "Low")

    score += (high_count * 20 + med_count * 10 + low_count * 4)
    score = max(0, min(100, score))

    if score <= 30:
        overall_risk = "Low"
    elif score <= 70:
        overall_risk = "Moderate"
    else:
        overall_risk = "High"

    return {
        "score": score,
        "overall_risk": overall_risk,
        "high_count": high_count,
        "med_count": med_count,
        "low_count": low_count
    }

def generate_executive_summary(
    contract_text: str,
    clauses: List[Dict[str, Any]],
    overall_risk: str,
    score: int,
    model_name: Optional[str] = None
) -> str:
    """
    Generates a concise 2-3 sentence executive summary tailored for MSME business owners.
    """
    if not clauses:
        return (
            f"The contract adheres to standard, fair MSME business practices with low overall risk (Risk Score: {score}/100). "
            "Payment terms, liability caps, dispute resolution, and termination provisions conform to benchmark MSME protections."
        )

    high_risks = [c["title"] for c in clauses if c.get("risk_level") == "High"]
    med_risks = [c["title"] for c in clauses if c.get("risk_level") == "Medium"]

    prompt = (
        f"Contract Analysis Summary Data:\n"
        f"Overall Risk: {overall_risk}\n"
        f"Risk Score: {score}/100 (where 0-30 is Low risk, 31-70 is Moderate risk, 71-100 is High risk)\n"
        f"High Risk Items ({len(high_risks)}): {', '.join(high_risks[:4]) or 'None'}\n"
        f"Medium Risk Items ({len(med_risks)}): {', '.join(med_risks[:4]) or 'None'}\n\n"
        "Write a concise 2-3 sentence executive summary explaining the contract risk profile to an MSME business owner."
    )
    system_instruction = "You are a senior MSME legal advisor. Provide clear, direct, and actionable executive summaries."

    try:
        summary = generate_text(prompt, system_instruction=system_instruction, model_name=model_name)
        return summary.strip() if summary else f"Contract analyzed with overall risk {overall_risk} (Risk Score: {score}/100)."
    except Exception as e:
        logger.error(f"Error generating executive summary: {e}")
        return f"Analysis complete with overall risk evaluated as {overall_risk} (Risk Score: {score}/100)."

def run_agentic_analysis_pipeline(
    db: Session,
    contract_text: str,
    file_name: str = "",
    status_callback: Optional[callable] = None
) -> Dict[str, Any]:
    """
    Executes full Phase 2 Agentic Analysis pipeline:
    1. Resolves a SINGLE active model at start of run across MODEL_FALLBACK_POOL for 100% internal consistency.
    2. Prepares vector benchmark retrieval for each agent using actual contract text.
    3. Runs 6 domain agents in parallel using ThreadPoolExecutor bounded by settings.MAX_AGENT_CONCURRENCY.
    4. Triggers status_callback(category, state) for real-time state tracking.
    5. Synthesizes findings, computes overall score, and generates executive summary.
    """
    categories = list(AGENT_CONFIGS.keys())
    agent_results: Dict[str, List[Dict[str, Any]]] = {}

    max_workers = getattr(settings, "MAX_AGENT_CONCURRENCY", 2)

    # Resolve single active model for the entire analysis run (NO mid-run model switching)
    resolved_model = resolve_active_model()
    logger.info(f"Initiating agentic analysis pipeline for '{file_name}' using single model '{resolved_model}' with MAX_AGENT_CONCURRENCY={max_workers}")

    # Step 1: Pre-fetch benchmark references for each domain category using retrieval threshold = 0.65
    benchmark_map = {}
    for cat in categories:
        try:
            matched = retrieve_benchmark_clauses(
                db=db,
                query_text=contract_text[:2000],
                category=cat,
                top_k=3,
                threshold=0.65
            )
            benchmark_map[cat] = matched
        except Exception as e:
            logger.warning(f"Benchmark retrieval error for category {cat}: {e}")
            benchmark_map[cat] = []

    # Step 2: Parallel Agent Execution bounded by MAX_AGENT_CONCURRENCY using resolved_model
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_cat = {}
        for cat in categories:
            if status_callback:
                status_callback(cat, "active")
            future = executor.submit(
                analyze_domain_category,
                category=cat,
                contract_text=contract_text,
                benchmark_clauses=benchmark_map.get(cat, []),
                file_name=file_name,
                model_name=resolved_model
            )
            future_to_cat[future] = cat
            time.sleep(2.0)  # Stagger requests to stay under free-tier 5 RPM quota

        failed_agents = []
        for future in as_completed(future_to_cat):
            cat = future_to_cat[future]
            try:
                clauses = future.result()
                agent_results[cat] = clauses
                if status_callback:
                    status_callback(cat, "done")
                logger.info(f"Agent '{cat}' completed with {len(clauses)} detected clauses using model '{resolved_model}'.")
            except Exception as e:
                logger.error(f"Agent '{cat}' failed with error: {e}")
                agent_results[cat] = []
                failed_agents.append(cat)
                if status_callback:
                    status_callback(cat, "failed")

        if failed_agents:
            raise RuntimeError(f"Agentic pipeline failed: Agents {failed_agents} failed due to LLM/API errors.")

    # Step 3: Combine all detected clauses and run verification + risk-floor enforcement
    all_clauses = []
    retrieved_ids_all: List[str] = [
        b.get("source_doc", "") for bm in benchmark_map.values() for b in bm
    ]
    for cat in categories:
        for clause in agent_results.get(cat, []):
            verify_finding(
                clause,
                source_text=contract_text,
                retrieved_benchmark_ids=retrieved_ids_all,
                injection_in_clause=bool(
                    clause.get("verification", {}) and
                    any("Injection" in f for f in clause.get("verification", {}).get("flags", []))
                ),
            )
            enforce_risk_floor(clause)
            all_clauses.append(clause)

    # Step 4: Calculate score and overall risk
    metrics = calculate_overall_risk_and_score(all_clauses)
    
    # Step 5: Synthesize executive summary using resolved_model
    summary = generate_executive_summary(
        contract_text=contract_text,
        clauses=all_clauses,
        overall_risk=metrics["overall_risk"],
        score=metrics["score"],
        model_name=resolved_model
    )

    return {
        "overall_risk": metrics["overall_risk"],
        "score": metrics["score"],
        "summary": summary,
        "clauses": all_clauses,
        "agent_results": agent_results,
        "model_used": resolved_model
    }

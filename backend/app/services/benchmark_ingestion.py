import os
import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any
import docx
from sqlalchemy.orm import Session
from app.config import settings
from app.models import BenchmarkClause
from app.services.llm_client import get_embedding

logger = logging.getLogger(__name__)

CATEGORY_KEYWORD_MAP = {
    "payment_terms": ["payment", "invoice", "price", "fee", "tax", "msme", "interest", "delayed payment"],
    "liability": ["liability", "limitation of liability", "indemn", "hold harmless"],
    "ip_ownership": ["intellectual property", "ip ", "ipr", "copyright", "patent", "confidential"],
    "penalty_ld": ["penalty", "liquidated damages", "delay charge"],
    "dispute_resolution": ["dispute", "arbitration", "governing law", "jurisdiction", "facilitation council"],
    "termination": ["termination", "term and termination", "cancel", "expiry"]
}

def classify_heading(heading_text: str) -> str:
    """Classifies a clause heading into one of the 6 core categories or 'other'."""
    text_lower = heading_text.lower()
    for category, keywords in CATEGORY_KEYWORD_MAP.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return "other"

def parse_docx_clauses(file_path: Path) -> List[Dict[str, Any]]:
    doc = docx.Document(str(file_path))
    clauses = []
    current_heading = "General"
    current_text_lines = []
    current_ref = ""

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue

        # Check for clause heading (e.g. "6. PAYMENT TERMS" or "Clause 11")
        if (len(text) < 80 and (text[0].isdigit() or paragraph.style.name.startswith("Heading"))):
            if current_text_lines:
                clause_text = "\n".join(current_text_lines).strip()
                if clause_text:
                    content_hash = hashlib.sha256(f"{file_path.name}_{current_heading}_{clause_text}".encode("utf-8")).hexdigest()
                    clauses.append({
                        "source_doc": file_path.name,
                        "clause_ref": current_ref or current_heading[:20],
                        "heading": current_heading,
                        "category": classify_heading(current_heading),
                        "text": clause_text,
                        "content_hash": content_hash
                    })
                current_text_lines = []
            current_heading = text
            parts = text.split(maxsplit=1)
            current_ref = parts[0] if parts else ""
        else:
            current_text_lines.append(text)

    if current_text_lines:
        clause_text = "\n".join(current_text_lines).strip()
        if clause_text:
            content_hash = hashlib.sha256(f"{file_path.name}_{current_heading}_{clause_text}".encode("utf-8")).hexdigest()
            clauses.append({
                "source_doc": file_path.name,
                "clause_ref": current_ref or current_heading[:20],
                "heading": current_heading,
                "category": classify_heading(current_heading),
                "text": clause_text,
                "content_hash": content_hash
            })

    return clauses

def seed_benchmark_library(db: Session, benchmark_folder: str = "MSME BENCHMARK LIB") -> int:
    """
    Ingests all MSME-BENCHMARK-*.docx contracts into PostgreSQL with pgvector embeddings.
    Idempotent: skips clauses with existing content_hash.
    Returns: count of newly ingested clauses.
    """
    base_dir = Path(settings.UPLOAD_DIR).parent.parent
    folder_path = base_dir / benchmark_folder
    if not folder_path.exists():
        # Fallback search
        folder_path = Path(benchmark_folder)
        if not folder_path.exists():
            logger.error(f"Benchmark folder not found: {benchmark_folder}")
            return 0

    docx_files = list(folder_path.glob("MSME-BENCHMARK-*.docx"))
    logger.info(f"Found {len(docx_files)} benchmark docx files in {folder_path}")

    added_count = 0
    for doc_file in docx_files:
        clauses = parse_docx_clauses(doc_file)
        for item in clauses:
            existing = db.query(BenchmarkClause).filter(BenchmarkClause.content_hash == item["content_hash"]).first()
            if existing:
                continue

            # Generate vector embedding for clause text using RETRIEVAL_DOCUMENT task type
            try:
                embedding_vector = get_embedding(item["text"], task_type="RETRIEVAL_DOCUMENT")
            except Exception as e:
                logger.warning(f"Could not generate embedding for {item['heading']}: {e}")
                embedding_vector = None

            benchmark_entry = BenchmarkClause(
                source_doc=item["source_doc"],
                clause_ref=item["clause_ref"],
                heading=item["heading"],
                category=item["category"],
                text=item["text"],
                content_hash=item["content_hash"],
                embedding=embedding_vector
            )
            db.add(benchmark_entry)
            added_count += 1

    db.commit()
    logger.info(f"Seeded {added_count} benchmark clauses into database.")
    return added_count

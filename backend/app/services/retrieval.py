from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models import BenchmarkClause
from app.services.llm_client import get_embedding
from app.config import settings

def retrieve_benchmark_clauses(
    db: Session,
    query_text: str,
    category: str,
    top_k: int = 3,
    threshold: float = None
) -> List[Dict[str, Any]]:
    """
    Performs category-filtered vector similarity search against the static benchmark library.
    Returns: List of dicts containing text, source_doc, heading, similarity score.
    """
    if threshold is None:
        threshold = settings.SIMILARITY_THRESHOLD

    # Generate query embedding using RETRIEVAL_QUERY task type
    try:
        query_vector = get_embedding(query_text, task_type="RETRIEVAL_QUERY")
    except Exception:
        query_vector = []

    if not query_vector:
        return []

    # pgvector cosine_distance operator: BenchmarkClause.embedding.cosine_distance(query_vector)
    # Cosine Similarity = 1.0 - Cosine Distance
    stmt = (
        select(
            BenchmarkClause,
            BenchmarkClause.embedding.cosine_distance(query_vector).label("distance")
        )
        .where(BenchmarkClause.category == category)
        .order_by("distance")
        .limit(top_k)
    )

    results = db.execute(stmt).all()
    matched_clauses = []
    for row in results:
        clause_obj, distance = row[0], row[1]
        similarity = 1.0 - float(distance) if distance is not None else 0.0
        
        if similarity >= threshold:
            matched_clauses.append({
                "source_doc": clause_obj.source_doc,
                "clause_ref": clause_obj.clause_ref,
                "heading": clause_obj.heading,
                "text": clause_obj.text,
                "similarity": round(similarity, 4)
            })

    return matched_clauses

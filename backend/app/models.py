import datetime
import uuid
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, JSON
from pgvector.sqlalchemy import Vector
from app.db import Base
from app.config import settings

class BenchmarkClause(Base):
    __tablename__ = "benchmark_clauses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_doc = Column(String(255), nullable=False)
    clause_ref = Column(String(100), nullable=True)
    heading = Column(String(255), nullable=True)
    category = Column(String(50), nullable=False, index=True)
    text = Column(Text, nullable=False)
    content_hash = Column(String(64), unique=True, nullable=False, index=True)
    # Dynamic dimension from settings.EMBEDDING_DIM (e.g. 768)
    embedding = Column(Vector(settings.EMBEDDING_DIM), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    file_type = Column(String(20), nullable=False)
    page_count = Column(Integer, nullable=True)
    status = Column(String(50), nullable=False, default="EXTRACTING") # EXTRACTING, ANALYZING, COMBINING, COMPLETE, FAILED
    stage = Column(String(50), nullable=False, default="EXTRACTING")
    progress = Column(Integer, default=0)
    agent_states = Column(JSON, default=dict)
    overall_risk = Column(String(50), nullable=True)
    score = Column(Integer, nullable=True)
    summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

class AnalysisClauseResult(Base):
    __tablename__ = "analysis_clause_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String(36), ForeignKey("analysis_records.id", ondelete="CASCADE"), nullable=False, index=True)
    clause_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    agent_category = Column(String(50), nullable=False)
    ui_category = Column(String(50), nullable=False)
    risk_level = Column(String(20), nullable=False) # High, Medium, Low
    what_it_says = Column(Text, nullable=False)
    why_risky = Column(Text, nullable=False)
    legal_flag = Column(Text, nullable=True)
    benchmark_comparison = Column(Text, nullable=True)
    suggested_alternative = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)
    benchmark_refs = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

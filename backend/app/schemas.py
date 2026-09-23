from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ClauseOutputSchema(BaseModel):
    id: int
    title: str
    risk: str = Field(..., description="High, Medium, Low")
    category: str = Field(..., description="UI Category label e.g. Financial, Exit, Privacy, Commercial")
    location: str
    text: str = Field(..., description="What the clause says")
    recommendation: str = Field(..., description="Suggested safer alternative")

    # Additive fields (UI will ignore these cleanly while backend keeps full detail)
    why_risky: str
    legal_flag: Optional[str] = None
    benchmark_comparison: Optional[str] = None
    confidence: Optional[float] = 1.0
    benchmark_refs: Optional[List[Dict[str, Any]]] = []
    agent_category: str

class AnalysisReportResponse(BaseModel):
    title: str
    fileName: str
    pages: Optional[int] = None
    analyzedAt: str
    overallRisk: str
    score: int
    summary: str
    clauses: List[ClauseOutputSchema]

class AnalysisStatusResponse(BaseModel):
    analysis_id: str
    status: str  # EXTRACTING, ANALYZING, COMBINING, COMPLETE, FAILED
    stage: str
    progress: int
    agent_states: Dict[str, str] = Field(default_factory=dict)
    error_message: Optional[str] = None

class HistoryItemSchema(BaseModel):
    analysis_id: str
    fileName: str
    analyzedAt: str
    overallRisk: Optional[str] = None
    score: Optional[int] = None
    status: str

class ChatRequestSchema(BaseModel):
    message: str

class ChatResponseSchema(BaseModel):
    reply: str

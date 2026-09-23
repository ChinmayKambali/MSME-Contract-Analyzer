import logging
from sqlalchemy.orm import Session
from app.models import AnalysisRecord
from app.services.llm_client import generate_text

logger = logging.getLogger(__name__)

def handle_followup_chat(db: Session, analysis_id: str, user_message: str) -> str:
    record = db.query(AnalysisRecord).filter(AnalysisRecord.id == analysis_id).first()
    if not record:
        return "Contract analysis record not found."

    # Grounded prompt context
    system_prompt = (
        "You are an expert MSME contract assistant. Answer the user's question about the contract based ONLY on "
        "the analyzed contract text and findings. Be clear, concise, and helpful to the small business owner."
    )
    prompt = f"Contract File: {record.file_name}\nOverall Risk: {record.overall_risk}\nSummary: {record.summary}\n\nUser Question: {user_message}"
    
    try:
        reply = generate_text(prompt, system_instruction=system_prompt)
        return reply if reply else "I could not generate a response based on the contract context."
    except Exception as e:
        logger.error(f"Chat generation error: {e}")
        return f"Follow-up chat response unavailable: {str(e)}"

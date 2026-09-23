import re
import time
import logging
from typing import List, Optional, Any, Callable
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

# Fallback pool of SDK-compatible Gemini models for free-tier quota resilience
MODEL_FALLBACK_POOL = [
    settings.MODEL_NAME,
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-flash-latest"
]

def call_with_retry(
    func: Callable,
    *args,
    max_retries: int = 4,
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    **kwargs
) -> Any:
    """
    Executes a callable with exponential backoff retry for transient network/503/429 errors.
    Dynamically extracts retryDelay / retry-in seconds from Gemini API error responses.
    """
    delay = initial_delay
    for attempt in range(1, max_retries + 2):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt > max_retries:
                raise e
            err_str = str(e)
            wait_sec = delay
            match = re.search(r"retry(?:\s*in|_delay|Delay)?\s*['\"]?:?\s*['\"]?(\d+(?:\.\d+)?)s?['\"]?", err_str, re.IGNORECASE)
            if match:
                extracted = float(match.group(1))
                wait_sec = max(wait_sec, extracted + 1.0)
            elif "RESOURCE_EXHAUSTED" in err_str or "429" in err_str:
                wait_sec = max(wait_sec, 20.0)

            logger.warning(
                f"Transient error in {getattr(func, '__name__', str(func))} (attempt {attempt}/{max_retries + 1}): {e}. Retrying in {wait_sec:.1f}s..."
            )
            time.sleep(wait_sec)
            delay *= backoff_factor

def get_genai_client() -> Optional[genai.Client]:
    if not settings.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY is not set.")
        return None
    return genai.Client(api_key=settings.GEMINI_API_KEY)

def resolve_active_model() -> str:
    """
    Resolves a single active model at the START of an analysis run.
    Pings settings.MODEL_NAME first; falls back if 429 quota limit is encountered.
    Ensures all agents in a single run use the EXACT SAME model for internal consistency.
    """
    client = get_genai_client()
    if not client:
        return settings.MODEL_NAME

    models_to_try = list(dict.fromkeys(MODEL_FALLBACK_POOL))
    for model_name in models_to_try:
        try:
            client.models.generate_content(
                model=model_name,
                contents="ping",
                config=types.GenerateContentConfig(
                    max_output_tokens=5,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
                )
            )
            logger.info(f"Resolved active model for analysis run: '{model_name}'")
            return model_name
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e) or "429" in str(e):
                logger.warning(f"Model '{model_name}' hit rate/quota limit. Testing fallback model...")
                continue
            return model_name

    return settings.MODEL_NAME

def generate_text(
    prompt: str,
    system_instruction: Optional[str] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Single-shot text generation call using non-chat generate_content.
    Disables AFC to avoid unnecessary multi-turn tool calling overhead/warnings.
    """
    client = get_genai_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is missing.")

    target_model = model_name or settings.MODEL_NAME

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    response = call_with_retry(
        client.models.generate_content,
        model=target_model,
        contents=prompt,
        config=config,
        max_retries=2
    )
    return response.text or ""

def generate_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Plain non-chat generate_content call for structured JSON outputs
    (classification, per-agent analysis, aggregation).
    Disables AFC since multi-turn tool calling is unnecessary.
    """
    client = get_genai_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is missing.")

    target_model = model_name or settings.MODEL_NAME

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=response_schema,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )

    response = call_with_retry(
        client.models.generate_content,
        model=target_model,
        contents=prompt,
        config=config,
        max_retries=2
    )
    return response.text or ""

def get_embedding(text_content: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    """
    Generates embedding for text content using google-genai SDK.
    task_type: 'RETRIEVAL_DOCUMENT' (for indexing benchmark library) or 'RETRIEVAL_QUERY' (for search queries).
    """
    client = get_genai_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is missing.")

    config = types.EmbedContentConfig(
        task_type=task_type,
        output_dimensionality=settings.EMBEDDING_DIM
    )

    response = call_with_retry(
        client.models.embed_content,
        model=settings.EMBEDDING_MODEL_NAME,
        contents=text_content,
        config=config,
        max_retries=3
    )
    if response.embeddings and len(response.embeddings) > 0:
        return response.embeddings[0].values
    return []

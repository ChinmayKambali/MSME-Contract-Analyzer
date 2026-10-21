import random
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



def _is_retryable(err_str: str) -> bool:
    """Return True for transient quota / availability errors."""
    return any(k in err_str for k in (
        "429", "RESOURCE_EXHAUSTED",
        "503", "UNAVAILABLE", "Service Unavailable",
    ))

_HARD_QUOTA_MARKERS = ("PerDay", "per day", "limit: 0", "quotaValue': '0'")

def _is_hard_quota_failure(err_str: str) -> bool:
    """True when the 429 signals a per-day / exhausted-for-today limit (no point retrying)."""
    return any(m in err_str for m in _HARD_QUOTA_MARKERS)

def _extract_retry_delay(err_str: str, base_delay: float) -> float:
    """Return server-suggested wait (+ 1 s buffer) or base_delay, whichever is larger."""
    match = re.search(
        r"""retry(?:\s*in|_delay|Delay)?\s*['""]?:?\s*['""]?(\d+(?:\.\d+)?)s?['""]?""",
        err_str, re.IGNORECASE
    )
    if match:
        return max(base_delay, float(match.group(1)) + 1.0)
    if _is_retryable(err_str):
        return max(base_delay, 20.0)
    return base_delay

def call_with_retry(
    func: Callable,
    *args,
    max_retries: int = 3,          # cap at 3 attempts per model
    initial_delay: float = 2.0,
    backoff_factor: float = 2.0,
    max_total_wait: float = 60.0,  # hard ceiling on total sleep per model
    **kwargs
) -> Any:
    """
    Retry with exponential backoff (2 s → 4 s → 8 s + jitter).
    Hard-quota (PerDay / limit:0) errors are re-raised immediately with no sleep.
    Other 429/503 errors retry up to max_retries times, capped at max_total_wait seconds.
    On exhaustion raises the last exception.
    """
    delay = initial_delay
    last_exc: Exception = RuntimeError("No attempts made")
    total_waited = 0.0
    for attempt in range(1, max_retries + 2):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exc = e
            err_str = str(e)
            # Hard daily quota: re-raise immediately so caller can skip to next model
            if _is_hard_quota_failure(err_str):
                raise
            if attempt > max_retries:
                break
            wait_sec = _extract_retry_delay(err_str, delay)
            wait_sec += random.uniform(0.1, 1.5)   # jitter
            # Never exceed the per-model total wait ceiling
            remaining = max_total_wait - total_waited
            if remaining <= 0:
                break
            wait_sec = min(wait_sec, remaining)
            logger.warning(
                f"Transient error in {getattr(func, '__name__', str(func))} "
                f"(attempt {attempt}/{max_retries}): {e}. Retrying in {wait_sec:.1f}s…"
            )
            time.sleep(wait_sec)
            total_waited += wait_sec
            delay *= backoff_factor
    raise last_exc

def _call_with_model_fallback(
    client: genai.Client,
    models: List[str],
    contents: str,
    config,
    label: str = "generate",
) -> Any:
    """
    Try each model in *models* with per-model retries (max 3, max 60 s wait).
    Hard daily-quota errors skip retries and advance to the next model immediately.
    Raise only when every model has failed.
    """
    last_exc: Exception = RuntimeError("No models available")
    for model_name in models:
        try:
            response = call_with_retry(
                client.models.generate_content,
                model=model_name,
                contents=contents,
                config=config,
                max_retries=3,
                initial_delay=2.0,
                backoff_factor=2.0,
                max_total_wait=60.0,
            )
            logger.info(f"[{label}] answered by model '{model_name}'")
            return response
        except Exception as e:
            last_exc = e
            err_str = str(e)
            if _is_hard_quota_failure(err_str):
                logger.warning(
                    f"[{label}] model '{model_name}' hit daily quota limit. "
                    f"Skipping to next model immediately."
                )
                continue
            if _is_retryable(err_str):
                logger.warning(
                    f"[{label}] model '{model_name}' exhausted retries "
                    f"({e}). Trying next model…"
                )
                continue
            # Non-retryable (auth, bad request, etc.) – fail fast
            raise
    raise RuntimeError(
        "Gemini quota exhausted or service busy, try again later."
    ) from last_exc

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
    Single-shot text generation with full model-pool fallback.
    """
    client = get_genai_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is missing.")

    models = list(dict.fromkeys([model_name or settings.MODEL_NAME] + MODEL_FALLBACK_POOL))
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )
    response = _call_with_model_fallback(client, models, prompt, config, label="generate_text")
    return response.text or ""

def generate_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    response_schema: Optional[Any] = None,
    model_name: Optional[str] = None
) -> str:
    """
    Structured JSON generation with full model-pool fallback.
    """
    client = get_genai_client()
    if not client:
        raise ValueError("GEMINI_API_KEY is missing.")

    models = list(dict.fromkeys([model_name or settings.MODEL_NAME] + MODEL_FALLBACK_POOL))
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        response_mime_type="application/json",
        response_schema=response_schema,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True)
    )
    response = _call_with_model_fallback(client, models, prompt, config, label="generate_json")
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

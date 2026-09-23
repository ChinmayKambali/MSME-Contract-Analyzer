import sys
from pathlib import Path

# Add backend directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.config import settings
from app.services.llm_client import generate_text, get_embedding

def test_api():
    print("\n==========================================")
    print("   GEMINI API REAL TEST VERIFICATION")
    print("==========================================")
    print(f"Generation Model: {settings.MODEL_NAME}")
    print(f"Embedding Model:  {settings.EMBEDDING_MODEL_NAME}")
    print(f"Embedding Dim:    {settings.EMBEDDING_DIM}")

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
        print("\n[NOTICE] GEMINI_API_KEY is not set in .env yet.")
        print("Please add GEMINI_API_KEY=your_key in .env file and run:")
        print("python backend/scripts/verify_api_key.py\n")
        return

    try:
        print("\n--- 1. Testing Text Generation Call ---")
        prompt = "Explain in one sentence why MSMEs need clear contract terms."
        response_text = generate_text(prompt)
        print(f"SUCCESS! Output:\n\"{response_text.strip()}\"")
    except Exception as e:
        print(f"ERROR in generation call: {e}")

    try:
        print("\n--- 2. Testing Embedding Call ---")
        sample_text = "The customer shall pay all undisputed invoices within 30 days."
        emb = get_embedding(sample_text, task_type="RETRIEVAL_DOCUMENT")
        print(f"SUCCESS! Embedding length returned: {len(emb)}")
        if len(emb) == settings.EMBEDDING_DIM:
            print(f"Verified embedding dimension matches EMBEDDING_DIM ({settings.EMBEDDING_DIM}).")
        else:
            print(f"WARNING: Dimension mismatch! Expected {settings.EMBEDDING_DIM}, got {len(emb)}")
    except Exception as e:
        print(f"ERROR in embedding call: {e}")

if __name__ == "__main__":
    test_api()

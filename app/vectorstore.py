import os
from dotenv import load_dotenv
from supabase import create_client, Client
from app.openai_utils import get_embedding
import numpy as np
import logging

logger = logging.getLogger(__name__)
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Validate environment variables
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("⚠️ Missing Supabase credentials. Vector queries will fail.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if (SUPABASE_URL and SUPABASE_KEY) else None

# --- Store embedded content ---
def embed_and_store_text(text: str, metadata: dict = {}) -> bool:
    try:
        embedding = get_embedding(text)
        data, count = supabase.table("documents").insert({
            "content": text,
            "embedding": embedding,
            "metadata": metadata
        }).execute()
        return bool(data)
    except Exception as e:
        print("❌ Failed to store embedding to Supabase:", e)
        return False

# --- Query top-k similar chunks ---
def query_vectorstore(query: str, top_k: int = 3) -> str:
    try:
        if not supabase:
            logger.warning("Supabase not initialized. Returning empty context.")
            return ""

        query_embedding = get_embedding(query)

        response = supabase.rpc("match_documents", {
            "query_embedding": query_embedding,
            "match_count": top_k
        }).execute()

        documents = response.data if response.data else []
        context = "\n---\n".join(doc["content"] for doc in documents)
        return context

    except Exception as e:
        logger.error(f"❌ Supabase vector query failed: {type(e).__name__}: {str(e)}", exc_info=True)
        return ""  # fallback: empty context

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from app.openai_utils import get_embedding
import numpy as np

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Store embedded content ---
def embed_and_store_text(text: str, metadata: dict = {}) -> bool:
    # Get embedding
    embedding = get_embedding(text)
    
    # Insert into Supabase
    data, count = supabase.table("documents").insert({
        "content": text,
        "embedding": embedding,
        "metadata": metadata
    }).execute()
    
    # Success if we got back inserted rows (count > 0)
    return bool(data)

# --- Query top-k similar chunks ---
def query_vectorstore(query: str, top_k: int = 3) -> str:
    query_embedding = get_embedding(query)

    # Use Supabase RPC function to perform similarity search
    response = supabase.rpc("match_documents", {
        "query_embedding": query_embedding,
        "match_count": top_k
    }).execute()

    documents = response.data if response.data else []
    context = "\n---\n".join(doc["content"] for doc in documents)
    return context

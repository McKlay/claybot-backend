import os
import tiktoken
from app.vectorstore import embed_and_store_text

# === Config ===
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "project_readmes")
CHUNK_TOKEN_LIMIT = 400
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

def split_into_chunks(text: str, max_tokens: int = CHUNK_TOKEN_LIMIT) -> list[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_tokens = 0

    for word in words:
        word_tokens = len(tokenizer.encode(word))
        if current_tokens + word_tokens > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_tokens = word_tokens
        else:
            current_chunk.append(word)
            current_tokens += word_tokens

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def run_loader():
    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".md"):
            continue

        base_id = os.path.splitext(filename)[0]  # e.g. "dogBreed"
        file_path = os.path.join(DATA_DIR, filename)

        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        print(f"🔎 Reading {filename}")
        chunks = split_into_chunks(text)

        for i, chunk in enumerate(chunks):
            metadata = {
                "project": base_id,
                "chunk": i + 1,
                "source": "project_readmes"
            }
            success = embed_and_store_text(chunk, metadata)
            if success:
                print(f"✅ Stored {base_id}-{i+1}")
            else:
                print(f"❌ Failed to store {base_id}-{i+1}")

if __name__ == "__main__":
    run_loader()

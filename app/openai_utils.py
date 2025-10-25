import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 1. Get embeddings for a text chunk ---
def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding


# --- 2. Get chat response from OpenAI ---
def get_chat_response(user_query: str, context: str, model: str = "gpt-5-nano") -> str:
    messages = [
        {"role": "system", "content": (
            f"You are ClayBot, a helpful assistant for Clay Sarte's portfolio site. Use the context below to answer user questions. "
            f"If the answer is not in the context, try to search for Clay Mark Sarte public data.\n\nContext:\n{context}"
        )},
        {"role": "user", "content": user_query}
    ]
    
    # gpt-5-nano doesn't support custom temperature, only default (1)
    create_kwargs = {
        "model": model,
        "messages": messages,
    }
    if model != "gpt-5-nano":
        create_kwargs["temperature"] = 0.3
    
    result = client.chat.completions.create(**create_kwargs)
    return result.choices[0].message.content.strip()

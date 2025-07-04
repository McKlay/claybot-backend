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
def get_chat_response(user_query: str, context: str, model: str = "gpt-3.5-turbo") -> str:
    messages = [
        {"role": "system", "content": f"You are ClayBot, a helpful assistant for Clay Sarte's portfolio site. Use the context below to answer user questions. If the answer is not in the context, say you don't know.\n\nContext:\n{context}"},
        {"role": "user", "content": user_query}
    ]
    result = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3
    )
    return result.choices[0].message.content.strip()

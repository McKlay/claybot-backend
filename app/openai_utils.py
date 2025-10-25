import os
from openai import OpenAI
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from typing import Dict

# Load environment variables from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Store conversation histories per session
conversation_histories: Dict[str, InMemoryChatMessageHistory] = {}

# --- 1. Get embeddings for a text chunk ---
def get_embedding(text: str, model: str = "text-embedding-3-small") -> list:
    response = client.embeddings.create(
        input=text,
        model=model
    )
    return response.data[0].embedding


# --- 2. Get chat response from OpenAI (Legacy - single turn) ---
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


# --- 3. Get chat response with conversation memory (Multi-turn) ---
def get_chat_response_with_memory(
    user_query: str, 
    context: str, 
    session_id: str = "default",
    model: str = "gpt-4o-mini"
) -> str:
    """
    Handle multi-turn conversations using LangChain with conversation memory.
    Each session_id maintains its own conversation history.
    """
    # Get or create history for this session
    def get_session_history(session_id: str) -> InMemoryChatMessageHistory:
        if session_id not in conversation_histories:
            conversation_histories[session_id] = InMemoryChatMessageHistory()
        return conversation_histories[session_id]
    
    # Create the chat model
    chat_kwargs = {"model": model, "api_key": os.getenv("OPENAI_API_KEY")}
    if model != "gpt-5-nano":
        chat_kwargs["temperature"] = 0.3
    
    llm = ChatOpenAI(**chat_kwargs)
    
    # Create a prompt template that includes context and conversation history
    prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are ClayBot, a helpful assistant for Clay Sarte's portfolio site. "
     "Respond concisely for a chat widget UI. Use the context below to answer user questions. "
     "If the answer is not in the context, try to search for Clay Mark Sarte public data.\n\n"
     f"Context:\n{context}\n\n"
     "Always format your response in markdown. If referencing a project demo, display the link as clickable markdown. "
     "Remember previous messages in the conversation and maintain context."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    # Create the chain
    chain = prompt | llm
    
    # Wrap with message history
    chain_with_history = RunnableWithMessageHistory(
        chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history"
    )
    
    # Get response
    response = chain_with_history.invoke(
        {"input": user_query},
        config={"configurable": {"session_id": session_id}}
    )
    
    return response.content.strip()


# --- 4. Clear conversation memory for a session ---
def clear_conversation_memory(session_id: str = "default") -> bool:
    """Clear the conversation history for a specific session."""
    if session_id in conversation_histories:
        del conversation_histories[session_id]
        return True
    return False

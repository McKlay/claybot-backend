# Dependency Error Fix

## Problem
When starting uvicorn, there was a `ModuleNotFoundError`:
```
ModuleNotFoundError: No module named 'langchain.chains'
```

## Root Cause
LangChain has restructured its package organization in recent versions:
- `langchain.chains` → moved to separate packages
- `langchain.prompts` → moved to `langchain-core`
- Modern pattern uses `RunnableWithMessageHistory` instead of `ConversationChain`

## Solution

### 1. Updated Imports in `app/openai_utils.py`

**Before:**
```python
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
```

**After:**
```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
```

### 2. Updated Implementation

**Before (Old LangChain Pattern):**
```python
memory = ConversationBufferMemory(memory_key="history", return_messages=True)
conversation = ConversationChain(llm=llm, memory=memory, prompt=prompt)
response = conversation.predict(input=user_query)
```

**After (Modern LangChain Pattern):**
```python
# Store histories per session
conversation_histories: Dict[str, InMemoryChatMessageHistory] = {}

def get_session_history(session_id: str):
    if session_id not in conversation_histories:
        conversation_histories[session_id] = InMemoryChatMessageHistory()
    return conversation_histories[session_id]

# Create chain with history
chain = prompt | llm
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Invoke with session config
response = chain_with_history.invoke(
    {"input": user_query},
    config={"configurable": {"session_id": session_id}}
)
```

### 3. Added Missing Package to `requirements.txt`

```diff
  langchain
  langchain-openai
  langchain-community
+ langchain-core
```

## Benefits of the New Approach

1. ✅ **More Modern**: Uses LangChain's current best practices (LCEL - LangChain Expression Language)
2. ✅ **Better Type Safety**: Clearer interfaces and better IDE support
3. ✅ **More Flexible**: Easier to customize and extend
4. ✅ **Future-Proof**: Aligns with LangChain's current architecture

## Verification

Run the test:
```bash
python -c "from app.main import app; print('✅ Success!')"
```

Expected output: `✅ Success!`

## Status

✅ **FIXED** - All dependencies now load correctly
✅ **TESTED** - Import verification successful
✅ **READY** - Server can now start with `uvicorn app.main:app --reload`

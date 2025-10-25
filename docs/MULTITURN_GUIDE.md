# Multi-Turn Conversation Implementation Guide

## Overview
The chatbot now supports multi-turn conversations using LangChain, allowing users to have contextual conversations where the bot remembers previous messages within a session.

## Key Features

### 1. **Conversation Memory**
- Each conversation session maintains its own history
- Uses `ConversationBufferMemory` to store message history
- Sessions are identified by a unique `session_id`

### 2. **Session Management**
- Multiple users can have separate conversations simultaneously
- Each session maintains independent context
- Conversation history can be cleared per session

### 3. **Context-Aware Responses**
- The bot remembers previous messages in the conversation
- Can reference earlier topics and provide contextual follow-ups
- Still uses vectorstore for retrieving relevant portfolio information

## API Changes

### `/chat` Endpoint (Updated)

**Request Body:**
```json
{
  "message": "Your question here",
  "session_id": "unique-session-identifier"  // Optional, defaults to "default"
}
```

**Response:**
```json
{
  "response": "Bot's contextual response"
}
```

**Example Usage:**
```javascript
// First message
fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "What projects has Clay worked on?",
    session_id: "user-123"
  })
});

// Follow-up message (bot remembers context)
fetch('http://localhost:8000/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: "Tell me more about the first one",
    session_id: "user-123"  // Same session ID
  })
});
```

### `/clear-history` Endpoint (New)

Clears conversation history for a specific session.

**Request:**
```
POST /clear-history?session_id=user-123
```

**Response:**
```json
{
  "message": "Conversation history cleared for session: user-123"
}
```

## Implementation Details

### Dependencies Added
```
langchain
langchain-openai
langchain-community
```

### Files Modified

1. **`requirements.txt`**
   - Added LangChain dependencies

2. **`app/openai_utils.py`**
   - Added `get_chat_response_with_memory()` function with conversation memory
   - Added `clear_conversation_memory()` function
   - Kept original `get_chat_response()` for backward compatibility
   - Uses `ConversationBufferMemory` to store chat history
   - Uses `ChatOpenAI` and `ConversationChain` from LangChain

3. **`app/routes.py`**
   - Updated `ChatRequest` model to include `session_id`
   - Modified `/chat` endpoint to use new memory-enabled function
   - Added `/clear-history` endpoint for session management

## How It Works

1. **User sends a message** with a `session_id`
2. **System retrieves relevant context** from Supabase vectorstore
3. **Memory manager** checks if a conversation history exists for this session
4. **LangChain conversation chain** processes the message with:
   - System prompt (bot personality + context)
   - Conversation history (previous messages)
   - Current user message
5. **Response is generated** considering all previous context
6. **Conversation is updated** in memory for future messages

## Frontend Integration

### Basic Implementation
```javascript
class ChatSession {
  constructor(sessionId = null) {
    this.sessionId = sessionId || this.generateSessionId();
  }

  generateSessionId() {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  async sendMessage(message) {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: message,
        session_id: this.sessionId
      })
    });
    return await response.json();
  }

  async clearHistory() {
    const response = await fetch(
      `http://localhost:8000/clear-history?session_id=${this.sessionId}`,
      { method: 'POST' }
    );
    return await response.json();
  }
}

// Usage
const chat = new ChatSession();
const response1 = await chat.sendMessage("What projects has Clay worked on?");
const response2 = await chat.sendMessage("Tell me more about the first one");
```

### React Example
```jsx
import { useState, useEffect } from 'react';

function ChatBot() {
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState([]);

  useEffect(() => {
    // Generate session ID on component mount
    setSessionId(`session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  const sendMessage = async (userMessage) => {
    // Add user message to UI
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    // Send to API
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: userMessage,
        session_id: sessionId
      })
    });

    const data = await response.json();
    
    // Add bot response to UI
    setMessages(prev => [...prev, { role: 'bot', content: data.response }]);
  };

  const clearHistory = async () => {
    await fetch(`http://localhost:8000/clear-history?session_id=${sessionId}`, {
      method: 'POST'
    });
    setMessages([]);
  };

  return (
    <div>
      {/* Chat UI implementation */}
    </div>
  );
}
```

## Testing

Run the test script to verify multi-turn conversation:
```bash
python test_multiturn.py
```

This will test:
1. Context retention across multiple messages
2. Ability to reference previous topics
3. History clearing functionality
4. Multiple independent sessions

## Configuration

### Model Selection
By default, the system uses `gpt-4o-mini`. You can change this in `openai_utils.py`:

```python
def get_chat_response_with_memory(
    user_query: str, 
    context: str, 
    session_id: str = "default",
    model: str = "gpt-4o-mini"  # Change model here
) -> str:
```

### Memory Type
Current implementation uses `ConversationBufferMemory` which stores all messages. For production with many users, consider:

- `ConversationBufferWindowMemory` - Keep only last N messages
- `ConversationSummaryMemory` - Summarize old messages
- Database-backed memory for persistence

Example to limit history:
```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    memory_key="history",
    return_messages=True,
    k=10  # Keep only last 10 messages
)
```

## Best Practices

1. **Session ID Generation**: Use unique, unpredictable session IDs
2. **Memory Cleanup**: Implement periodic cleanup of old sessions
3. **Error Handling**: Always handle cases where memory might be corrupted
4. **Privacy**: Clear session data when user logs out
5. **Scalability**: For production, consider database-backed memory storage

## Migration Notes

- The old `get_chat_response()` function is still available for backward compatibility
- Frontend clients need to include `session_id` in requests
- If `session_id` is not provided, it defaults to "default"

## Troubleshooting

**Issue: Bot doesn't remember context**
- Verify the same `session_id` is being sent with each request
- Check that the conversation memory isn't being cleared unintentionally

**Issue: Memory grows too large**
- Implement `ConversationBufferWindowMemory` to limit history
- Add periodic cleanup of old sessions

**Issue: Different users share conversation history**
- Ensure each user has a unique `session_id`
- Don't use "default" for production use cases

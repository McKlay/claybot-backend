# Quick Start Guide - Multi-Turn Conversations

## 🚀 Getting Started in 5 Minutes

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the Server
```bash
uvicorn app.main:app --reload
```

### 3. Test Multi-Turn Conversation

#### Using Python:
```python
import requests

# Message 1
response = requests.post('http://localhost:8000/chat', json={
    'message': 'What projects has Clay worked on?',
    'session_id': 'my-session'
})
print(response.json()['response'])

# Message 2 (bot remembers context!)
response = requests.post('http://localhost:8000/chat', json={
    'message': 'Tell me more about the first one',
    'session_id': 'my-session'  # Same session ID
})
print(response.json()['response'])
```

#### Using cURL:
```bash
# Message 1
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are Clay'\''s skills?", "session_id": "test-123"}'

# Message 2 (remembers previous message)
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Which one is he best at?", "session_id": "test-123"}'
```

#### Using the Test Script:
```bash
python test_multiturn.py
```

### 4. Clear Conversation History
```bash
curl -X POST "http://localhost:8000/clear-history?session_id=test-123"
```

## 📝 Key Concepts

### Session ID
- **What**: Unique identifier for each conversation
- **Why**: Allows multiple users to have separate conversations
- **How**: Include in every request: `"session_id": "unique-id"`

### Multi-Turn Flow
```
User: "What projects has Clay worked on?"
Bot: "Clay has worked on AI Chatbot, Image Processing, ..."

User: "Tell me more about the first one"  👈 References "first one"
Bot: "The AI Chatbot project is..."  👈 Knows what "first one" means!
```

## 🎨 Frontend Integration

### HTML + JavaScript
```html
<!DOCTYPE html>
<html>
<body>
  <div id="chat"></div>
  <input id="input" type="text" />
  <button onclick="sendMessage()">Send</button>

  <script>
    const sessionId = `session-${Date.now()}`;
    
    async function sendMessage() {
      const message = document.getElementById('input').value;
      
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          session_id: sessionId
        })
      });
      
      const data = await response.json();
      document.getElementById('chat').innerHTML += 
        `<p><strong>You:</strong> ${message}</p>
         <p><strong>Bot:</strong> ${data.response}</p>`;
      
      document.getElementById('input').value = '';
    }
  </script>
</body>
</html>
```

### React Component
```jsx
import { useState, useEffect } from 'react';

function ChatBot() {
  const [sessionId, setSessionId] = useState('');
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');

  useEffect(() => {
    setSessionId(`session-${Date.now()}`);
  }, []);

  const sendMessage = async () => {
    const response = await fetch('http://localhost:8000/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: input,
        session_id: sessionId
      })
    });
    
    const data = await response.json();
    setMessages([...messages, 
      { role: 'user', text: input },
      { role: 'bot', text: data.response }
    ]);
    setInput('');
  };

  return (
    <div>
      {messages.map((msg, i) => (
        <div key={i}>{msg.role}: {msg.text}</div>
      ))}
      <input value={input} onChange={e => setInput(e.target.value)} />
      <button onClick={sendMessage}>Send</button>
    </div>
  );
}
```

## ❓ FAQ

**Q: Do I need to include session_id?**
A: No, it's optional. If not provided, it defaults to "default". But for multiple users, use unique IDs.

**Q: What happens if I use the same session_id for two different users?**
A: They will share the same conversation history (not recommended!).

**Q: How long is the conversation history stored?**
A: Currently stored in memory while the server is running. Clears on server restart.

**Q: Can I limit the conversation history length?**
A: Yes, modify `openai_utils.py` to use `ConversationBufferWindowMemory` with a `k` parameter.

**Q: Does this cost more than single-turn?**
A: Yes, because conversation history is sent with each request. Use message limits for cost control.

## 🔧 Configuration

### Change AI Model
Edit `app/openai_utils.py`:
```python
def get_chat_response_with_memory(
    model: str = "gpt-4o-mini"  # Change to "gpt-4", "gpt-3.5-turbo", etc.
)
```

### Limit Conversation History
Edit `app/openai_utils.py`:
```python
from langchain.memory import ConversationBufferWindowMemory

conversation_memories[session_id] = ConversationBufferWindowMemory(
    memory_key="history",
    return_messages=True,
    k=5  # Keep only last 5 messages
)
```

## 📚 Need More Help?

- **Detailed Guide**: See `MULTITURN_GUIDE.md`
- **Code Examples**: See `frontend_examples.js`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Test Script**: Run `python test_multiturn.py`

## ✅ Checklist

- [ ] Installed dependencies (`pip install -r requirements.txt`)
- [ ] Started server (`uvicorn app.main:app --reload`)
- [ ] Tested with `test_multiturn.py` or cURL
- [ ] Generated unique session IDs in frontend
- [ ] Included `session_id` in chat requests
- [ ] Tested conversation context retention
- [ ] Implemented clear history functionality

---

**Ready to deploy?** Make sure to set environment variables:
- `OPENAI_API_KEY`
- `SUPABASE_URL`
- `SUPABASE_KEY`

Happy chatting! 🎉

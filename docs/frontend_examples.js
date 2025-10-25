/**
 * Frontend Integration Example for Multi-Turn Conversation
 * 
 * This file demonstrates how to integrate the multi-turn conversation
 * chatbot into your frontend application.
 */

// ========================================
// 1. Basic JavaScript/TypeScript Class
// ========================================

class ClayBotSession {
  constructor(baseUrl = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
    this.sessionId = this.generateSessionId();
  }

  /**
   * Generate a unique session ID
   */
  generateSessionId() {
    return `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Send a message to the chatbot
   * @param {string} message - The user's message
   * @returns {Promise<string>} - The bot's response
   */
  async sendMessage(message) {
    try {
      const response = await fetch(`${this.baseUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          session_id: this.sessionId
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.response;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Clear the conversation history
   */
  async clearHistory() {
    try {
      const response = await fetch(
        `${this.baseUrl}/clear-history?session_id=${this.sessionId}`,
        { method: 'POST' }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.message;
    } catch (error) {
      console.error('Error clearing history:', error);
      throw error;
    }
  }

  /**
   * Start a new session (generates new session ID)
   */
  startNewSession() {
    this.sessionId = this.generateSessionId();
  }
}

// ========================================
// 2. Usage Example
// ========================================

async function exampleUsage() {
  // Create a new chat session
  const chat = new ClayBotSession('https://your-backend-url.com');

  // Send first message
  const response1 = await chat.sendMessage("What projects has Clay worked on?");
  console.log('Bot:', response1);

  // Send follow-up (bot remembers context)
  const response2 = await chat.sendMessage("Tell me more about the first one");
  console.log('Bot:', response2);

  // Clear history
  await chat.clearHistory();

  // Start fresh conversation
  const response3 = await chat.sendMessage("What are Clay's skills?");
  console.log('Bot:', response3);
}

// ========================================
// 3. React Hook Example
// ========================================

/**
 * Custom React hook for managing chatbot sessions
 * 
 * Usage in component:
 * const { messages, sendMessage, clearHistory, isLoading } = useChatBot();
 */
function useChatBot(baseUrl = 'http://localhost:8000') {
  const [sessionId, setSessionId] = React.useState('');
  const [messages, setMessages] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);

  // Generate session ID on mount
  React.useEffect(() => {
    setSessionId(`session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
  }, []);

  const sendMessage = async (userMessage) => {
    if (!userMessage.trim()) return;

    setIsLoading(true);

    // Add user message to chat
    const userMsg = { role: 'user', content: userMessage, timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);

    try {
      const response = await fetch(`${baseUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId
        })
      });

      const data = await response.json();

      // Add bot response to chat
      const botMsg = { role: 'bot', content: data.response, timestamp: new Date() };
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      console.error('Error:', error);
      const errorMsg = { 
        role: 'bot', 
        content: 'Sorry, I encountered an error. Please try again.', 
        timestamp: new Date() 
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const clearHistory = async () => {
    try {
      await fetch(`${baseUrl}/clear-history?session_id=${sessionId}`, {
        method: 'POST'
      });
      setMessages([]);
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  const startNewSession = () => {
    setSessionId(`session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`);
    setMessages([]);
  };

  return { messages, sendMessage, clearHistory, startNewSession, isLoading };
}

// ========================================
// 4. React Component Example
// ========================================

function ChatBot() {
  const { messages, sendMessage, clearHistory, isLoading } = useChatBot(
    'https://your-backend-url.com'
  );
  const [input, setInput] = React.useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      sendMessage(input);
      setInput('');
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chat-header">
        <h2>ClayBot</h2>
        <button onClick={clearHistory}>Clear History</button>
      </div>

      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
            <div className="message-time">
              {msg.timestamp.toLocaleTimeString()}
            </div>
          </div>
        ))}
        {isLoading && <div className="loading">ClayBot is typing...</div>}
      </div>

      <form onSubmit={handleSubmit} className="chat-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask me about Clay's projects..."
          disabled={isLoading}
        />
        <button type="submit" disabled={isLoading || !input.trim()}>
          Send
        </button>
      </form>
    </div>
  );
}

// ========================================
// 5. Vue.js Composition API Example
// ========================================

/**
 * Vue 3 Composition API composable for chatbot
 */
function useChatBotVue(baseUrl = 'http://localhost:8000') {
  const sessionId = ref('');
  const messages = ref([]);
  const isLoading = ref(false);

  onMounted(() => {
    sessionId.value = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  });

  const sendMessage = async (userMessage) => {
    if (!userMessage.trim()) return;

    isLoading.value = true;
    messages.value.push({ role: 'user', content: userMessage, timestamp: new Date() });

    try {
      const response = await fetch(`${baseUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage,
          session_id: sessionId.value
        })
      });

      const data = await response.json();
      messages.value.push({ role: 'bot', content: data.response, timestamp: new Date() });
    } catch (error) {
      console.error('Error:', error);
      messages.value.push({ 
        role: 'bot', 
        content: 'Sorry, I encountered an error.', 
        timestamp: new Date() 
      });
    } finally {
      isLoading.value = false;
    }
  };

  const clearHistory = async () => {
    try {
      await fetch(`${baseUrl}/clear-history?session_id=${sessionId.value}`, {
        method: 'POST'
      });
      messages.value = [];
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  };

  return { messages, sendMessage, clearHistory, isLoading };
}

// ========================================
// 6. Vanilla JavaScript Example
// ========================================

class SimpleChatUI {
  constructor(containerId, apiUrl) {
    this.container = document.getElementById(containerId);
    this.apiUrl = apiUrl;
    this.sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="chat-window">
        <div id="messages"></div>
        <form id="chat-form">
          <input type="text" id="message-input" placeholder="Ask me anything..." />
          <button type="submit">Send</button>
        </form>
        <button id="clear-btn">Clear History</button>
      </div>
    `;

    document.getElementById('chat-form').addEventListener('submit', (e) => {
      e.preventDefault();
      this.sendMessage();
    });

    document.getElementById('clear-btn').addEventListener('click', () => {
      this.clearHistory();
    });
  }

  async sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();
    if (!message) return;

    this.addMessage('user', message);
    input.value = '';

    try {
      const response = await fetch(`${this.apiUrl}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: message,
          session_id: this.sessionId
        })
      });

      const data = await response.json();
      this.addMessage('bot', data.response);
    } catch (error) {
      this.addMessage('bot', 'Error: Could not get response');
    }
  }

  addMessage(role, content) {
    const messagesDiv = document.getElementById('messages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${role}`;
    msgDiv.textContent = content;
    messagesDiv.appendChild(msgDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  async clearHistory() {
    try {
      await fetch(`${this.apiUrl}/clear-history?session_id=${this.sessionId}`, {
        method: 'POST'
      });
      document.getElementById('messages').innerHTML = '';
    } catch (error) {
      console.error('Error clearing history:', error);
    }
  }
}

// Initialize the chat UI
// const chat = new SimpleChatUI('chat-container', 'https://your-backend-url.com');

// ========================================
// Export for module usage
// ========================================

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { ClayBotSession, useChatBot, SimpleChatUI };
}

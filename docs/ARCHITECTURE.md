# Multi-Turn Conversation Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Vue/JS)                      │
│                                                                      │
│  ┌────────────────┐     ┌─────────────────┐    ┌─────────────────┐ │
│  │  Chat UI       │     │  Session Mgmt   │    │  Message State  │ │
│  │  - Input       │────▶│  - session_id   │───▶│  - User msgs    │ │
│  │  - Messages    │     │  - Clear button │    │  - Bot replies  │ │
│  │  - Send button │     │  - New session  │    │  - Timestamps   │ │
│  └────────────────┘     └─────────────────┘    └─────────────────┘ │
│                                   │                                  │
└───────────────────────────────────┼──────────────────────────────────┘
                                    │ HTTP POST
                                    │ { message, session_id }
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                         FASTAPI BACKEND                              │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                      /chat ENDPOINT                             │ │
│  │                                                                  │ │
│  │  1. Receive: { message, session_id }                           │ │
│  │  2. Query vectorstore for context                              │ │
│  │  3. Get/create conversation memory for session                 │ │
│  │  4. Process with LangChain + OpenAI                            │ │
│  │  5. Update conversation memory                                 │ │
│  │  6. Return: { response }                                       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                  /clear-history ENDPOINT                        │ │
│  │                                                                  │ │
│  │  1. Receive: session_id                                        │ │
│  │  2. Delete conversation memory for session                     │ │
│  │  3. Return: { message: "cleared" }                             │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
└───┬──────────────────────────┬──────────────────────┬───────────────┘
    │                          │                      │
    │ Query Context            │ Store/Retrieve       │ Generate Response
    │                          │ Memory               │
    ▼                          ▼                      ▼
┌──────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│   SUPABASE   │    │  CONVERSATION       │    │   OPENAI API    │
│  (pgvector)  │    │  MEMORY STORE       │    │                 │
│              │    │                     │    │  ┌───────────┐  │
│  ┌────────┐  │    │  session-1:         │    │  │ gpt-4o    │  │
│  │ Docs   │  │    │  ┌──────────────┐   │    │  │  -mini    │  │
│  │ Table  │  │    │  │ Message 1    │   │    │  └───────────┘  │
│  │        │  │    │  │ Response 1   │   │    │                 │
│  │ Vector │  │    │  │ Message 2    │   │    │  LangChain      │
│  │ Search │  │    │  │ Response 2   │   │    │  Integration    │
│  └────────┘  │    │  └──────────────┘   │    │                 │
│              │    │                     │    │                 │
│  Portfolio   │    │  session-2:         │    │                 │
│  Context     │    │  ┌──────────────┐   │    │                 │
│              │    │  │ Message A    │   │    │                 │
│              │    │  │ Response A   │   │    │                 │
│              │    │  └──────────────┘   │    │                 │
└──────────────┘    └─────────────────────┘    └─────────────────┘
```

## Conversation Flow Diagram

```
USER                BACKEND                 MEMORY              OPENAI
  │                   │                       │                   │
  │  Message 1        │                       │                   │
  ├──────────────────▶│                       │                   │
  │  "What projects"  │                       │                   │
  │  session: A       │  Get/Create Memory    │                   │
  │                   ├──────────────────────▶│                   │
  │                   │                       │  Empty (new)      │
  │                   │◀──────────────────────┤                   │
  │                   │                       │                   │
  │                   │  Query Context        │                   │
  │                   │  (vectorstore)        │                   │
  │                   │                       │                   │
  │                   │  Generate Response    │                   │
  │                   ├───────────────────────┼──────────────────▶│
  │                   │  Context + Message    │                   │
  │                   │                       │                   │
  │                   │◀──────────────────────┼───────────────────┤
  │                   │                       │  "Clay has..."    │
  │  Response         │                       │                   │
  │◀──────────────────┤  Save to Memory       │                   │
  │  "Clay has        ├──────────────────────▶│                   │
  │   worked on..."   │                       │  [Msg1, Resp1]    │
  │                   │                       │                   │
  │                   │                       │                   │
  │  Message 2        │                       │                   │
  ├──────────────────▶│                       │                   │
  │  "Tell me more"   │                       │                   │
  │  session: A       │  Get Memory           │                   │
  │                   ├──────────────────────▶│                   │
  │                   │                       │  [Msg1, Resp1]    │
  │                   │◀──────────────────────┤                   │
  │                   │                       │                   │
  │                   │  Query Context        │                   │
  │                   │  (vectorstore)        │                   │
  │                   │                       │                   │
  │                   │  Generate Response    │                   │
  │                   ├───────────────────────┼──────────────────▶│
  │                   │  Context + History +  │                   │
  │                   │  Message 2            │                   │
  │                   │                       │                   │
  │                   │◀──────────────────────┼───────────────────┤
  │                   │                       │  "The first       │
  │  Response         │                       │   project was..." │
  │◀──────────────────┤  Update Memory        │                   │
  │  "The first       ├──────────────────────▶│                   │
  │   project was..." │                       │  [Msg1, Resp1,    │
  │                   │                       │   Msg2, Resp2]    │
  │                   │                       │                   │
```

## Memory Structure

```
conversation_memories = {
    "session-user-123": ConversationBufferMemory {
        history: [
            HumanMessage("What projects has Clay worked on?"),
            AIMessage("Clay has worked on AI Chatbot, Image Processing..."),
            HumanMessage("Tell me more about the first one"),
            AIMessage("The AI Chatbot project is a portfolio chatbot...")
        ]
    },
    "session-user-456": ConversationBufferMemory {
        history: [
            HumanMessage("What are Clay's skills?"),
            AIMessage("Clay has expertise in Python, React, Machine Learning...")
        ]
    }
}
```

## Data Flow (Step by Step)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: User sends message                                      │
├─────────────────────────────────────────────────────────────────┤
│ POST /chat                                                       │
│ {                                                                │
│   "message": "What projects has Clay worked on?",               │
│   "session_id": "session-123"                                   │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Query vectorstore for relevant context                 │
├─────────────────────────────────────────────────────────────────┤
│ vectorstore.query("What projects has Clay worked on?")         │
│                                                                  │
│ Returns:                                                         │
│ "Clay's projects include: AI Chatbot, Image Processing,        │
│  Neural Network Logic Gates, Dog Breed Classifier..."          │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Get/Create conversation memory                          │
├─────────────────────────────────────────────────────────────────┤
│ if "session-123" not in conversation_memories:                  │
│     conversation_memories["session-123"] =                      │
│         ConversationBufferMemory()                              │
│                                                                  │
│ memory = conversation_memories["session-123"]                   │
│ history = memory.load_memory_variables({})                      │
│ # First message: history is empty                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Build prompt with context + history                    │
├─────────────────────────────────────────────────────────────────┤
│ System: "You are ClayBot, assistant for Clay's portfolio.      │
│          Use this context: [vectorstore context]               │
│          Remember previous messages."                           │
│                                                                  │
│ History: [empty on first message]                               │
│                                                                  │
│ Human: "What projects has Clay worked on?"                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Send to OpenAI via LangChain                           │
├─────────────────────────────────────────────────────────────────┤
│ conversation.predict(input="What projects...")                  │
│                                                                  │
│ OpenAI processes with:                                          │
│ - System prompt (ClayBot personality + context)                │
│ - Conversation history                                          │
│ - Current message                                               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Receive response from OpenAI                           │
├─────────────────────────────────────────────────────────────────┤
│ Response: "Clay has worked on several exciting projects        │
│            including an AI Chatbot, Image Processing tools,    │
│            and Neural Network implementations..."               │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 7: Update conversation memory                             │
├─────────────────────────────────────────────────────────────────┤
│ memory.save_context(                                            │
│     {"input": "What projects has Clay worked on?"},            │
│     {"output": "Clay has worked on..."}                        │
│ )                                                                │
│                                                                  │
│ Memory now contains:                                            │
│ - HumanMessage("What projects has Clay worked on?")            │
│ - AIMessage("Clay has worked on...")                           │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ STEP 8: Return response to user                                │
├─────────────────────────────────────────────────────────────────┤
│ {                                                                │
│   "response": "Clay has worked on several exciting projects..." │
│ }                                                                │
└─────────────────────────────────────────────────────────────────┘
```

## Session Isolation

```
┌───────────────────────────────────────────────────────────────┐
│                    MULTIPLE SESSIONS                           │
├───────────────────────────────────────────────────────────────┤
│                                                                │
│  Session A (User 1)              Session B (User 2)           │
│  ═══════════════════             ═══════════════════          │
│                                                                │
│  "What projects?"                "What skills?"               │
│       ↓                               ↓                       │
│  "Clay has X, Y, Z..."           "Python, React..."           │
│       ↓                               ↓                       │
│  "Tell me about X"               "Is he good at ML?"          │
│       ↓                               ↓                       │
│  "X is a project..."             "Yes, he has..."             │
│                                                                │
│  ✅ Separate histories           ✅ No cross-talk              │
│  ✅ Independent context          ✅ Isolated memory            │
│                                                                │
└───────────────────────────────────────────────────────────────┘
```

## Key Components

### 1. ConversationBufferMemory
- Stores full conversation history
- Maintains message order
- Returns messages in LangChain format

### 2. ConversationChain
- Orchestrates the conversation flow
- Integrates memory with LLM
- Handles prompt formatting

### 3. ChatOpenAI
- LangChain wrapper for OpenAI API
- Supports streaming and callbacks
- Manages API credentials

### 4. Session Management
- In-memory dictionary (current)
- Per-session isolation
- Easy to extend to database storage

## Scalability Considerations

```
Current (In-Memory)          Future (Database-Backed)
═══════════════════          ════════════════════════

┌─────────────────┐          ┌─────────────────────┐
│  Python Dict    │          │   PostgreSQL        │
│                 │          │   ┌──────────────┐  │
│  {              │          │   │ sessions     │  │
│    session-1,   │   ──▶    │   │ - id         │  │
│    session-2    │          │   │ - history    │  │
│  }              │          │   │ - updated_at │  │
│                 │          │   └──────────────┘  │
│  Lost on        │          │                     │
│  restart        │          │   Persistent        │
└─────────────────┘          └─────────────────────┘
```

---

**Legend:**
- `─▶` Data flow
- `┌─┐` Component boundary
- `│` Connection
- `═` Emphasis
- `✅` Feature/Benefit

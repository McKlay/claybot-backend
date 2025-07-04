# ClayBot Backend

This is the backend API for Clay Sarte's portfolio chatbot (ClayBot), built using FastAPI, Supabase pgvector, and OpenAI embeddings.

## Features

- Embeds Markdown content using `text-embedding-3-small`
- Stores vectors in Supabase `documents` table
- Retrieves top-k chunks using pgvector similarity
- Serves chatbot via `/chat` endpoint
- Dockerized for easy deployment to Render

## Folder Structure

```bash

chatbot-backend/
├── app/
│   ├── main.py           # FastAPI app
│   ├── routes.py         # /chat and /embed endpoints
│   ├── vectorstore.py    # Supabase + pgvector logic
│   ├── openai\_utils.py   # Embedding + chat helper
│   └── data\_loader.py    # Load + embed markdown files
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md

```

## Deployment (Render)

1. Push repo to GitHub
2. Create new **Web Service** on [Render](https://render.com)
3. Select this repo → Docker → Python 3.10
4. Set environment variables:
   - `OPENAI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
5. Done — Render will build and host your API

## 🔗 Endpoints
```bash

| Route    | Method | Description                       |
|----------|--------|-----------------------------------|
| `/chat`  | POST   | Query chatbot with user message   |
| `/embed` | POST   | (Optional) Embed new content      |

```

---

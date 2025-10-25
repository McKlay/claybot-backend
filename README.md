# 🤖 ClayBot Backend

This is the backend API for **Clay Sarte's portfolio chatbot (ClayBot)** — built using:

- OpenAI gpt-5-nano + Embeddings (`text-embedding-3-small`)
- Supabase with `pgvector` for vector storage & similarity search
- FastAPI for REST API endpoints
- Docker for deployment to Render

---

## 💡 How the Whole Flow Works

### Architectural Flow (RAG with GPT)

#### 1. PREPROCESSING (One-time):
Your Text Content → **Embedding Model** (`text-embedding-3-small`)  
→ Store vectors + original text in **Supabase**

#### 2. AT RUNTIME (User asks question):
User Question → Embed → Vector  
→ Similarity Search in Supabase → Top Matching Chunks  
→ Combine chunks + user question → GPT-5-nano prompt  
→ GPT-3.5 returns natural-language answer

---

## Features

- Embeds Markdown project descriptions into vector form
- Stores in `documents` table using `pgvector` for similarity search
- Supports `/chat` endpoint for real-time questions
- Uses OpenAI gpt-5-nano for answer generation
- Dockerized for easy deployment via Render
- CORS-restricted to Netlify frontend (`clay-portfolio.netlify.app`)
- Includes `/healthz` endpoint for uptime monitoring

---

## Folder Structure

```

chatbot-backend/
├── app/
│   ├── main.py           # FastAPI entrypoint + CORS + health check
│   ├── routes.py         # /chat and /embed endpoints
│   ├── vectorstore.py    # Supabase + pgvector search and storage
│   ├── openai_utils.py   # GPT & embedding API helpers
│   └── data_loader.py    # Chunk + embed all markdown files
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md

````

---

## Deployment (Render)

1. Push this repo to GitHub
2. Create a new **Web Service** on [Render](https://render.com)
3. Select this repo → Choose **Docker** → Python 3.10
4. Set environment variables:

```env
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-service-role-key
````

5. Click **Deploy Web Service**

> Your backend will be live.

---

## API Endpoints

| Route      | Method | Description                               |
| ---------- | ------ | ----------------------------------------- |
| `/chat`    | POST   | Accepts a `message`, returns GPT reply    |
| `/embed`   | POST   | (Optional) Embed additional text chunks   |
| `/healthz` | GET    | Uptime monitor ping (returns status OK)   |
| `/`        | GET    | Suppresses Render 404 logs with simple OK |

---

## CORS

This backend only accepts requests from:

```
https://clay-portfolio.netlify.app
```

Defined in `main.py` using:

```python
allow_origin_regex=r"https:\/\/clay-portfolio\.netlify\.app"
```

---

## Tech Stack

| Layer     | Tool                            |
| --------- | ------------------------------- |
| Backend   | FastAPI                         |
| LLM       | OpenAI gpt-5-nano            |
| Embedding | OpenAI `text-embedding-3-small` |
| Vector DB | Supabase + pgvector             |
| Hosting   | Render (Dockerized Web Service) |

---

## ✅ Status

ClayBot is now fully live and integrated into Clay's personal portfolio:  
🔗 [`https://clay-portfolio.netlify.app`](https://clay-portfolio.netlify.app)

```
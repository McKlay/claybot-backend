from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as chatbot_router
from dotenv import load_dotenv
import os

# ✅ Load .env variables early
load_dotenv()

app = FastAPI(
    title="ClayBot API",
    description="Chatbot backend for clay-portfolio site.",
    version="1.0.0"
)

# ✅ Dev or Production toggle
IS_DEV = os.getenv("IS_DEV", "false").lower() == "true"

# ✅ Conditional CORS config
if IS_DEV:
    # For local testing only
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Strict production access via regex (Netlify only)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"https:\/\/clay-portfolio\.netlify\.app",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# ✅ Health check for uptime tools
@app.get("/healthz")
def health():
    return {"status": "ok"}

# ✅ Render root fallback
@app.get("/")
async def root():
    return {"status": "ClayBot backend is live."}

# ✅ Include chatbot API routes
app.include_router(chatbot_router)

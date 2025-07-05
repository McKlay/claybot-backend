from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as chatbot_router

app = FastAPI(
    title="ClayBot API",
    description="Chatbot backend for clay-portfolio site.",
    version="1.0.0"
)

# ✅ CORS settings — secure and production-ready for Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https:\/\/clay-portfolio\.netlify\.app",  # ✅ only allow Netlify frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Health check for uptime services (e.g., UptimeRobot)
@app.get("/healthz")
def health():
    return {"status": "ok"}

# ✅ Minimal root response (to suppress Render 404 logs)
@app.get("/")
async def root():
    return {"status": "ClayBot backend is live."}

# ✅ Include chatbot routes
app.include_router(chatbot_router)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as chatbot_router

app = FastAPI(
    title="ClayBot API",
    description="Chatbot backend for clay-portfolio site.",
    version="1.0.0"
)

# CORS settings (adjust allow_origins before production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace with your Netlify domain later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routes from routes.py
app.include_router(chatbot_router)

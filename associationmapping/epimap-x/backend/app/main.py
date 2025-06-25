from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import create_db_and_tables

app = FastAPI(
    title="EpiMap X API",
    description="Epigenome-Wide Association Studies (EWAS) Analysis Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "EpiMap X - EWAS Analysis Platform", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
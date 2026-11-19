"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.api.routes import router

app = FastAPI(
    title="Leclerc Labs API",
    description="Race intelligence API backed by OpenF1 data.",
    version="0.9.0",
)

# CORS allows the deployed React origin as well as the local dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router)

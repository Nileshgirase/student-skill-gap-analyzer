from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import Base, engine
import app.models  # Ensures models are registered with Base.metadata
from app.routes import health, auth, analyses, roadmaps


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database schemas (if any models are registered)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description=(
        "Backend API for the Student Skill Gap Analyzer and Personalized Learning "
        "Roadmap Provider."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS for local development with frontend
origins = [
    settings.frontend_origin,
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routes
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(analyses.router)
app.include_router(roadmaps.router)


@app.get(
    "/",
    summary="Root Service Information",
    description="Provides quick links and information about the Student Skill Gap Analyzer API.",
    tags=["Root"],
)
def root():
    return JSONResponse(
        content={
            "app_name": settings.app_name,
            "version": "0.1.0",
            "status": "online",
            "docs_url": "/docs",
            "health_check": "/api/health",
        }
    )

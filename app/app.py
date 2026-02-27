from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database.db import create_db_and_tables
from .database.models import User, RefreshToken
from .routers import auth
from .dependencies import get_current_user


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    await create_db_and_tables()
    yield
    print("Shutting down...")


app = FastAPI(
    title="Authentication Microservice",
    description="A simple authentication microservice using FastAPI, SQLModel, and JWT.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1", tags=["Authentication"])

# Health Check
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "service": "auth-microservice"}

# ==========================================
# THE PROTECTED TEST ROUTE
# ==========================================
@app.get("/api/v1/users/me", tags=["Users"])
async def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    This endpoint is locked down. 
    If you don't provide a valid Bearer token, the dependency will throw a 401 before 
    this code even executes.
    """
    return {
        "message": "Authentication successful! Your RS256 JWT is valid.",
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role
    }


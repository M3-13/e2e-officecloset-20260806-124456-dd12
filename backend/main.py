import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from auth.router import router as auth_router
from config import settings
from outfits.router import router as outfits_router
from wardrobe.router import router as wardrobe_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    from database import Base, engine

    Base.metadata.create_all(bind=engine)
    os.makedirs("uploads", exist_ok=True)
    logger.info("Database tables created, uploads directory ready")
    yield


app = FastAPI(
    title="Glamouröser Kleiderschrank-Manager",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(auth_router)
app.include_router(outfits_router)
app.include_router(wardrobe_router)


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok"}

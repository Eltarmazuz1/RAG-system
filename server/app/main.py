import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.utils.logging_config import setup_logging

# Setup logging before app startup
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up RAG Chat App...")
    logger.info(f"LLM Provider: {settings.LLM_PROVIDER}")
    logger.info(f"Vector DB URL: {settings.VECTOR_DB_URL}")
    yield
    logger.info("Shutting down RAG Chat App...")

app = FastAPI(title="RAG Chat App", lifespan=lifespan)

from app.routes.files import router as files_router
from app.routes.chat import router as chat_router

app.include_router(files_router)
app.include_router(chat_router)

from app.utils.middleware import auth_middleware
app.middleware("http")(auth_middleware)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

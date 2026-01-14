import logging
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.text_splitter import split_text_into_chunks
from app.services.embeddings import embeddings_service
from app.services.vector_store import vector_store

router = APIRouter(prefix="/api/files", tags=["files"])
logger = logging.getLogger(__name__)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a text file, chunk it, embed it, and store in vector DB.
    """
    logger.info(f"Received file upload: {file.filename}")
    
    # Validation
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")
    
    # 1. Read file
    try:
        content_bytes = await file.read()
        # Assume UTF-8 text for now
        text_content = content_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(status_code=400, detail="Invalid file content. Please upload a UTF-8 text file.")

    if not text_content:
        raise HTTPException(status_code=400, detail="File is empty")

    document_id = str(uuid.uuid4())
    
    # 2. Chunk text
    chunks = split_text_into_chunks(
        text=text_content, 
        document_id=document_id,
        source_file=file.filename
    )
    logger.info(f"Split document into {len(chunks)} chunks.")

    if not chunks:
        return {"document_id": document_id, "num_chunks": 0, "message": "No text chunks created."}

    # 3. Generate Embeddings
    chunk_texts = [c.text for c in chunks]
    try:
        embeddings = await embeddings_service.embed_texts(chunk_texts)
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate embeddings")

    # 4. Upsert to Vector DB
    # Ensure collection exists first (best effort, or do it on startup)
    await vector_store.ensure_collection()
    
    try:
        await vector_store.upsert_chunks(chunks, embeddings)
    except Exception as e:
        logger.error(f"Upsert failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to store chunks in vector DB")

    return {
        "document_id": document_id,
        "num_chunks": len(chunks),
        "message": "File processed and indexed successfully"
    }

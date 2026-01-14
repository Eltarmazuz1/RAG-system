import uuid
from app.models.schemas import Chunk

def split_text_into_chunks(text: str, document_id: str, source_file: str, chunk_size: int = 1000, overlap: int = 100) -> list[Chunk]:
    """
    Split text into overlapping chunks.
    Simple sliding window character-based splitter.
    """
    chunks = []
    text_len = len(text)
    start = 0
    chunk_index = 0

    while start < text_len:
        end = min(start + chunk_size, text_len)
        chunk_text = text[start:end]
        
        # Don't create empty chunks
        if not chunk_text.strip():
            start += chunk_size - overlap
            continue

        chunk_id = str(uuid.uuid4())
        chunks.append(Chunk(
            id=chunk_id,
            document_id=document_id,
            text=chunk_text,
            metadata={
                "document_id": document_id,
                "source_file": source_file,
                "chunk_index": chunk_index
            }
        ))

        chunk_index += 1
        start += (chunk_size - overlap)
        
        # Prevent infinite loop if overlap >= chunk_size (logic error check)
        if (chunk_size - overlap) <= 0:
            break

    return chunks

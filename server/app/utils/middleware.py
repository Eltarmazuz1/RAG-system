from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.config import settings

async def auth_middleware(request: Request, call_next):
    path = request.url.path
    
    # Allow health, docs, and openapi without auth
    if (path.startswith("/health") or 
        path.startswith("/docs") or 
        path.startswith("/redoc") or 
        path.startswith("/openapi")):
        return await call_next(request)
    
    # Check Header
    token = request.headers.get("X-API-TOKEN")
    if token != settings.API_TOKEN:
        return JSONResponse(
            status_code=401,
            content={"detail": "Invalid or missing API token."}
        )

    response = await call_next(request)
    return response

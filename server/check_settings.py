from app.config import settings
import os

print(f"LLM_PROVIDER: {settings.LLM_PROVIDER}")
print(f"LLM_MODEL: {settings.LLM_MODEL}")
print(f"OPENAI_API_KEY set in settings: {'Yes' if settings.OPENAI_API_KEY else 'No'}")
if settings.OPENAI_API_KEY:
    print(f"Key starts with: {settings.OPENAI_API_KEY[:10]}...")
    print(f"Key length: {len(settings.OPENAI_API_KEY)}")

print(f"OPENAI_API_KEY in os.environ: {'Yes' if 'OPENAI_API_KEY' in os.environ else 'No'}")

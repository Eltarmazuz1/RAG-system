from functools import lru_cache
from fastapi import Depends
from app.config import Settings, settings

@lru_cache()
def get_settings() -> Settings:
    """
    Cached dependency for settings.
    """
    return settings

# Example usage in a route:
# def my_route(settings: Settings = Depends(get_settings)): ...

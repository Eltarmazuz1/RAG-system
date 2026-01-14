import logging
import sys

def setup_logging():
    """
    Configure the standard logging for the application.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Console Handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    # Avoid duplicate handlers if setup_logging is called multiple times
    if not logger.handlers:
        logger.addHandler(handler)

    logging.getLogger("uvicorn.access").handlers = logger.handlers

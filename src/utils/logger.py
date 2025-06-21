import logging

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
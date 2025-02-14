"""
Logging configuration module.

This module sets up logging using Loguru, ensuring logs are rotated when they exceed 1 MB.
"""

from loguru import logger

# Configure Loguru logging
logger.add(
    "bot.log",
    rotation="1 MB",  # Rotate logs when file reaches 1 MB
    level="INFO",  # Log level: INFO and above
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

import os
import json
import time
from contextlib import contextmanager
from app.utils.logger import logger

@contextmanager
def timer(name: str):
    """
    Context manager to log the execution time of a block of code.
    Yields a dictionary that will be populated with the elapsed time in seconds.
    """
    start_time = time.perf_counter()
    elapsed = {"time": 0.0}
    try:
        yield elapsed
    finally:
        elapsed["time"] = time.perf_counter() - start_time
        logger.info(f"{name} execution took {elapsed['time']:.4f} seconds")

def load_json_file(filepath: str) -> dict:
    """
    Utility function to load and parse a JSON file with logging and error handling.
    """
    if not os.path.exists(filepath):
        logger.error(f"JSON file not found: {filepath}")
        raise FileNotFoundError(f"File not found at path: {filepath}")
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"JSON format error in {filepath}: {e}")
        raise ValueError(f"Invalid JSON format in file: {filepath}")
    except Exception as e:
        logger.error(f"Error loading file {filepath}: {str(e)}")
        raise

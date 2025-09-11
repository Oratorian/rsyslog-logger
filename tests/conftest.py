"""
Pytest configuration and fixtures for logger tests.
"""

import pytest
import os
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    if os.path.exists(temp_dir):
        # Windows needs time to release file handles
        import time
        import gc

        gc.collect()
        time.sleep(0.1)  # Small delay for Windows file handle cleanup
        try:
            shutil.rmtree(temp_dir)
        except PermissionError:
            # If still locked, try again after a longer delay
            time.sleep(0.5)
            shutil.rmtree(temp_dir)


@pytest.fixture
def temp_log_file(temp_dir):
    """Provide a temporary log file path."""
    return os.path.join(temp_dir, "test.log")


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration after each test."""
    import logging

    # Clear all existing handlers and loggers
    logging.getLogger().handlers.clear()

    # Reset logging configuration
    for name in list(logging.Logger.manager.loggerDict.keys()):
        if name.startswith("test_") or name == "Rsyslog-Logger":
            logger = logging.getLogger(name)
            logger.handlers.clear()
            logger.setLevel(logging.NOTSET)

    yield

    # Cleanup after test - close all handlers properly
    import gc

    # Force close all file handlers
    for name in list(logging.Logger.manager.loggerDict.keys()):
        logger = logging.getLogger(name)
        for handler in logger.handlers[:]:
            if hasattr(handler, "close"):
                handler.close()
            logger.removeHandler(handler)

    # Clear root logger handlers too
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if hasattr(handler, "close"):
            handler.close()
        root_logger.removeHandler(handler)

    # Force garbage collection to release file handles
    gc.collect()

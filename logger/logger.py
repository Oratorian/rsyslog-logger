#!/usr/bin/env python3
"""!
********************************************************************************
@brief  Professional logging system with rsyslog-style formatting and rotation

@file   logger.py
@author Mahesvara ( https://github.com/Oratorian )
@copyright Mahesvara ( https://github.com/Oratorian )
********************************************************************************
"""

import logging
import sys
import os
from datetime import datetime
import glob
import config

# Global flag to ensure log rotation only happens once per application run
_log_rotated = False


class SizeRotatingFileHandler(logging.FileHandler):
    """
    Custom file handler that rotates log files when they reach maximum size.
    """

    def __init__(self, filename, max_size=10 * 1024 * 1024, **kwargs):
        """
        Initialize the size-rotating file handler.

        Args:
            filename: Path to the log file
            max_size: Maximum file size before rotation in bytes (default: 10MB)
            **kwargs: Additional arguments passed to FileHandler
        """
        super().__init__(filename, **kwargs)
        self.max_size = max_size  # 10MB default
        self.baseFilename = os.path.abspath(filename)

    def emit(self, record):
        """
        Emit a record, rotating the file if necessary.
        """
        try:
            if self.should_rotate():
                self.rotate()
        except Exception:
            pass  # Don't let rotation errors stop logging

        super().emit(record)

    def should_rotate(self):
        """
        Check if the log file should be rotated based on size.
        """
        try:
            if os.path.exists(self.baseFilename):
                return os.path.getsize(self.baseFilename) >= self.max_size
        except OSError:
            pass
        return False

    def rotate(self):
        """
        Rotate the log file using copy-and-truncate method.
        This works even when the file is open by our handler.
        """
        try:
            # Flush any pending writes
            if self.stream:
                self.stream.flush()

            # Rotate using copy-and-truncate (works with open handles)
            rotate_log_file(self.baseFilename, force=False)  # Size-based rotation

            # No need to reopen - the existing handle now points to truncated file
        except Exception:
            pass  # Don't let rotation errors stop logging


def rotate_log_file(log_file_path, force=False):
    """
    Rotate existing log file by copying it with a number suffix and truncating original.
    This method works on Windows even when the file is open by handlers.

    Args:
        log_file_path: Path to the log file to rotate
        force: Force rotation even if file is small (used for app restart)
    """
    if not os.path.exists(log_file_path):
        return  # No existing log file to rotate

    # Check file size for rotation (unless forced)
    if not force:
        try:
            file_size = os.path.getsize(log_file_path)
            max_size = getattr(config, "LOG_MAX_SIZE", 10 * 1024 * 1024)  # Default 10MB
            if file_size < max_size:
                return  # File not large enough for rotation
        except OSError:
            return  # Can't check size, skip rotation

    # Get the directory and base name
    log_dir = os.path.dirname(log_file_path)
    log_name = os.path.basename(log_file_path)

    # Find existing rotated files to determine next number
    pattern = os.path.join(log_dir, f"{log_name}.*")
    existing_files = glob.glob(pattern)

    # Extract numbers from existing rotated files
    numbers = []
    for file_path in existing_files:
        suffix = file_path.split(f"{log_file_path}.")[-1]
        try:
            numbers.append(int(suffix))
        except ValueError:
            # Ignore files with non-numeric suffixes
            continue

    # Determine next number (start from 1 if no rotated files exist)
    next_number = max(numbers) + 1 if numbers else 1

    # Rotate the current log file using copy-and-truncate method
    # This works on Windows even when file handles are open
    rotated_path = f"{log_file_path}.{next_number}"
    try:
        import shutil

        # Copy the current log to rotated name
        shutil.copy2(log_file_path, rotated_path)

        # Truncate the original file (this works even with open handles)
        with open(log_file_path, "w") as f:
            pass  # Truncate to 0 bytes

        print(f"Rotated log file: {log_file_path} -> {rotated_path}")

        # Clean up old rotated files based on LOG_BACKUP_COUNT
        cleanup_old_log_files(log_file_path)

    except OSError as e:
        print(f"Warning: Could not rotate log file {log_file_path}: {e}")


def cleanup_old_log_files(log_file_path, backup_count=5):
    """
    Clean up old rotated log files, keeping only the specified number of backups.

    Args:
        log_file_path: Path to the main log file
        backup_count: Maximum number of backup files to keep (default: 5)

    Example:
        >>> cleanup_old_log_files("/var/log/app.log", 10)  # Keep 10 backups
    """
    try:
        # Get directory and base name
        log_dir = os.path.dirname(log_file_path)
        log_name = os.path.basename(log_file_path)

        # Find all rotated files
        pattern = os.path.join(log_dir, f"{log_name}.*")
        existing_files = glob.glob(pattern)

        # Extract numbers and sort by number (highest first)
        numbered_files = []
        for file_path in existing_files:
            suffix = file_path.split(f"{log_file_path}.")[-1]
            try:
                number = int(suffix)
                numbered_files.append((number, file_path))
            except ValueError:
                # Ignore files with non-numeric suffixes
                continue

        # Sort by number (descending)
        numbered_files.sort(key=lambda x: x[0], reverse=True)

        # Remove files beyond backup count
        files_to_remove = numbered_files[backup_count:]
        for number, file_path in files_to_remove:
            try:
                os.remove(file_path)
                print(f"Removed old log file: {file_path}")
            except OSError as e:
                print(f"Warning: Could not remove old log file {file_path}: {e}")

    except Exception as e:
        print(f"Warning: Error during log cleanup: {e}")


def setup_logger(
    name="Rsyslog-Logger",
    log_file="Rsyslog-Logger.log",
    log_level="INFO",
    log_format="rsyslog",
    console_log_level="INFO",
):
    """
    Setup logger with rsyslog-style formatting

    Args:
        name: Logger name (default: "Rsyslog-Logger")
        log_file: Path to log file (default: "Rsyslog-Logger.log", None for console only)
        log_level: Log level string (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format style ("rsyslog" or "simple")
        console_log_level: Console log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger: Configured logger instance with rsyslog formatting and rotation

    Example:
        >>> logger = setup_logger()  # Uses defaults
        >>> logger = setup_logger("myapp", "/var/log/myapp.log", "DEBUG")
        >>> logger.info("Application started")
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(numeric_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Create formatter based on style
    if log_format == "rsyslog":
        # rsyslog style: Jan 1 12:34:56 hostname program[pid]: level: message
        formatter = RsyslogFormatter()
    else:
        # Simple style: 2025-01-01 12:34:56 - LEVEL - message
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

    # File handler (if specified)
    if log_file:
        try:
            # Ensure log directory exists
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            # Rotate existing log file ONLY once per application startup
            global _log_rotated
            if not _log_rotated:
                rotate_log_file(log_file, force=True)  # Force rotation on app startup
                _log_rotated = True

            file_handler = SizeRotatingFileHandler(log_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

            # When file logging is active, minimize console output
            console_level = console_log_level
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(getattr(logging, console_level, logging.CRITICAL))
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        except Exception as e:
            # If file logging fails, fall back to console
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            logger.warning(f"Failed to setup file logging to {log_file}: {e}")
    else:
        # No file specified, use console only
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger


class RsyslogFormatter(logging.Formatter):
    """
    Custom formatter that mimics rsyslog format:
    Jan  1 12:34:56 hostname Rsyslog-Logger[1234]: info: User admin logged in
    """

    def __init__(self):
        super().__init__()
        self.hostname = self._get_hostname()
        self.pid = os.getpid()

    def _get_hostname(self):
        """Get hostname, fallback to localhost"""
        try:
            import socket

            return socket.gethostname().split(".")[0]  # Short hostname
        except:
            return "localhost"

    def format(self, record):
        # Convert timestamp to rsyslog format
        dt = datetime.fromtimestamp(record.created)
        timestamp = dt.strftime("%b %d %H:%M:%S")

        # Ensure day is padded correctly (rsyslog uses space padding for single digit days)
        day = dt.strftime("%d")
        if day.startswith("0"):
            day = " " + day[1:]
        timestamp = dt.strftime("%b ") + day + dt.strftime(" %H:%M:%S")

        # Format level name to lowercase
        level = record.levelname.lower()

        # Get program name from logger name
        program = record.name

        # Build rsyslog-style message
        # Format: timestamp hostname program[pid]: level: message
        message = f"{timestamp} {self.hostname} {program}[{self.pid}]: {level}: {record.getMessage()}"

        # Add exception info if present
        if record.exc_info:
            message += "\n" + self.formatException(record.exc_info)

        return message


def get_logger(name=None):
    """
    Get or create a logger instance with automatic configuration.

    Args:
        name: Logger name (defaults to calling module name or "Rsyslog-Logger")

    Returns:
        Logger: Configured logger instance

    Example:
        >>> logger = get_logger("myapp")
        >>> logger = get_logger()  # Uses auto-detected module name
    """
    if name is None:
        # Get caller's module name
        frame = sys._getframe(1)
        name = frame.f_globals.get("__name__", "Rsyslog-Logger")
        if name == "__main__":
            name = "Rsyslog-Logger"

    # Check if logger already exists and is configured
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger = setup_logger(name)

    return logger


# Convenience functions for quick logging
def debug(msg, logger_name=None):
    get_logger(logger_name).debug(msg)


def info(msg, logger_name=None):
    get_logger(logger_name).info(msg)


def warning(msg, logger_name=None):
    get_logger(logger_name).warning(msg)


def error(msg, logger_name=None):
    get_logger(logger_name).error(msg)


def critical(msg, logger_name=None):
    get_logger(logger_name).critical(msg)

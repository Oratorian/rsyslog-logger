#!/usr/bin/env python3
"""!
********************************************************************************
@file   __init__.py
@author Mahesvara ( https://github.com/Oratorian )
@copyright Mahesvara ( https://github.com/Oratorian )
********************************************************************************
"""

from .logger import (
    get_logger,
    setup_logger,
    info,
    debug,
    warning,
    error,
    critical,
    SizeRotatingFileHandler,
    RsyslogFormatter,
    cleanup_old_log_files,
    rotate_log_file,
)

__all__ = [
    "get_logger",
    "setup_logger",
    "info",
    "debug",
    "warning",
    "error",
    "critical",
    "SizeRotatingFileHandler",
    "RsyslogFormatter",
    "cleanup_old_log_files",
    "rotate_log_file",
]

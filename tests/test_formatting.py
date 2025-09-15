"""
Tests for rsyslog formatting functionality.
"""

import os
import tempfile
import shutil
import logging
import re
import sys
from datetime import datetime
from io import StringIO

# Add parent directory to path to import logger
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from rsyslog_logger import setup_logger, RsyslogFormatter, get_logger


class TestRsyslogFormatting:

    def setup_method(self):
        """Setup test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.test_log_file = os.path.join(self.test_dir, "test_format.log")

    def teardown_method(self):
        """Clean up test environment."""
        import gc
        import time

        # Close all logging handlers before cleanup
        for name in list(logging.Logger.manager.loggerDict.keys()):
            if name.startswith("test_"):
                logger = logging.getLogger(name)
                for handler in logger.handlers[:]:
                    if hasattr(handler, "close"):
                        handler.close()
                    logger.removeHandler(handler)

        # Force garbage collection
        gc.collect()
        time.sleep(0.1)  # Give Windows time to release handles

        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except PermissionError:
                # Retry after longer delay
                time.sleep(0.5)
                shutil.rmtree(self.test_dir)

    def test_rsyslog_formatter_initialization(self):
        """Test RsyslogFormatter initializes correctly."""
        formatter = RsyslogFormatter()

        assert hasattr(formatter, "hostname")
        assert hasattr(formatter, "pid")
        assert isinstance(formatter.pid, int)
        assert len(formatter.hostname) > 0

    def test_rsyslog_format_structure(self):
        """Test that rsyslog format matches expected structure."""
        formatter = RsyslogFormatter()

        # Create a test log record
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Expected format: "Sep 11 20:16:15 andrew-pc test_logger[25900]: info: Test message"
        # Use regex to validate structure (hostname can contain hyphens)
        pattern = r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+([\w\-]+)\s+(\w+)\[(\d+)\]:\s+(\w+):\s+(.+)$"
        match = re.match(pattern, formatted)

        assert match is not None, f"Format doesn't match expected pattern: {formatted}"

        timestamp, hostname, logger_name, pid, level, message = match.groups()
        assert logger_name == "test_logger"
        assert level == "info"
        assert message == "Test message"
        assert pid.isdigit()

        # Verify timestamp format (month abbreviation + day + time)
        assert re.match(r"^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}$", timestamp)

    def test_different_log_levels_formatting(self):
        """Test formatting with different log levels."""
        formatter = RsyslogFormatter()

        levels = [
            (logging.DEBUG, "debug"),
            (logging.INFO, "info"),
            (logging.WARNING, "warning"),
            (logging.ERROR, "error"),
            (logging.CRITICAL, "critical"),
        ]

        for log_level, expected_level_name in levels:
            record = logging.LogRecord(
                name="test_logger",
                level=log_level,
                pathname="test.py",
                lineno=1,
                msg="Test message",
                args=(),
                exc_info=None,
            )

            formatted = formatter.format(record)
            assert f": {expected_level_name}: " in formatted

    def test_timestamp_format(self):
        """Test that timestamp follows rsyslog format."""
        formatter = RsyslogFormatter()

        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        formatted = formatter.format(record)

        # Extract timestamp (first part before hostname)
        timestamp_match = re.match(r"^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})", formatted)
        assert timestamp_match is not None

        timestamp = timestamp_match.group(1)

        # Should be in format "Jan  1 12:34:56" or "Jan 12 12:34:56"
        assert re.match(r"^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}$", timestamp)

    def test_setup_logger_uses_rsyslog_format(self):
        """Test that setup_logger with rsyslog format produces correct output."""
        logger = setup_logger(
            name="test_rsyslog", log_file=self.test_log_file, log_format="rsyslog"
        )

        test_message = "Testing rsyslog format"
        logger.info(test_message)

        # Read the log file
        with open(self.test_log_file, "r") as f:
            log_content = f.read().strip()

        # Should contain the test message and follow rsyslog format
        assert test_message in log_content
        assert "test_rsyslog" in log_content
        assert ": info: " in log_content

        # Should match rsyslog pattern (hostname can contain hyphens)
        pattern = r"^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}\s+[\w\-]+\s+test_rsyslog\[\d+\]:\s+info:\s+Testing rsyslog format$"
        assert re.match(pattern, log_content)

    def test_simple_format_option(self):
        """Test that simple format option works correctly."""
        logger = setup_logger(
            name="test_simple", log_file=self.test_log_file, log_format="simple"
        )

        test_message = "Testing simple format"
        logger.info(test_message)

        # Read the log file
        with open(self.test_log_file, "r") as f:
            log_content = f.read().strip()

        # Simple format: "2025-01-01 12:34:56 - INFO - Testing simple format"
        assert test_message in log_content
        assert " - INFO - " in log_content

        # Should match simple pattern (YYYY-MM-DD HH:MM:SS - LEVEL - message)
        pattern = r"^\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+-\s+INFO\s+-\s+Testing simple format$"
        assert re.match(pattern, log_content)

    def test_console_logging_format(self):
        """Test console logging uses correct format."""
        # Capture stdout for console logging test
        import sys
        from io import StringIO

        old_stdout = sys.stdout
        captured_output = StringIO()
        sys.stdout = captured_output

        try:
            logger = setup_logger(
                name="test_console", log_file=None, log_format="rsyslog"  # Console only
            )

            logger.info("Console test message")

            # Get captured output
            output = captured_output.getvalue().strip()

            # Should contain rsyslog format
            assert "Console test message" in output
            assert "test_console" in output
            assert ": info: " in output

        finally:
            sys.stdout = old_stdout

    def test_exception_formatting(self):
        """Test that exceptions are properly formatted in logs."""
        logger = setup_logger(
            name="test_exception", log_file=self.test_log_file, log_format="rsyslog"
        )

        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("An error occurred")

        # Read the log file
        with open(self.test_log_file, "r") as f:
            log_content = f.read()

        # Should contain the exception message and traceback
        assert "An error occurred" in log_content
        assert "ValueError: Test exception" in log_content
        assert "Traceback" in log_content

    def test_get_logger_function(self):
        """Test the convenience get_logger function."""
        logger = get_logger("test_get_logger")

        # Should return a logger instance
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_get_logger"

        # Should have handlers configured
        assert len(logger.handlers) > 0

    def test_auto_detected_module_name(self):
        """Test that get_logger auto-detects module name."""
        logger = get_logger()  # No name provided

        # Should have some name (either auto-detected or default)
        assert logger.name is not None
        assert len(logger.name) > 0

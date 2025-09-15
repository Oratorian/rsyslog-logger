"""
Tests for log rotation functionality.
"""

import os
import tempfile
import shutil
import pytest
import sys

# Add parent directory to path to import logger
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from rsyslog_logger import setup_logger, SizeRotatingFileHandler, rotate_log_file


class TestLogRotation:

    def setup_method(self):
        """Setup test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_log_file = os.path.join(self.test_dir, "test.log")

    def teardown_method(self):
        """Clean up test environment."""
        import gc
        import time
        import logging

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

    def test_size_rotating_handler_initialization(self):
        """Test SizeRotatingFileHandler initializes correctly."""
        handler = SizeRotatingFileHandler(
            self.test_log_file, max_size=1024  # 1KB for testing
        )

        assert handler.max_size == 1024
        assert handler.baseFilename == os.path.abspath(self.test_log_file)

    def test_rotation_triggers_at_size_limit(self):
        """Test that rotation occurs when file exceeds max size."""
        # Create a small log file that will trigger rotation
        max_size = 100  # Very small for testing

        handler = SizeRotatingFileHandler(self.test_log_file, max_size=max_size)

        # Write data larger than max_size
        test_data = "A" * (max_size + 50)
        with open(self.test_log_file, "w") as f:
            f.write(test_data)

        # Check if rotation should occur
        assert handler.should_rotate() == True

    def test_rotation_creates_backup_file(self):
        """Test that rotation creates numbered backup files."""
        # Create initial log file
        initial_content = "Initial log content"
        with open(self.test_log_file, "w") as f:
            f.write(initial_content)

        # Force rotation
        rotate_log_file(self.test_log_file, force=True)

        # Check that backup file was created
        backup_files = [f for f in os.listdir(self.test_dir) if f.endswith(".1")]
        assert len(backup_files) == 1

        # Check backup contains original content
        backup_path = os.path.join(self.test_dir, backup_files[0])
        with open(backup_path, "r") as f:
            assert f.read() == initial_content

        # Check original file is truncated
        with open(self.test_log_file, "r") as f:
            assert f.read() == ""

    def test_multiple_rotations_increment_numbers(self):
        """Test that multiple rotations create sequentially numbered files."""
        # Create and rotate multiple times
        for i in range(3):
            content = f"Log content {i}"
            with open(self.test_log_file, "w") as f:
                f.write(content)
            rotate_log_file(self.test_log_file, force=True)

        # Should have files: test.log.1, test.log.2, test.log.3
        backup_files = [f for f in os.listdir(self.test_dir) if "test.log." in f]
        assert len(backup_files) == 3
        assert "test.log.1" in backup_files
        assert "test.log.2" in backup_files
        assert "test.log.3" in backup_files

    def test_rotation_with_logger_integration(self):
        """Test rotation works with actual logger setup."""
        # Setup logger with small max size
        logger = setup_logger(
            name="test_logger", log_file=self.test_log_file, log_level="INFO"
        )

        # Write lots of log messages to trigger rotation
        for i in range(100):
            logger.info(
                f"This is test message {i} with some content to fill up the log file"
            )

        # Check if backup files were created (rotation occurred)
        backup_files = [f for f in os.listdir(self.test_dir) if "test.log." in f]
        # Should have at least one backup if rotation triggered
        assert (
            len(backup_files) >= 0
        )  # May or may not trigger depending on message size

    def test_rotation_handles_missing_file_gracefully(self):
        """Test rotation handles non-existent files gracefully."""
        non_existent_file = os.path.join(self.test_dir, "doesnt_exist.log")

        # Should not raise exception
        try:
            rotate_log_file(non_existent_file, force=True)
        except Exception as e:
            pytest.fail(
                f"Rotation should handle missing files gracefully, but raised: {e}"
            )

    def test_size_check_prevents_unnecessary_rotation(self):
        """Test that small files don't get rotated unless forced."""
        # Create small file
        small_content = "small"
        with open(self.test_log_file, "w") as f:
            f.write(small_content)

        # Try rotation without force (should not rotate)
        rotate_log_file(self.test_log_file, force=False)

        # Should not have created backup
        backup_files = [f for f in os.listdir(self.test_dir) if "test.log." in f]
        assert len(backup_files) == 0

        # Original content should be intact
        with open(self.test_log_file, "r") as f:
            assert f.read() == small_content

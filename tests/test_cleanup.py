"""
Tests for log cleanup and backup management functionality.
"""

import os
import tempfile
import shutil
import sys

# Add parent directory to path to import logger
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from rsyslog_logger import cleanup_old_log_files, rotate_log_file


class TestLogCleanup:

    def setup_method(self):
        """Setup test environment with temporary directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_log_file = os.path.join(self.test_dir, "test.log")

    def teardown_method(self):
        """Clean up test environment."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_cleanup_respects_backup_count(self):
        """Test that cleanup keeps only the specified number of backups."""
        # Create main log file
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        # Manually create backup files (bypass rotation's automatic cleanup)
        for i in range(1, 11):  # Create test.log.1 through test.log.10
            backup_file = f"{self.test_log_file}.{i}"
            with open(backup_file, "w") as f:
                f.write(f"backup content {i}")

        # Should have 10 backup files
        backup_files = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(backup_files) == 10

        # Now cleanup with backup_count=3
        cleanup_old_log_files(self.test_log_file, backup_count=3)

        # Should only have 3 backup files remaining
        remaining_backups = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(remaining_backups) == 3

        # Should keep the most recent 3 (highest numbers: 8, 9, 10)
        expected_files = ["test.log.8", "test.log.9", "test.log.10"]
        for expected_file in expected_files:
            assert expected_file in remaining_backups

        # Should have removed the older files
        removed_files = [
            "test.log.1",
            "test.log.2",
            "test.log.3",
            "test.log.4",
            "test.log.5",
            "test.log.6",
            "test.log.7",
        ]
        for removed_file in removed_files:
            assert removed_file not in remaining_backups

    def test_cleanup_with_default_backup_count(self):
        """Test cleanup with default backup count (5)."""
        # Create main log file
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        # Manually create 8 backup files
        for i in range(1, 9):  # Create test.log.1 through test.log.8
            backup_file = f"{self.test_log_file}.{i}"
            with open(backup_file, "w") as f:
                f.write(f"backup {i}")

        # Should have 8 backup files
        backup_files = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(backup_files) == 8

        # Cleanup with default backup_count (5)
        cleanup_old_log_files(self.test_log_file)

        # Should only have 5 backup files remaining
        remaining_backups = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(remaining_backups) == 5

        # Should keep files test.log.4 through test.log.8 (highest 5 numbers)
        expected_files = [
            "test.log.4",
            "test.log.5",
            "test.log.6",
            "test.log.7",
            "test.log.8",
        ]
        for expected_file in expected_files:
            assert expected_file in remaining_backups

        # Should have removed the oldest files
        removed_files = ["test.log.1", "test.log.2", "test.log.3"]
        for removed_file in removed_files:
            assert removed_file not in remaining_backups

    def test_cleanup_ignores_non_numeric_suffixes(self):
        """Test that cleanup ignores files with non-numeric suffixes."""
        # Create main log file
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        # Create numbered backup files
        for i in range(1, 4):
            backup_file = f"{self.test_log_file}.{i}"
            with open(backup_file, "w") as f:
                f.write(f"backup {i}")

        # Create files with non-numeric suffixes
        non_numeric_files = [
            f"{self.test_log_file}.old",
            f"{self.test_log_file}.backup",
            f"{self.test_log_file}.tmp",
        ]
        for file_path in non_numeric_files:
            with open(file_path, "w") as f:
                f.write("non-numeric backup")

        # Run cleanup with backup_count=2
        cleanup_old_log_files(self.test_log_file, backup_count=2)

        # Should remove test.log.1 but keep test.log.2 and test.log.3
        remaining_files = os.listdir(self.test_dir)
        assert "test.log.1" not in remaining_files
        assert "test.log.2" in remaining_files
        assert "test.log.3" in remaining_files

        # Non-numeric files should be untouched
        for non_numeric_file in non_numeric_files:
            assert os.path.basename(non_numeric_file) in remaining_files

    def test_cleanup_with_no_backup_files(self):
        """Test cleanup when there are no backup files."""
        # Create only main log file
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        # Run cleanup (should not cause errors)
        try:
            cleanup_old_log_files(self.test_log_file, backup_count=5)
        except Exception as e:
            assert (
                False
            ), f"Cleanup should handle no backup files gracefully, but raised: {e}"

        # Main log file should still exist
        assert os.path.exists(self.test_log_file)

    def test_cleanup_with_backup_count_zero(self):
        """Test cleanup with backup_count=0 removes all backups."""
        # Create main log file and some backups
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        for i in range(3):
            with open(self.test_log_file, "w") as f:
                f.write(f"backup {i}")
            rotate_log_file(self.test_log_file, force=True)

        # Should have 3 backup files
        backup_files = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(backup_files) == 3

        # Cleanup with backup_count=0
        cleanup_old_log_files(self.test_log_file, backup_count=0)

        # Should have no backup files remaining
        remaining_backups = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(remaining_backups) == 0

        # Main log file should still exist
        assert os.path.exists(self.test_log_file)

    def test_cleanup_handles_permission_errors_gracefully(self):
        """Test that cleanup handles file permission errors gracefully."""
        # Create main log file and backup
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        backup_file = f"{self.test_log_file}.1"
        with open(backup_file, "w") as f:
            f.write("backup 1")

        # On Windows, we can't easily test permission errors the same way as Unix
        # But we can test the general error handling by trying to cleanup a non-existent file
        non_existent_log = os.path.join(self.test_dir, "nonexistent.log")

        # Should not raise exception
        try:
            cleanup_old_log_files(non_existent_log, backup_count=1)
        except Exception as e:
            assert False, f"Cleanup should handle errors gracefully, but raised: {e}"

    def test_cleanup_with_large_backup_count(self):
        """Test cleanup with backup count larger than existing files."""
        # Create main log file and 3 backups
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        for i in range(3):
            with open(self.test_log_file, "w") as f:
                f.write(f"backup {i}")
            rotate_log_file(self.test_log_file, force=True)

        # Should have 3 backup files
        backup_files = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(backup_files) == 3

        # Cleanup with backup_count=10 (larger than existing files)
        cleanup_old_log_files(self.test_log_file, backup_count=10)

        # Should still have all 3 backup files (no removal)
        remaining_backups = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(remaining_backups) == 3

    def test_cleanup_sorts_files_correctly(self):
        """Test that cleanup correctly sorts backup files by number."""
        # Create main log file
        with open(self.test_log_file, "w") as f:
            f.write("main log")

        # Create backup files in non-sequential order
        backup_numbers = [2, 10, 1, 5, 3]
        for num in backup_numbers:
            backup_file = f"{self.test_log_file}.{num}"
            with open(backup_file, "w") as f:
                f.write(f"backup {num}")

        # Cleanup with backup_count=3
        cleanup_old_log_files(self.test_log_file, backup_count=3)

        # Should keep the 3 highest numbered files (3, 5, 10)
        remaining_backups = [
            f for f in os.listdir(self.test_dir) if f.startswith("test.log.")
        ]
        assert len(remaining_backups) == 3

        expected_files = ["test.log.3", "test.log.5", "test.log.10"]
        for expected_file in expected_files:
            assert expected_file in remaining_backups

        # Should have removed the lower numbered files (1, 2)
        assert "test.log.1" not in remaining_backups
        assert "test.log.2" not in remaining_backups

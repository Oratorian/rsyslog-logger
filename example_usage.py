#!/usr/bin/env python3
"""
Example usage demonstrating the improved rsyslog-logger API
"""

from rsyslog_logger import setup_logger, SizeRotatingFileHandler

# Example 1: Simple setup with improved API
print("Example 1: Simple logger with 5MB rotation")
logger1 = setup_logger(
    name="example1",
    log_file="example1.log",
    max_size=5,  # Just 5, not 5 * 1024 * 1024!
    backup_count=3
)
logger1.info("This is so much cleaner!")

# Example 2: Direct handler usage
print("\nExample 2: Direct handler with 10MB limit")
handler = SizeRotatingFileHandler(
    "example2.log",
    max_size=10  # Just 10, not 10 * 1024 * 1024!
)
print(f"Handler max_size: {handler.max_size} bytes ({handler.max_size / (1024*1024)} MB)")

# Example 3: Custom production setup
print("\nExample 3: Production setup with custom limits")
logger3 = setup_logger(
    name="production-app",
    log_file="production.log",
    log_level="INFO",
    max_size=20,      # 20MB - clean and simple!
    backup_count=10   # Keep 10 backups
)
logger3.info("Production logger ready")

print("\n✓ All examples completed successfully!")
print("✓ No more calculating 10 * 1024 * 1024 - just use 10!")

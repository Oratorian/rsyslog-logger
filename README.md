# Rsyslog Logger

[![PyPI version](https://badge.fury.io/py/rsyslog-logger.svg)](https://badge.fury.io/py/rsyslog-logger)
[![Python Support](https://img.shields.io/pypi/pyversions/rsyslog-logger.svg)](https://pypi.org/project/rsyslog-logger/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready Python logging library with professional rsyslog-style formatting, reliable log rotation, and cross-platform compatibility. Designed for system administrators and developers who need robust, operational logging.

## 🚀 Features

- **📝 Rsyslog-style formatting**: Industry-standard syslog format (`Jan 1 12:34:56 hostname program[pid]: level: message`)
- **🔄 Reliable log rotation**: Copy-and-truncate method works even with open file handles (Windows-friendly)
- **⚡ Zero dependencies**: No external requirements, uses only Python standard library
- **🌍 Cross-platform**: Works seamlessly on Windows, Linux, and macOS
- **🔧 Production-ready**: Robust error handling and file operation safety
- **📊 Configurable**: Flexible sizing, backup counts, and formatting options
- **🧪 Fully tested**: Comprehensive test suite with 25+ tests

## 📦 Installation

```bash
pip install rsyslog-logger
```

## 🎯 Quick Start

```python
from rsyslog_logger import setup_logger

# Simple setup with default rsyslog formatting
logger = setup_logger("myapp")
logger.info("Application started")
# Output: Sep 11 20:15:30 hostname myapp[1234]: info: Application started

# Custom log file and level
logger = setup_logger(
    name="myapp",
    log_file="/var/log/myapp.log",
    log_level="DEBUG"
)
logger.debug("Debug information")
logger.error("Something went wrong!")
```

## 📖 Usage Examples

### Basic Logging

```python
from rsyslog_logger import setup_logger

logger = setup_logger("webapp")

logger.info("User login successful")
logger.warning("High memory usage detected")
logger.error("Database connection failed")
logger.critical("System shutdown initiated")
```

### Custom Configuration

```python
from rsyslog_logger import setup_logger

# Production configuration with custom settings
logger = setup_logger(
    name="production-app",
    log_file="/var/log/production.log",
    log_level="INFO",
    log_format="rsyslog",           # or "simple"
    console_log_level="ERROR"       # Only errors to console
)

# The logger automatically handles:
# - Log rotation when files get too large (10MB default)
# - Keeps 5 backup files by default
# - Proper file handle management
# - Cross-platform path handling
```

### Using Different Formatters

```python
# Rsyslog format (default)
logger = setup_logger("app", log_format="rsyslog")
logger.info("Hello world")
# Sep 11 20:15:30 hostname app[1234]: info: Hello world

# Simple format
logger = setup_logger("app", log_format="simple")
logger.info("Hello world")
# 2025-09-11 20:15:30 - INFO - Hello world
```

### Advanced Usage with Manual Rotation

```python
from rsyslog_logger import setup_logger, rotate_log_file, cleanup_old_log_files

logger = setup_logger("advanced-app", "/var/log/app.log")

# Manual log rotation (automatic rotation happens by size)
rotate_log_file("/var/log/app.log", force=True)

# Custom cleanup (keep only 3 backup files)
cleanup_old_log_files("/var/log/app.log", backup_count=3)
```

### Exception Logging

```python
logger = setup_logger("error-handler")

try:
    result = 10 / 0
except ZeroDivisionError:
    logger.exception("Division error occurred")
    # Automatically includes full traceback
```

## ⚙️ Configuration Options

### setup_logger() Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | str | `"Rsyslog-Logger"` | Logger name (appears in log messages) |
| `log_file` | str | `"Rsyslog-Logger.log"` | Log file path (`None` for console only) |
| `log_level` | str | `"INFO"` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) |
| `log_format` | str | `"rsyslog"` | Format style (`"rsyslog"` or `"simple"`) |
| `console_log_level` | str | `"INFO"` | Separate log level for console output |

### Log Rotation Settings

The logger automatically rotates files when they exceed **10MB** by default. You can customize this:

```python
from rsyslog_logger import SizeRotatingFileHandler

# Custom rotation size (5MB)
handler = SizeRotatingFileHandler(
    "/var/log/app.log",
    max_size=5 * 1024 * 1024  # 5MB
)
```

### Cleanup Settings

```python
from rsyslog_logger import cleanup_old_log_files

# Keep only 10 backup files
cleanup_old_log_files("/var/log/app.log", backup_count=10)

# Remove all backups
cleanup_old_log_files("/var/log/app.log", backup_count=0)
```

## 🏗️ Architecture

The library consists of several key components:

- **`setup_logger()`**: Main entry point for logger configuration
- **`SizeRotatingFileHandler`**: Custom file handler with size-based rotation
- **`RsyslogFormatter`**: Professional syslog-style message formatting
- **`rotate_log_file()`**: Manual log rotation using copy-and-truncate
- **`cleanup_old_log_files()`**: Backup file management with configurable retention

### Why Copy-and-Truncate?

Unlike traditional rotation methods that move files, this library uses **copy-and-truncate** rotation:

✅ **Works with open file handles** (no application restart needed)  
✅ **Windows compatible** (no file locking issues)  
✅ **Safe for production** (no log loss during rotation)  
✅ **Process-agnostic** (works regardless of file handle state)

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=rsyslog_logger --cov-report=html
```

The test suite includes:
- **Rotation testing**: Size limits, backup creation, sequential numbering
- **Format validation**: Rsyslog format compliance, timestamp accuracy
- **Cleanup testing**: Backup count limits, file sorting, error handling
- **Cross-platform testing**: Windows and Linux compatibility
- **Error resilience**: Permission errors, missing files, edge cases

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Oratorian/rsyslog-logger.git
cd rsyslog-logger

# Install development dependencies
pip install -e .
pip install pytest pytest-cov pytest-mock

# Run tests
pytest
```

### Code Quality

- Follow PEP 8 style guidelines
- Add tests for new functionality
- Update documentation for API changes
- Ensure cross-platform compatibility

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/rsyslog-logger/
- **Source Code**: https://github.com/Oratorian/rsyslog-logger
- **Issue Tracker**: https://github.com/Oratorian/rsyslog-logger/issues
- **Documentation**: https://github.com/Oratorian/rsyslog-logger/blob/main/README.md

## 🎉 Why Choose Rsyslog Logger?

**For System Administrators:**
- Professional syslog format integrates with existing log management
- Reliable rotation prevents disk space issues
- Cross-platform compatibility for mixed environments
- Zero-dependency deployment simplifies installation

**For Developers:**
- Production-ready out of the box
- Comprehensive error handling
- Clean, documented API
- Extensive test coverage ensures reliability

**For DevOps Teams:**
- Operational logging best practices built-in
- Configurable retention policies
- Performance optimized for high-throughput scenarios
- Container and cloud-friendly

---

*Built with ❤️ by [Mahesvara](https://github.com/Oratorian) for the Python community*
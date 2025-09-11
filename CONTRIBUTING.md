# Contributing to Rsyslog Logger

Thank you for your interest in contributing to rsyslog-logger! We welcome contributions from the community.

## 🚀 Getting Started

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/rsyslog-logger.git
   cd rsyslog-logger
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e .
   pip install pytest pytest-cov pytest-mock
   ```

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rsyslog_logger --cov-report=html

# Run specific test file
pytest tests/test_rotation.py

# Run with verbose output
pytest -v
```

## 📝 Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Use meaningful variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and modular

## 🐛 Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template when creating new issues
3. Include:
   - Python version
   - Operating system
   - rsyslog-logger version
   - Minimal code example to reproduce
   - Full error traceback

## ✨ Suggesting Features

1. Check existing issues and discussions first
2. Use the feature request template
3. Explain the use case and why it would be valuable
4. Consider backward compatibility

## 🔧 Pull Requests

### Before You Start

1. **Create an issue** to discuss major changes first
2. **Check existing PRs** to avoid duplicate work
3. **Fork the repository** and create a feature branch

### PR Guidelines

1. **Branch naming**: Use descriptive names like `feature/add-json-formatter` or `fix/rotation-bug`

2. **Commit messages**: Use clear, descriptive commit messages
   ```
   Add JSON formatter option
   
   - Implements new JSONFormatter class
   - Updates setup_logger to accept json format
   - Adds comprehensive tests for JSON output
   ```

3. **Code changes**:
   - Add tests for new functionality
   - Update documentation if needed
   - Ensure all tests pass
   - Maintain backward compatibility

4. **Testing requirements**:
   - All new code must have tests
   - Tests should cover both success and failure cases
   - Cross-platform compatibility should be considered

### PR Process

1. **Create your branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**
   ```bash
   pytest
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Descriptive commit message"
   git push origin feature/your-feature-name
   ```

5. **Create the pull request**
   - Use the PR template
   - Link to related issues
   - Describe what you changed and why

## 📚 Documentation

- Update the README for user-facing changes
- Add docstrings for new functions and classes
- Include code examples in docstrings
- Update type hints where applicable

## 🎯 Areas We Welcome Contributions

### High Priority
- **Cross-platform testing**: More Windows-specific test coverage
- **Performance improvements**: Benchmarking and optimization
- **Error handling**: Edge cases and resilience improvements

### Medium Priority  
- **New formatters**: JSON, structured logging formats
- **Configuration options**: More flexibility in log rotation
- **Integration examples**: Flask, Django, FastAPI examples

### Documentation
- **Usage examples**: Real-world scenarios
- **Performance guides**: Best practices for high-volume logging
- **Troubleshooting**: Common issues and solutions

## ❓ Questions?

- Create a [Support Issue](https://github.com/Oratorian/rsyslog-logger/issues/new?template=support.yml)
- Start a [Discussion](https://github.com/Oratorian/rsyslog-logger/discussions)
- Check the [README](README.md) for usage examples

## 📄 License

By contributing to rsyslog-logger, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

All contributors will be recognized in our README. Thank you for making rsyslog-logger better!

---

*Looking forward to your contributions! 🎉*
# Contributing to Clinical Mental Health Assistant

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on what is best for the community
- Show empathy towards other community members

## 🐛 Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment details** (OS, Python version, GPU type)
- **Relevant logs or screenshots**

## 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description**
- **Use case** - why this enhancement would be useful
- **Possible implementation** (if you have ideas)
- **Alternative solutions** you've considered

## 🔧 Development Setup

1. **Fork the repository**

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/clinical_assistant.git
   cd clinical_assistant
   ```

3. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r backend/requirements.txt
   pip install -r backend/requirements-dev.txt
   ```

5. **Create .env file**
   ```bash
   cp .env.example .env
   # Edit .env with your HuggingFace token
   ```

6. **Run tests**
   ```bash
   pytest
   ```

## 📝 Pull Request Process

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bugfix-name
   ```

2. **Make your changes** following the coding standards below

3. **Add tests** for new features or bugfixes

4. **Run the test suite**:
   ```bash
   pytest
   flake8 backend/
   black backend/ --check
   mypy backend/
   ```

5. **Update documentation** if needed:
   - Update README.md for user-facing changes
   - Update docstrings for code changes
   - Update docs/ for architectural changes

6. **Commit your changes** with descriptive messages:
   ```bash
   git commit -m "feat: add sentiment analysis endpoint"
   # or
   git commit -m "fix: resolve rate limiting edge case"
   ```

   **Commit message conventions:**
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `style:` Code style changes (formatting, etc.)
   - `refactor:` Code refactoring
   - `test:` Adding or updating tests
   - `chore:` Maintenance tasks

7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

8. **Create a Pull Request** on GitHub:
   - Provide a clear description of the changes
   - Reference any related issues
   - Ensure CI checks pass

## 🎨 Coding Standards

### Python

- **PEP 8** compliance (enforced by flake8)
- **Black** for code formatting (line length: 100)
- **Type hints** for all functions
- **Docstrings** for all public functions and classes

Example:
```python
from typing import Dict, Optional

def analyze_case(text: str, confidence_threshold: float = 0.6) -> Dict[str, any]:
    """
    Analyze a clinical case description.
    
    Args:
        text: The clinical case description
        confidence_threshold: Minimum confidence for classification
        
    Returns:
        Dictionary containing classification, summary, and recommendations
        
    Raises:
        ValueError: If text is too short or empty
    """
    if len(text) < 50:
        raise ValueError("Text must be at least 50 characters")
    
    # Implementation...
    return result
```

### JavaScript

- **ES6+** syntax
- **Semicolons** required
- **2 spaces** for indentation
- **JSDoc** comments for functions

### Testing

- **Test coverage** should be >70%
- **Unit tests** for individual functions
- **Integration tests** for API endpoints
- **Descriptive test names**:
  ```python
  def test_rate_limiter_blocks_after_limit():
      """Test that rate limiter blocks requests after exceeding limit"""
      # Test implementation...
  ```

## 📂 Project Structure

When adding new features, follow this structure:

```
backend/app/
├── api/v1/              # API endpoints
├── core/                # Configuration and core utilities
├── middleware/          # Middleware (auth, rate limiting, etc.)
├── ml/                  # ML models and pipelines
└── utils/               # Helper functions

tests/
├── unit/                # Unit tests
└── integration/         # Integration tests

docs/                    # Documentation
```

## 🔍 Code Review Process

- All submissions require review
- Reviewers will check for:
  - Code quality and style
  - Test coverage
  - Documentation
  - Performance implications
  - Security concerns

## 🎯 Priority Areas for Contribution

We especially welcome contributions in these areas:

### High Priority
- [ ] Improve T5 summarizer performance
- [ ] Add crisis detection keywords
- [ ] Implement sentiment analysis
- [ ] Add multilingual support
- [ ] Improve test coverage (current: 70%, target: 85%)

### Medium Priority
- [ ] Add explainability (LIME/SHAP)
- [ ] A/B testing framework
- [ ] User feedback collection
- [ ] Model versioning system
- [ ] Admin dashboard

### Low Priority
- [ ] Additional export formats
- [ ] Custom themes
- [ ] Mobile responsive improvements
- [ ] Voice input support

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🤔 Questions?

- Open an issue for questions
- Join discussions in existing issues
- Reach out to maintainers: [@gortif00](https://github.com/gortif00)

## 🙏 Thank You!

Your contributions make this project better for everyone in the mental health community.

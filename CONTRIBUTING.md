# Contributing to AMOS Documentation Validator

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, education, socio-economic status, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Examples of positive behavior**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Examples of unacceptable behavior**:
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

### Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be reported by opening an issue or contacting the project maintainers. All complaints will be reviewed and investigated promptly and fairly.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of pandas, PyQt6
- Familiarity with aircraft maintenance documentation (helpful but not required)

### Set Up Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/amos-validator.git
   cd amos-validator
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL-OWNER/amos-validator.git
   ```

4. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-gui.txt
   pip install -r requirements-dev.txt
   ```

6. **Verify installation**:
   ```bash
   python -m doc_validator.tests.test_validators
   python run_gui.py
   ```

---

## How to Contribute

### Ways to Contribute

- **Report bugs** - Found a bug? Open an issue
- **Suggest features** - Have an idea? Open a discussion
- **Fix bugs** - Browse open issues and submit a fix
- **Add features** - Implement new functionality
- **Improve documentation** - Fix typos, add examples, clarify
- **Write tests** - Increase test coverage
- **Review pull requests** - Help review others' code

### Good First Issues

Look for issues labeled `good first issue` or `help wanted`:
- Documentation improvements
- Adding test cases
- Fixing typos or small bugs
- Adding new reference keywords
- Improving error messages

---

## Development Workflow

### 1. Choose an Issue

- Browse [open issues](https://github.com/yourusername/amos-validator/issues)
- Comment on the issue to claim it
- Wait for maintainer approval before starting work

### 2. Create a Branch

```bash
# Update your fork
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-feature

# Or for bug fixes
git checkout -b fix/bug-description
```

**Branch naming**:
- `feature/add-new-document-type`
- `fix/date-filter-bug`
- `docs/update-readme`
- `test/add-validation-tests`

### 3. Make Changes

- Write clean, readable code
- Follow [coding standards](#coding-standards)
- Add tests for new functionality
- Update documentation as needed
- Keep commits focused and atomic

### 4. Test Your Changes

```bash
# Run unit tests
python -m doc_validator.tests.test_validators
python -m doc_validator.tests.test_real_world_data

# Test GUI
python run_gui.py

# Test CLI
python -m doc_validator.interface.cli_main

# Test with real data
python -m doc_validator.tools.process_local_batch ./INPUT
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat: add support for new document type"
```

Follow [commit message guidelines](#commit-messages).

### 6. Push and Create Pull Request

```bash
git push origin feature/my-feature
```

Then create a Pull Request on GitHub.

---

## Coding Standards

### Python Style Guide

Follow **PEP 8** with these specifics:

- **Line length**: 88 characters (Black formatter default)
- **Indentation**: 4 spaces (no tabs)
- **Quotes**: Double quotes for strings
- **Naming**:
  - Functions/variables: `snake_case`
  - Classes: `PascalCase`
  - Constants: `UPPER_CASE`

### Code Formatting

Use **Black** formatter:

```bash
# Format all files
black doc_validator/

# Check without modifying
black --check doc_validator/
```

### Linting

Use **Flake8**:

```bash
# Run linter
flake8 doc_validator/

# Configuration (.flake8)
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = __pycache__, venv, build, dist
```

### Type Hints

Use type hints for function signatures:

```python
from typing import Optional, List, Dict
from datetime import date

def process_excel(
    file_path: str,
    filter_start_date: Optional[date] = None,
    filter_end_date: Optional[date] = None
) -> Optional[str]:
    """Process Excel file with validation."""
    pass
```

### Docstrings

Use **Google-style docstrings**:

```python
def my_function(arg1: str, arg2: int = 10) -> bool:
    """
    One-line summary of the function.
    
    More detailed explanation of what the function does,
    including any important notes or edge cases.
    
    Args:
        arg1: Description of first argument
        arg2: Description of second argument with default value
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When arg1 is empty
        TypeError: When arg2 is not an integer
        
    Example:
        >>> my_function("test", 42)
        True
    """
    if not arg1:
        raise ValueError("arg1 cannot be empty")
    return True
```

### Code Organization

```python
# 1. Standard library imports
import os
from pathlib import Path
from typing import Optional

# 2. Third-party imports
import pandas as pd
from PyQt6.QtWidgets import QWidget

# 3. Local imports
from doc_validator.config import DATA_FOLDER
from doc_validator.validation.engine import check_ref_keywords

# 4. Constants
DEFAULT_TIMEOUT = 30

# 5. Classes
class MyClass:
    """Class docstring."""
    pass

# 6. Functions
def my_function():
    """Function docstring."""
    pass

# 7. Main execution
if __name__ == "__main__":
    main()
```

---

## Testing

### Writing Tests

Add tests for all new functionality:

```python
# doc_validator/tests/test_my_feature.py
from doc_validator.validation.engine import check_ref_keywords

class TestResults:
    # ... (use existing test infrastructure)

results = TestResults()

def test_my_new_feature():
    """Test new validation pattern."""
    print("\n=== Testing My Feature ===")
    
    results.assert_equal(
        check_ref_keywords("MY TEST INPUT"),
        "Expected Result",
        "Test case description"
    )
    
    results.assert_equal(
        check_ref_keywords("ANOTHER TEST"),
        "Valid",
        "Another test case"
    )

if __name__ == "__main__":
    test_my_new_feature()
    success = results.print_summary()
    exit(0 if success else 1)
```

### Running Tests

```bash
# Run all tests
python -m doc_validator.tests.test_validators
python -m doc_validator.tests.test_real_world_data

# Run specific test
python -m doc_validator.tests.test_my_feature

# Run with pytest (if installed)
pytest doc_validator/tests/

# Run with coverage
pytest --cov=doc_validator doc_validator/tests/
```

### Test Coverage

Aim for:
- **90%+ coverage** for core validation logic
- **80%+ coverage** for utilities
- **70%+ coverage** overall

### Manual Testing Checklist

Before submitting PR:
- [ ] GUI launches without errors
- [ ] Can process local files
- [ ] Can process Drive files (if credentials configured)
- [ ] Date filter works correctly
- [ ] Output files are correct
- [ ] Console output is clear
- [ ] No crashes or freezes

---

## Documentation

### Documentation Requirements

When contributing, update relevant documentation:

- **Code comments** - Explain complex logic
- **Docstrings** - All public functions/classes
- **README.md** - If adding major features
- **USER_GUIDE.md** - If changing user-facing functionality
- **DEVELOPER_GUIDE.md** - If changing architecture
- **VALIDATION_RULES.md** - If modifying validation logic
- **API_REFERENCE.md** - If adding/changing APIs
- **CHANGELOG.md** - All changes

### Documentation Style

- Use **Markdown** format
- Be clear and concise
- Include examples
- Use proper headings
- Add links to related docs

### Example Documentation Update

When adding a new reference type:

1. **Update constants.py**:
   ```python
   REF_KEYWORDS = [
       "AMM", "SRM", "CMM",
       "NEW_TYPE",  # NEW: Added support for NEW_TYPE documents
   ]
   ```

2. **Update VALIDATION_RULES.md**:
   ```markdown
   | NEW_TYPE | New Type Manual | IAW NEW_TYPE 123 REV 45 |
   ```

3. **Update CHANGELOG.md**:
   ```markdown
   ### Added
   - Support for NEW_TYPE document references
   ```

4. **Add test cases**:
   ```python
   results.assert_equal(
       check_ref_keywords("IAW NEW_TYPE 123 REV 45"),
       "Valid",
       "NEW_TYPE with revision"
   )
   ```

---

## Submitting Changes

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples**:

```
feat(validation): add support for DDG references

Add DDG (Dispatch Deviation Guide) to the list of valid
reference keywords. Update tests and documentation.

Closes #123
```

```
fix(gui): resolve file selection bug

Fixed issue where "Deselect All" was not working when
search filter was active. The bug was caused by using
filtered list instead of original list.

Fixes #456
```

```
docs: update installation guide for macOS

Add instructions for installing system dependencies
and handling Qt platform plugin issues.
```

### Pull Request Process

1. **Update your branch**:
   ```bash
   git checkout main
   git pull upstream main
   git checkout feature/my-feature
   git rebase main
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/my-feature --force-with-lease
   ```

3. **Create Pull Request** on GitHub

4. **Fill out PR template**:
   - Describe changes
   - Link related issues
   - Add screenshots (for UI changes)
   - List breaking changes (if any)

5. **Wait for review**:
   - Respond to comments
   - Make requested changes
   - Push updates to same branch

6. **After approval**:
   - Maintainer will merge
   - Delete your branch

### Pull Request Template

```markdown
## Description
Brief description of what this PR does

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change (fix or feature that changes existing functionality)
- [ ] Documentation update

## Related Issues
Closes #123
Fixes #456

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] GUI tested
- [ ] CLI tested

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
- [ ] CHANGELOG.md updated
```

### Code Review Guidelines

**For contributors**:
- Be open to feedback
- Ask questions if unclear
- Don't take it personally
- Learn from the process

**For reviewers**:
- Be respectful and constructive
- Explain the "why" behind suggestions
- Acknowledge good work
- Focus on code, not person

---

## Release Process

(For maintainers)

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **MAJOR** (1.0.0): Breaking changes
- **MINOR** (0.1.0): New features (backward compatible)
- **PATCH** (0.0.1): Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Version bumped in:
  - `doc_validator/__init__.py`
  - `interface/main_window.py`
- [ ] Create Git tag
- [ ] Build executable
- [ ] Create GitHub release
- [ ] Update documentation links

---

## Questions?

- **General questions**: [GitHub Discussions](https://github.com/yourusername/amos-validator/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/yourusername/amos-validator/issues)
- **Feature requests**: [GitHub Issues](https://github.com/yourusername/amos-validator/issues)
- **Security issues**: Email maintainer directly

---

## Attribution

Contributors will be recognized in:
- README.md Contributors section
- CHANGELOG.md release notes
- GitHub contributors page

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to AMOS Documentation Validator!** 🎉
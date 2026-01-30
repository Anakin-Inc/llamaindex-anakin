# Contributing to llamaindex-anakin

Thank you for your interest in contributing to llamaindex-anakin! We welcome contributions from the community.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- `uv` package manager
- Git

### Setting Up Development Environment

1. **Fork and Clone**

```bash
git clone https://github.com/your-username/llamaindex-anakin.git
cd llamaindex-anakin
```

2. **Install Dependencies**

```bash
pip install -e ".[dev]"
```

3. **Set Up Environment Variables**

```bash
cp .env.template .env
# Add your ANAKIN_API_KEY to .env
```

## Development Workflow

### Running Tests

```bash
# Run all tests
hatch run test

# Run with coverage
pytest --cov=llamaindex_anakin
```

### Code Quality

We use several tools to maintain code quality:

```bash
# Format code
hatch run format

# Lint code
hatch run lint

# Type check
hatch run typecheck

# Run all checks
hatch run all-check
```

### Running Examples

```bash
cd examples
python basic_scraping.py
python ai_search.py
```

### Testing Workflows Locally

```bash
# Start the workflow server
llamactl serve

# In another terminal, test the endpoints
curl -X POST http://localhost:4501/deployments/llamaindex-anakin/workflows/search/run \
  -H "Content-Type: application/json" \
  -d '{"query": "test query", "max_results": 5}'
```

## Contribution Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all function arguments and return values
- Write descriptive docstrings for all public functions and classes
- Keep functions focused and modular

### Commit Messages

Use clear and descriptive commit messages:

- `feat: Add new feature X`
- `fix: Resolve issue with Y`
- `docs: Update README with Z`
- `refactor: Improve code structure in A`
- `test: Add tests for B`

### Pull Request Process

1. **Create a Branch**

```bash
git checkout -b feature/your-feature-name
```

2. **Make Your Changes**

- Write clear, documented code
- Add tests for new functionality
- Update documentation as needed

3. **Test Your Changes**

```bash
hatch run all-check
```

4. **Commit Your Changes**

```bash
git add .
git commit -m "feat: Add your feature description"
```

5. **Push to Your Fork**

```bash
git push origin feature/your-feature-name
```

6. **Create a Pull Request**

- Go to the original repository on GitHub
- Click "New Pull Request"
- Select your branch
- Fill out the PR template with:
  - Description of changes
  - Related issues
  - Testing performed
  - Screenshots (if applicable)

### PR Review Process

- Maintainers will review your PR within a few days
- Address any feedback or requested changes
- Once approved, your PR will be merged

## Types of Contributions

### Bug Reports

When reporting bugs, please include:

- Description of the bug
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or stack traces

Use the GitHub issue template for bug reports.

### Feature Requests

When requesting features, please include:

- Clear description of the feature
- Use cases and benefits
- Potential implementation approach
- Any related examples or references

### Documentation Improvements

- Fix typos or unclear explanations
- Add more examples
- Improve API documentation
- Create tutorials or guides

### Code Contributions

- New tools or workflows
- Bug fixes
- Performance improvements
- Test coverage improvements
- Refactoring

## Project Structure

```
llamaindex-anakin/
├── src/
│   └── llamaindex_anakin/
│       ├── __init__.py
│       ├── client.py           # API client
│       ├── tools/              # LlamaIndex tools
│       │   ├── scrape_tool.py
│       │   ├── search_tool.py
│       │   └── agentic_search_tool.py
│       └── workflows/          # Deployable workflows
│           ├── scrape_workflow.py
│           ├── search_workflow.py
│           └── agentic_search_workflow.py
├── examples/                   # Usage examples
├── tests/                      # Test suite
├── docs/                       # Documentation
├── pyproject.toml             # Project configuration
└── README.md                  # Main documentation
```

## Adding New Features

### Adding a New Tool

1. Create a new file in `src/llamaindex_anakin/tools/`
2. Implement the tool class with `to_tool()` method
3. Add exports to `tools/__init__.py`
4. Add exports to main `__init__.py`
5. Write tests in `tests/`
6. Add example usage to `examples/`
7. Update README.md

### Adding a New Workflow

1. Create a new file in `src/llamaindex_anakin/workflows/`
2. Implement the workflow class
3. Add exports to `workflows/__init__.py`
4. Register in `pyproject.toml` under `[tool.llamadeploy.workflows]`
5. Write tests
6. Add documentation

## Testing Guidelines

### Writing Tests

- Use pytest for all tests
- Aim for high test coverage (>80%)
- Test both success and error cases
- Use fixtures for common setup
- Mock external API calls

Example test structure:

```python
import pytest
from llamaindex_anakin import AnakinScrapeTool

def test_scrape_tool_initialization():
    """Test that tool initializes correctly."""
    tool = AnakinScrapeTool(api_key="test-key")
    assert tool.client.api_key == "test-key"

@pytest.mark.asyncio
async def test_scrape_workflow():
    """Test scraping workflow execution."""
    # Test implementation
    pass
```

## Documentation Guidelines

- Keep README.md up to date
- Document all public APIs
- Include code examples
- Use clear, concise language
- Add inline comments for complex logic

## Questions?

If you have questions:

- Check existing issues and discussions
- Join our community forum
- Email: anakin@anakininc.com

## Code of Conduct

Please be respectful and professional in all interactions. We're here to build great software together!

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to llamaindex-anakin! 🦙✨

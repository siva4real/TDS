# Contributing to Automated GitHub Pages Deployment API

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We aim to maintain a welcoming and collaborative environment.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs actual behavior
- Your environment (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:

- Check if the enhancement has already been suggested
- Provide a clear use case
- Explain why this enhancement would be useful
- Consider potential drawbacks or challenges

### Pull Requests

1. **Fork the repository**

   ```bash
   git clone https://github.com/yourusername/TDS.git
   cd TDS
   ```

2. **Create a branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**

   - Follow the code style guidelines below
   - Add tests if applicable
   - Update documentation as needed

4. **Test your changes**

   ```bash
   # Run tests
   python test_api.py

   # Check code style
   pip install flake8 black
   black app.py
   flake8 app.py
   ```

5. **Commit your changes**

   ```bash
   git add .
   git commit -m "Add feature: description of your feature"
   ```

6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```
   Then open a Pull Request on GitHub.

## Code Style Guidelines

### Python Code

- Follow PEP 8 style guide
- Use type hints where applicable
- Write docstrings for functions and classes
- Keep functions focused and small
- Use meaningful variable names

Example:

```python
def process_attachments(attachments: List[Attachment]) -> List[Dict[str, Any]]:
    """
    Process data URI attachments and extract content.

    Args:
        attachments: List of attachment objects with name and data URI

    Returns:
        List of processed attachment dictionaries with decoded data
    """
    processed = []
    # Implementation...
    return processed
```

### Formatting

- Use Black for code formatting: `black app.py`
- Line length: 88 characters (Black default)
- Use double quotes for strings
- 4 spaces for indentation

### Documentation

- Update README.md if you change functionality
- Add comments for complex logic
- Keep comments up-to-date with code changes

## Development Setup

1. **Clone and setup**

   ```bash
   git clone <repo-url>
   cd TDS
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Configure environment**

   ```bash
   cp env.template .env
   # Edit .env with your credentials
   ```

3. **Run in development mode**
   ```bash
   uvicorn app:app --reload
   ```

## Testing

### Manual Testing

1. Start the server: `uvicorn app:app --reload`
2. Run test script: `python test_api.py`
3. Test specific endpoints with curl or Postman

### Adding Tests

If you add new functionality, please add corresponding tests to `test_api.py`:

```python
def test_new_feature():
    """Test description."""
    # Setup
    request_data = {...}

    # Execute
    response = requests.post(f"{API_URL}/endpoint", json=request_data)

    # Verify
    assert response.status_code == 200
    assert response.json()["field"] == "expected_value"

    print("✓ Test passed")
```

## Areas for Contribution

### High Priority

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] Caching layer (Redis)
- [ ] Better error handling and recovery
- [ ] Comprehensive unit tests
- [ ] API rate limiting per user
- [ ] Webhook support for deployment status

### Medium Priority

- [ ] Support for more AI models (Claude, Gemini)
- [ ] Template library for common tasks
- [ ] Admin dashboard
- [ ] Deployment analytics
- [ ] Custom domain support
- [ ] Multi-language code generation

### Low Priority

- [ ] GraphQL API
- [ ] WebSocket support for real-time updates
- [ ] CLI tool for API interaction
- [ ] Browser extension
- [ ] Mobile app

## Project Structure

```
TDS/
├── app.py                 # Main application code
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── SETUP.md              # Quick setup guide
├── CONTRIBUTING.md       # This file
├── test_api.py           # Test suite
├── deploy.sh             # Deployment script
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose config
├── nginx.conf            # Nginx configuration
├── deployment-api.service # Systemd service file
└── env.template          # Environment variables template
```

## Key Components

### Request Processing (`handle_round_1`, `handle_round_2`)

- Validates incoming requests
- Manages workflow orchestration
- Handles error cases

### AI Integration (`generate_code_with_ai`)

- Constructs prompts for OpenAI
- Parses generated code
- Provides fallback templates

### GitHub Integration

- `create_github_repo`: Creates repository and commits files
- `update_github_repo`: Updates existing repositories
- `enable_github_pages`: Enables GitHub Pages deployment

### Storage

- Currently in-memory (needs database implementation)
- Stores mapping between tasks and repositories

## Commit Message Guidelines

Use conventional commits format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

Examples:

```
feat: add database integration with PostgreSQL
fix: handle timeout errors in OpenAI API calls
docs: update README with deployment instructions
refactor: extract GitHub operations into separate module
```

## Release Process

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release tag: `git tag -a v1.0.0 -m "Release 1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release with notes

## Questions?

If you have questions:

- Open an issue for discussion
- Check existing issues and PRs
- Review the README and documentation

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing! 🎉

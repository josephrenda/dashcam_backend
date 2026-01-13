# Contributing to Dashcam Backend

Thank you for your interest in contributing to the Dashcam Backend project! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, inclusive, and considerate of others. We're all here to build something great together.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/dashcam_backend.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Submit a pull request

## Development Setup

### Local Development Environment

```bash
# Clone the repository
git clone https://github.com/josephrendacec/dashcam_backend.git
cd dashcam_backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start services with Docker
docker-compose up -d mysql redis

# Run migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, start Celery worker
celery -A app.celery_app worker --loglevel=info
```

## Coding Standards

### Python Style Guide

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Write comprehensive docstrings for all functions and classes
- Keep functions small and focused (single responsibility principle)
- Maximum line length: 100 characters

### Example Function Format

```python
def process_video(video_path: str, options: Dict[str, Any]) -> ProcessingResult:
    """
    Process a video file and extract relevant information.
    
    Args:
        video_path: Path to the video file to process
        options: Dictionary of processing options
        
    Returns:
        ProcessingResult object containing extracted data
        
    Raises:
        FileNotFoundError: If video file doesn't exist
        ValueError: If video format is not supported
    """
    # Implementation here
    pass
```

### Code Organization

- **Models**: Database models go in `app/models/`
- **Schemas**: Pydantic schemas go in `app/schemas/`
- **Endpoints**: API endpoints go in `app/api/v1/endpoints/`
- **Services**: Business logic goes in `app/services/`
- **Tasks**: Background tasks go in `app/tasks/`

## Testing

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run specific test function
pytest tests/test_auth.py::test_register_success
```

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow the Arrange-Act-Assert pattern

Example test:

```python
def test_create_incident_with_valid_data():
    """Test creating an incident with valid data."""
    # Arrange
    token = get_auth_token()
    video_file = create_test_video()
    
    # Act
    response = client.post(
        "/api/v1/incidents/report",
        headers={"Authorization": f"Bearer {token}"},
        files={"video": video_file},
        data={"type": "crash", "latitude": 37.7749, ...}
    )
    
    # Assert
    assert response.status_code == 201
    assert "incident_id" in response.json()
```

## Database Migrations

When adding or modifying database models:

1. Create a new migration:
```bash
alembic revision --autogenerate -m "Description of changes"
```

2. Review the generated migration file

3. Test the migration:
```bash
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

4. Include the migration file in your PR

## Pull Request Process

### Before Submitting

- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] New tests added for new features
- [ ] Documentation updated (if applicable)
- [ ] Commit messages are clear and descriptive
- [ ] No merge conflicts with main branch

### PR Title Format

Use conventional commit format:

- `feat: Add license plate color detection`
- `fix: Resolve video upload timeout issue`
- `docs: Update API documentation`
- `test: Add tests for incident deletion`
- `refactor: Improve video processing performance`
- `chore: Update dependencies`

### PR Description Template

```markdown
## Description
Brief description of the changes

## Motivation
Why is this change needed?

## Changes Made
- Bullet point list of changes
- Another change

## Testing
How was this tested?

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
```

## Feature Requests and Bug Reports

### Reporting Bugs

Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Relevant logs or error messages

### Suggesting Features

Include:
- Clear description of the feature
- Use case/motivation
- Proposed implementation (if applicable)
- Alternative solutions considered

## Areas for Contribution

### High Priority

- [ ] Rate limiting implementation
- [ ] Enhanced vehicle make/model detection
- [ ] Improved license plate validation for different regions
- [ ] Mobile app integration examples
- [ ] Performance optimization for video processing

### Medium Priority

- [ ] Additional incident types
- [ ] Advanced search filters
- [ ] Incident sharing functionality
- [ ] Export incident data to various formats
- [ ] Notification system

### Good First Issues

- [ ] Add more comprehensive input validation
- [ ] Improve error messages
- [ ] Add more unit tests
- [ ] Update documentation with examples
- [ ] Add logging throughout the application

## Documentation

When contributing documentation:

- Use clear, concise language
- Include code examples where appropriate
- Keep formatting consistent
- Update table of contents if needed

## Questions?

- Open an issue for general questions
- Use GitHub Discussions for broader topics
- Tag maintainers if urgent

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors will be recognized in:
- GitHub contributors page
- Release notes (for significant contributions)
- README acknowledgments section

Thank you for contributing to Dashcam Backend! 🚀

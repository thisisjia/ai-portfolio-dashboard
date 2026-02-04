# Test Suite

Unit tests for the resume dashboard backend.

## Running Tests

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src/solutions/resume_dashboard

# Run specific test file
pytest tests/test_router.py

# Run with verbose output
pytest -v
```

## Test Structure

- `conftest.py` - Shared fixtures and configuration
- `test_router.py` - Tests for RouterAgent routing logic
- `test_agents.py` - Tests for specialized agents (Technical, Personal, etc.)

## Test Coverage

- ✅ Router agent routing decisions
- ✅ Agent initialization and configuration
- ✅ Agent response validation
- ✅ Confidence scoring

## Future Tests

- API endpoint tests
- Database query tests
- Integration tests for full workflow
- Authentication tests

# Testing

Unit tests with mocked dependencies to avoid LLM API costs.

## Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/agents/test_feature_extraction_agent.py

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Verbose output
pytest tests/ -v

# Stop on first failure
pytest tests/ -x
```

## Test Organization

- `tests/agents/` - Agent tests (classification, search queries, workflows)
- `tests/test_routing.py` - Routing logic between agents
- `tests/conftest.py` - Shared fixtures and configuration


## Current Coverage

41 tests covering:
- Question classification
- Search query generation
- Agent answer workflows
- Multi-agent routing
- Edge cases and error handling

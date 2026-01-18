"""
Pytest configuration and shared fixtures

This file contains common test fixtures and configuration
that can be used across all test files.
"""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def project_root():
    """Return the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_dir(project_root):
    """Return the test data directory"""
    data_dir = project_root / "tests" / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def sample_search_results():
    """Sample search results for testing"""
    return """Found 3 search results:

[1] Towards Monosemanticity: Decomposing Language Models
    URL: https://transformer-circuits.pub/2023/monosemantic-features
    We use sparse autoencoders to decompose language models...

[2] Scaling Monosemanticity
    URL: https://transformer-circuits.pub/2024/scaling-monosemanticity
    We scale our previous work on monosemantic features...

[3] In-context Learning and Induction Heads
    URL: https://transformer-circuits.pub/2022/in-context-learning-and-induction-heads
    We investigate the phenomenon of in-context learning...
"""


@pytest.fixture
def sample_queries():
    """Sample queries for different question types"""
    return {
        "circuit_analysis": [
            "How does the IOI circuit work?",
            "Explain the mechanism of induction heads",
            "What is the implementation of the greater-than circuit?"
        ],
        "technique": [
            "How does activation patching work?",
            "Explain causal tracing",
            "What is ablation study?"
        ],
        "attention_head": [
            "What are induction heads?",
            "How do attention patterns work?",
            "Explain the QK circuit"
        ],
        "concept_explanation": [
            "What is monosemanticity?",
            "Explain sparse autoencoders",
            "Define superposition"
        ],
        "tool_usage": [
            "How do I use TransformerLens?",
            "Show me SAELens code examples",
            "How to use TransformerLens for feature extraction?"
        ],
        "general": [
            "What is mechanistic interpretability?",
            "Tell me about recent research",
            "Compare different approaches"
        ]
    }


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response structure"""
    return {
        "id": "chatcmpl-test123",
        "object": "chat.completion",
        "created": 1234567890,
        "model": "gpt-4",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "This is a test response"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }


@pytest.fixture
def mock_mcp_search_result():
    """Mock MCP search server result"""
    return """Found 5 search results:

[1] Test Paper Title
    URL: https://example.com/paper1
    This is a test snippet about the topic...

[2] Another Research Paper
    URL: https://example.com/paper2
    More information about the subject matter...

[3] Technical Blog Post
    URL: https://example.com/blog
    Blog post explaining the concept in detail...

[4] Documentation
    URL: https://example.com/docs
    Official documentation for the tool...

[5] ArXiv Paper
    URL: https://arxiv.org/abs/2301.12345
    Academic paper discussing the methodology...
"""


# Configure pytest to show more verbose output
def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_api: marks tests that require API keys"
    )


# Automatically skip tests that require API keys if not available
def pytest_collection_modifyitems(config, items):
    """Modify test collection to skip tests requiring API keys"""
    skip_requires_api = pytest.mark.skip(reason="API keys not configured")

    for item in items:
        if "requires_api" in item.keywords:
            # Check if API keys are available
            if not os.getenv("OPENAI_API_KEY") or not os.getenv("GOOGLE_API_KEY"):
                item.add_marker(skip_requires_api)

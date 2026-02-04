"""Pytest configuration and fixtures."""

import pytest
import os
from pathlib import Path


@pytest.fixture
def mock_groq_api_key(monkeypatch):
    """Mock Groq API key for testing."""
    monkeypatch.setenv("GROQ_API_KEY", "test-groq-key-12345")


@pytest.fixture
def sample_resume_data():
    """Sample resume data for testing agents."""
    return {
        "name": "Test User",
        "title": "Software Engineer",
        "skills": {
            "languages": ["Python", "JavaScript", "TypeScript"],
            "frameworks": ["FastAPI", "React", "Next.js"],
            "tools": ["Docker", "Git", "AWS"]
        },
        "experience": [
            {
                "company": "Tech Company",
                "role": "Senior Engineer",
                "duration": "2022-2024",
                "highlights": ["Built scalable APIs", "Led team of 3"]
            }
        ]
    }

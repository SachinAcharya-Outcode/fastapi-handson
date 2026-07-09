"""Tests for the Settings / config module.

Covers the field validator edge cases that can't be triggered through
normal env-var parsing with NoDecode.
"""

from pydantic import AnyHttpUrl

import pytest

from app.core.config import Settings


class TestCorsOriginsValidator:
    """BACKEND_CORS_ORIGINS field_validator edge cases."""

    def test_validator_with_list(self):
        """When ``v`` is already a ``list`` (e.g. direct instantiation)."""
        s = Settings(  # type: ignore[call-arg]
            BACKEND_CORS_ORIGINS=["http://localhost:4000", "http://localhost:5000"],
            SECRET_KEY="test-key",
        )
        origins = s.BACKEND_CORS_ORIGINS
        assert len(origins) == 2
        assert AnyHttpUrl("http://localhost:4000") in origins

    def test_validator_with_json_array_string(self):
        """When ``v`` is a JSON array string (starts with ``[``)."""
        s = Settings(  # type: ignore[call-arg]
            BACKEND_CORS_ORIGINS='["http://localhost:4000"]',
            SECRET_KEY="test-key",
        )
        origins = s.BACKEND_CORS_ORIGINS
        assert len(origins) == 1

    def test_validator_raises_on_invalid_type(self):
        """When ``v`` is neither str nor list (e.g. an int)."""
        with pytest.raises(ValueError):
            Settings(  # type: ignore[call-arg]
                BACKEND_CORS_ORIGINS=42,
                SECRET_KEY="test-key",
            )

    def test_validator_json_array_parsed_not_list(self):
        """When ``v`` is a JSON string but does not decode to a list."""
        with pytest.raises(ValueError):
            Settings(  # type: ignore[call-arg]
                BACKEND_CORS_ORIGINS='"just-a-string"',
                SECRET_KEY="test-key",
            )

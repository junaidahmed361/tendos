"""Tests for JWT token management — TDD."""

from __future__ import annotations

import time

import pytest

from tendos.security.tokens import TokenManager


class TestTokenManager:
    @pytest.fixture
    def manager(self):
        return TokenManager(secret="test-secret-key-for-jwt-signing-32ch")  # noqa: S106

    def test_issue_token(self, manager):
        token = manager.issue(
            cartridge_id="hub://clinical-nlp-v2",
            user_id="user-123",
            calls_allowed=100,
        )
        assert isinstance(token, str)
        assert len(token) > 0

    def test_validate_token(self, manager):
        token = manager.issue(
            cartridge_id="hub://clinical-nlp-v2",
            user_id="user-123",
            calls_allowed=50,
        )
        claims = manager.validate(token)
        assert claims["cartridge_id"] == "hub://clinical-nlp-v2"
        assert claims["user_id"] == "user-123"
        assert claims["calls_allowed"] == 50

    def test_expired_token_raises(self, manager):
        token = manager.issue(
            cartridge_id="hub://x",
            user_id="u",
            calls_allowed=1,
            ttl_seconds=0,
        )
        time.sleep(1)
        with pytest.raises(ValueError, match="expired"):
            manager.validate(token)

    def test_invalid_token_raises(self, manager):
        with pytest.raises(ValueError, match="Invalid token"):
            manager.validate("not.a.valid.token")

    def test_wrong_secret_raises(self, manager):
        token = manager.issue(cartridge_id="x", user_id="u", calls_allowed=1)
        other = TokenManager(secret="different-secret-key-for-jwt-32chars")  # noqa: S106
        with pytest.raises(ValueError, match="Invalid token"):
            other.validate(token)

    def test_token_contains_issued_at(self, manager):
        token = manager.issue(cartridge_id="x", user_id="u", calls_allowed=1)
        claims = manager.validate(token)
        assert "iat" in claims
        assert "exp" in claims

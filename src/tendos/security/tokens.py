"""JWT token management for pay-per-use cartridge licensing."""

from __future__ import annotations

import time
from typing import Any
import jwt


class TokenManager:
    """Issue and validate JWT tokens for cartridge usage."""

    ALGORITHM = "HS256"
    DEFAULT_TTL = 3600 * 24  # 24 hours

    def __init__(self, secret: str) -> None:
        self._secret = secret

    def issue(
        self,
        *,
        cartridge_id: str,
        user_id: str,
        calls_allowed: int,
        ttl_seconds: int | None = None,
    ) -> str:
        now = time.time()
        ttl = ttl_seconds if ttl_seconds is not None else self.DEFAULT_TTL
        payload = {
            "cartridge_id": cartridge_id,
            "user_id": user_id,
            "calls_allowed": calls_allowed,
            "iat": now,
            "exp": now + ttl,
        }
        return jwt.encode(payload, self._secret, algorithm=self.ALGORITHM)

    def validate(self, token: str) -> dict[str, Any]:
        try:
            return jwt.decode(token, self._secret, algorithms=[self.ALGORITHM])
        except jwt.ExpiredSignatureError as e:
            raise ValueError("Token has expired") from e
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {e}") from e

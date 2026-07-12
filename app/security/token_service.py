import jwt
from typing import Optional
from datetime import datetime, timedelta, timezone


class TokenService:
    """Creates and decodes JWT access tokens."""

    def __init__(self, secret: str, algorithm: str = "HS256",
        ttl_hours: int = 24) -> None:
        self._secret = secret
        self._algorithm = algorithm
        self._ttl_hours = ttl_hours

    def create(self, user_id: int, role: str) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": now + timedelta(hours=self._ttl_hours),
            "iat": now
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def decode(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError:
            return None

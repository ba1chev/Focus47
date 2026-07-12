from passlib.context import CryptContext


class PasswordHasher:
    """Hashes and verifies passwords using bcrypt."""

    def __init__(self) -> None:
        self._context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def hash(self, plain: str) -> str:
        return self._context.hash(plain)

    def verify(self, plain: str, hashed: str) -> bool:
        return self._context.verify(plain, hashed)

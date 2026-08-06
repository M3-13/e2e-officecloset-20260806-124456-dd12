import os
import secrets
import warnings


def generate_secret() -> str:
    return secrets.token_hex(32)


class Settings:
    _jwt_secret: str | None = None

    @property
    def jwt_secret(self) -> str:
        secret = os.environ.get("JWT_SECRET")
        if secret:
            return secret
        if self._jwt_secret is None:
            self._jwt_secret = generate_secret()
            warnings.warn(
                "JWT_SECRET not set in environment — using a temporary generated value. "
                "Set JWT_SECRET for production. See RUN.json.",
                RuntimeWarning,
                stacklevel=2,
            )
        return self._jwt_secret

    @property
    def frontend_origin(self) -> str:
        return os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

    @property
    def database_url(self) -> str:
        return os.environ.get("DATABASE_URL", "sqlite:///./wardrobe.db")


settings = Settings()

from functools import lru_cache
from typing import Any

import jwt
from fastapi import HTTPException, status
from jwt import PyJWKClient

from app.core.config import get_settings


@lru_cache
def jwks_client() -> PyJWKClient:
    return PyJWKClient(get_settings().supabase_jwks_url)


def verify_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        header = jwt.get_unverified_header(token)
        algorithm = header.get("alg")
        if algorithm == "HS256":
            secret = settings.supabase_jwt_secret
            if secret is None:
                raise ValueError("HS256 token received but SUPABASE_JWT_SECRET is not configured")
            key = secret.get_secret_value()
        else:
            signing_key = jwks_client().get_signing_key_from_jwt(token)
            key = signing_key.key
        return jwt.decode(
            token,
            key,
            algorithms=[algorithm] if algorithm else ["RS256", "ES256"],
            audience="authenticated",
            issuer=settings.supabase_issuer,
            options={"require": ["sub", "exp", "iat"]},
        )
    except (jwt.PyJWTError, ValueError, OSError) as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token") from exc


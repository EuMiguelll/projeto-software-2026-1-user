import os
from functools import wraps

import requests
from authlib.integrations.flask_oauth2 import ResourceProtector
from authlib.oauth2.rfc7523 import JWTBearerTokenValidator
from joserfc.jwk import KeySet


class Auth0JWTValidator(JWTBearerTokenValidator):
    def __init__(self, domain: str, audience: str):
        issuer = f"https://{domain}/"
        jwks = requests.get(f"{issuer}.well-known/jwks.json", timeout=5).json()
        super().__init__(KeySet.import_key_set(jwks))
        self.claims_options = {
            "exp": {"essential": True},
            "aud": {"essential": True, "value": audience},
            "iss": {"essential": True, "value": issuer},
        }

    def authenticate_token(self, token_string):
        try:
            return super().authenticate_token(token_string)
        except ValueError:
            return None


def _noop(*_args, **_kwargs):
    def deco(f):
        @wraps(f)
        def wrapper(*a, **kw):
            return f(*a, **kw)
        return wrapper
    return deco


if os.environ.get("AUTH_DISABLED") == "1":
    require_auth = _noop
else:
    _protector = ResourceProtector()
    _protector.register_token_validator(
        Auth0JWTValidator(
            os.environ["AUTH0_DOMAIN"],
            os.environ["AUTH0_AUDIENCE"],
        )
    )
    require_auth = _protector

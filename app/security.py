# app/security.py
from __future__ import annotations

import os
import json
import base64
from typing import Any, Dict, Optional
from collections.abc import Mapping

import requests
from authlib.integrations.flask_oauth2 import ResourceProtector, current_token
from authlib.jose import JsonWebKey, JsonWebToken
from authlib.oauth2.rfc6750 import BearerTokenValidator
# Compatibilidade do erro entre versões da Authlib
try:
    from authlib.oauth2.rfc6750.errors import InvalidTokenError  # >= 1.3
except Exception:
    from authlib.oauth2.rfc6750 import InvalidTokenError  # versões mais antigas

# Decorator para proteger rotas
require_oauth = ResourceProtector()


def _b64url_json(segment: str) -> Dict[str, Any]:
    """Decodifica um segmento JWT (header/payload) sem verificar assinatura (apenas debug)."""
    pad = "=" * (-len(segment) % 4)
    return json.loads(base64.urlsafe_b64decode(segment + pad))


class KeycloakJWTValidator(BearerTokenValidator):
    """
    Valida access tokens do Keycloak:
      - Baixa JWKS do realm e valida assinatura RS256
      - Checa 'iss' e valida exp/nbf/iat (com leeway)
      - Checa 'aud' se configurado
    Compatível com ResourceProtector (Authlib).
    """

    def __init__(
        self,
        issuer: str,
        jwks_uri: str,
        expected_aud: Optional[str] = None,
        timeout: int = 5,
        leeway: int = 60,
        debug: bool = False,
    ):
        super().__init__()  # garante TOKEN_TYPE='Bearer' e parsing do header Authorization
        self.realm = "prodmanager-api"  # aparece no WWW-Authenticate
        self.issuer = issuer
        self.jwks_uri = jwks_uri
        self.expected_aud = expected_aud
        self.timeout = timeout
        self.leeway = leeway
        self.debug = debug

        self._jwks_cache: Optional[Dict[str, Any]] = None
        self._jwt = JsonWebToken(["RS256"])

    # ====== Métodos esperados pelo ResourceProtector/BearerTokenValidator ======

    def authenticate_token(self, token_string: str):
        """Decodifica e valida o token, retornando 'claims' (dict-like) se ok."""
        # Log útil antes da verificação de assinatura
        if self.debug:
            try:
                h, p = token_string.split(".")[:2]
                header = _b64url_json(h)
                payload = _b64url_json(p)
                print(
                    "[AUTHN-DEBUG]",
                    "alg=", header.get("alg"),
                    "kid=", header.get("kid"),
                    "iss=", payload.get("iss"),
                    "aud=", payload.get("aud"),
                    "exp=", payload.get("exp"),
                    "nbf=", payload.get("nbf"),
                    flush=True,
                )
            except Exception:
                pass

        # 1) JWKS (com cache simples)
        jwks = self._get_jwks()

        # 2) Valida assinatura e issuer
        claims = self._jwt.decode(
            token_string,
            JsonWebKey.import_key_set(jwks),
            claims_options={
                "iss": {"essential": True, "values": [self.issuer]},
                # aud opcional: validamos nós mesmos abaixo
                "aud": {"essential": False},
            },
        )
        # 3) exp/nbf/iat com leeway
        claims.validate(leeway=self.leeway)
        return claims

    def validate_request(self, request):
        """Pré-validação do request (não precisamos de nada extra aqui)."""
        return None

    def validate_token(self, claims, scopes, request, **kwargs):
        """Checagens adicionais pós-assinatura (ex.: audience)."""
        if self.expected_aud:
            aud = claims.get("aud")
            ok = False
            if isinstance(aud, str):
                ok = (aud == self.expected_aud)
            elif isinstance(aud, (list, tuple, set)):
                ok = (self.expected_aud in aud)
            if not ok:
                raise InvalidTokenError(description="invalid audience")
        return claims

    # ====== Helpers ======

    def _get_jwks(self) -> Dict[str, Any]:
        if self._jwks_cache is None:
            resp = requests.get(self.jwks_uri, timeout=self.timeout)
            if self.debug:
                print("[JWKS]", resp.status_code,
                      "from", self.jwks_uri, flush=True)
            resp.raise_for_status()
            self._jwks_cache = resp.json()
        return self._jwks_cache


def init_oauth(app) -> None:
    """
    Inicializa o validador usando:
      - OIDC_WELL_KNOWN (descoberta)
      - OIDC_AUDIENCE
      - OIDC_DEBUG=true|false
      - OIDC_DISABLE_AUDIENCE_CHECK=true|false
    """
    # Descoberta OIDC via .well-known
    wk_url = app.config["OIDC_WELL_KNOWN"]
    wk = requests.get(wk_url, timeout=5).json()
    issuer = wk["issuer"]
    jwks_uri = wk["jwks_uri"]

    audience = app.config.get("OIDC_AUDIENCE")
    debug = str(os.getenv("OIDC_DEBUG", "")).lower() in (
        "1", "true", "yes", "on")
    disable_aud = str(os.getenv("OIDC_DISABLE_AUDIENCE_CHECK", "")).lower() in (
        "1", "true", "yes", "on"
    )
    expected_aud = None if disable_aud else audience

    if debug:
        print(
            "[OIDC]",
            f"issuer={issuer}",
            f"jwks_uri={jwks_uri}",
            f"audience={audience}",
            f"aud_check={'OFF' if disable_aud else 'ON'}",
            flush=True,
        )

    validator = KeycloakJWTValidator(
        issuer=issuer,
        jwks_uri=jwks_uri,
        expected_aud=expected_aud,
        timeout=5,
        leeway=60,
        debug=debug,
    )
    require_oauth.register_token_validator(validator)


# ====== Helpers para roles ======

def _extract_claims_from_current_token() -> dict:
    """
    Extrai claims do current_token de forma compatível com várias versões da Authlib.
    Tenta .claims, .token (ou _token), e por fim o próprio objeto (Claims / Mapping).
    """
    ct = current_token
    for attr in ("claims", "token", "_token"):
        v = getattr(ct, attr, None)
        if v is not None:
            # tenta converter para dict de maneira resiliente
            if isinstance(v, Mapping):
                return dict(v)
            try:
                return dict(v)  # alguns objetos Claims são iteráveis
            except Exception:
                try:
                    return {k: v.get(k) for k in v.keys()}  # type: ignore
                except Exception:
                    pass
    # fallback: o próprio objeto
    if isinstance(ct, Mapping):
        return dict(ct)
    try:
        return dict(ct)
    except Exception:
        return {}


def has_role(role: str, client: str = "prodmanager-api") -> bool:
    """
    Verifica se o access_token possui uma role do Keycloak em resource_access.<client>.roles
    Ex.: has_role("products:write")
    """
    claims = _extract_claims_from_current_token()
    roles = (claims.get("resource_access", {}).get(
        client, {}) or {}).get("roles", [])
    if role in roles:
        return True
    # fallback: realm roles (não é o nosso caso, mas ajuda)
    realm_roles = (claims.get("realm_access", {}) or {}).get("roles", [])
    return role in realm_roles

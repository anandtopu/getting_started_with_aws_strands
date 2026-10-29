"""Verify inbound Cognito tokens before binding identity; keep outbound OAuth out of prompts."""

import time
import uuid
from contextlib import nullcontext

from botocore.stub import Stubber

from common.cloud_clients import client


def verify_token(token, key, *, issuer, client_id, scope="nimbus/read"):
    import jwt

    claims = jwt.decode(
        token,
        key,
        algorithms=["RS256"],
        issuer=issuer,
        options={"verify_aud": False, "require": ["exp", "iat", "sub", "iss"]},
    )
    # Cognito access tokens use client_id; ID tokens use aud and must not authorize an API.
    if (
        claims.get("token_use") != "access"
        or claims.get("client_id") != client_id
        or scope not in claims.get("scope", "").split()
    ):
        raise ValueError("Access token has the wrong client, type or scope")
    return {"actor": claims["sub"], "scope": scope}


def demo_identity():
    import jwt
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    issuer, client_id = "https://issuer.nimbus.example", "offline-client"
    payload = {
        "sub": str(uuid.uuid4()),
        "iss": issuer,
        "iat": int(time.time()),
        "exp": int(time.time()) + 60,
        "token_use": "access",
        "client_id": client_id,
        "scope": "nimbus/read",
    }
    token = jwt.encode(payload, key, algorithm="RS256")
    verified = verify_token(token, key.public_key(), issuer=issuer, client_id=client_id)
    return verified


def cognito_identity(settings, token, pool_id, client_id):
    import re

    import jwt

    if not re.fullmatch(re.escape(settings.aws_region) + r"_[A-Za-z0-9]+", pool_id):
        raise ValueError("Pool ID must belong to the configured AWS region")
    issuer = f"https://cognito-idp.{settings.aws_region}.amazonaws.com/{pool_id}"
    key = jwt.PyJWKClient(issuer + "/.well-known/jwks.json", timeout=5).get_signing_key_from_jwt(
        token
    )
    return verify_token(token, key.key, issuer=issuer, client_id=client_id)


def outbound_oauth(settings, *, workload, provider, user_token):
    api = client("bedrock-agentcore", settings)
    request = {"workloadName": workload, "userToken": user_token}
    stub = Stubber(api)
    if settings.provider == "mock":
        stub.add_response(
            "get_workload_access_token_for_jwt",
            {"workloadAccessToken": "offline-workload-token"},
            request,
        )
        stub.add_response(
            "get_resource_oauth2_token",
            {"accessToken": "offline-resource-token"},
            {
                "workloadIdentityToken": "offline-workload-token",
                "resourceCredentialProviderName": provider,
                "scopes": ["read"],
                "oauth2Flow": "USER_FEDERATION",
            },
        )
    with stub if settings.provider == "mock" else nullcontext():
        workload_token = api.get_workload_access_token_for_jwt(**request)["workloadAccessToken"]
        response = api.get_resource_oauth2_token(
            workloadIdentityToken=workload_token,
            resourceCredentialProviderName=provider,
            scopes=["read"],
            oauth2Flow="USER_FEDERATION",
        )
        if settings.provider == "mock":
            stub.assert_no_pending_responses()
    # A first federation request can need consent at authorizationUrl. The host UI handles it.
    return {
        "credential_ready": bool(response.get("accessToken")),
        "consent_required": bool(response.get("authorizationUrl")),
    }

"""Sign in through Cognito with PKCE, then launch the live Copilot without saving its token.

Run: uv run --group identity python scripts/cognito_copilot.py
Expected: browser sign-in, then a public quote. Cost: Cognito and AgentCore usage.
Resources: existing NimbusAgentCore stack; this script provisions nothing.
"""

import base64
import hashlib
import os
import re
import secrets
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx

from common.config import ROOT, course_value, load_settings
from common.pretty import run_cli


def authorization_request(domain, region, client_id, state, verifier):
    target = urlsplit(domain)
    if (
        target.scheme != "https"
        or not re.fullmatch(
            r"[a-z0-9-]+\.auth\." + re.escape(region) + r"\.amazoncognito\.com",
            target.hostname or "",
        )
        or target.username
        or target.password
        or target.port
        or target.query
        or target.fragment
        or target.path not in ("", "/")
        or not client_id
    ):
        raise ValueError("Set NIMBUS_LOGIN_DOMAIN and NIMBUS_CLIENT_ID from the stack outputs")
    challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    )
    return (
        domain.rstrip("/")
        + "/oauth2/authorize?"
        + urlencode(
            {
                "response_type": "code",
                "client_id": client_id,
                "redirect_uri": "http://localhost:8765/callback",
                "scope": "openid nimbus/read",
                "state": state,
                "code_challenge": challenge,
                "code_challenge_method": "S256",
            }
        )
    )


def callback_code(path, state):
    url = urlsplit(path)
    params = parse_qs(url.query)
    if url.path != "/callback" or not secrets.compare_digest(params.get("state", [""])[0], state):
        raise ValueError("Sign-in callback state mismatch")
    code = params.get("code", [""])[0]
    if not code or "error" in params:
        raise ValueError("Sign-in did not return an authorization code")
    return code


def main():
    cfg = load_settings()
    domain, client_id = course_value("NIMBUS_LOGIN_DOMAIN"), course_value("NIMBUS_CLIENT_ID")
    state, verifier = secrets.token_urlsafe(32), secrets.token_urlsafe(64)
    url = authorization_request(domain, cfg.aws_region, client_id, state, verifier)
    codes = []

    class Callback(BaseHTTPRequestHandler):
        def do_GET(self):
            try:
                code = callback_code(self.path, state)
            except ValueError:
                self.send_error(400, "Invalid sign-in callback")
                return
            codes.append(code)
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Signed in. Return to the terminal; you may close this tab.")

        def log_message(self, *_):
            return  # Authorization codes and callback URLs must never enter access logs.

    with HTTPServer(("127.0.0.1", 8765), Callback) as server:
        server.timeout = 180
        print("Opening Cognito sign-in. Use the course user created by your account administrator.")
        if not webbrowser.open(url):
            raise ValueError("Could not open the browser for sign-in")
        server.handle_request()
    if not codes:
        raise TimeoutError("Sign-in timed out or the callback was rejected")
    with httpx.Client(timeout=10, follow_redirects=False, trust_env=False) as client:
        response = client.post(
            domain.rstrip("/") + "/oauth2/token",
            data={
                "grant_type": "authorization_code",
                "client_id": client_id,
                "code": codes[0],
                "redirect_uri": "http://localhost:8765/callback",
                "code_verifier": verifier,
            },
        )
        if response.status_code != 200:
            raise ValueError(
                "Cognito token exchange failed; check the client and callback configuration"
            )
        token = response.json()["access_token"]
    result = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            str(ROOT / "modules/21_agentcore/use_case/production_copilot.py"),
            "--live-aws",
        ],
        cwd=ROOT,
        env={**os.environ, "NIMBUS_ACCESS_TOKEN": token},
        check=False,
        timeout=180,
    )
    return result.returncode


if __name__ == "__main__":
    run_cli(main)

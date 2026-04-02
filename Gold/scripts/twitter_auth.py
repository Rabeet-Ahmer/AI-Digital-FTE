"""
Twitter OAuth 2.0 PKCE Authorization Flow.

One-time setup: runs a local HTTP server, opens browser for Twitter auth,
captures the callback, exchanges for tokens, and saves to .twitter_session/.

Usage:
    uv run python twitter_auth.py

Environment variables required:
    TWITTER_CLIENT_ID — OAuth 2.0 Client ID
    TWITTER_CLIENT_SECRET — OAuth 2.0 Client Secret (optional for public clients)
"""

import hashlib
import http.server
import json
import os
import secrets
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import requests

TWITTER_AUTH_URL = "https://twitter.com/i/oauth2/authorize"
TWITTER_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"
REDIRECT_URI = "http://127.0.0.1:8739/callback"
SCOPES = "tweet.read tweet.write users.read offline.access"

SESSION_DIR = Path(__file__).parent / ".twitter_session"
TOKEN_FILE = SESSION_DIR / "tokens.json"


def get_env(name: str) -> str:
    val = os.environ.get(name, "").strip()
    if not val:
        print(f"Error: Missing environment variable {name}")
        sys.exit(1)
    return val


class CallbackHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler to capture OAuth callback."""
    auth_code = None
    state_received = None

    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == "/callback":
            CallbackHandler.auth_code = params.get("code", [None])[0]
            CallbackHandler.state_received = params.get("state", [None])[0]

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h2>Authorization successful!</h2><p>You can close this tab.</p></body></html>")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress server logs


def generate_pkce() -> tuple[str, str]:
    """Generate PKCE code_verifier and code_challenge."""
    verifier = secrets.token_urlsafe(64)[:128]
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = secrets.token_urlsafe(64)  # placeholder
    # Proper S256 challenge
    import base64
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge


def main():
    client_id = get_env("TWITTER_CLIENT_ID")
    client_secret = os.environ.get("TWITTER_CLIENT_SECRET", "").strip()

    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    # Generate PKCE
    code_verifier, code_challenge = generate_pkce()
    state = secrets.token_urlsafe(32)

    # Build auth URL
    auth_params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    auth_url = f"{TWITTER_AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in auth_params.items())}"

    # Start local server
    server = http.server.HTTPServer(("127.0.0.1", 8739), CallbackHandler)
    server_thread = threading.Thread(target=server.handle_request, daemon=True)
    server_thread.start()

    print("Opening browser for Twitter authorization...")
    print(f"If browser doesn't open, visit:\n{auth_url}\n")
    webbrowser.open(auth_url)

    # Wait for callback
    server_thread.join(timeout=120)
    server.server_close()

    if not CallbackHandler.auth_code:
        print("Error: No authorization code received (timed out or user denied)")
        sys.exit(1)

    if CallbackHandler.state_received != state:
        print("Error: State mismatch — possible CSRF attack")
        sys.exit(1)

    print("Authorization code received. Exchanging for tokens...")

    # Exchange code for tokens
    token_data = {
        "grant_type": "authorization_code",
        "code": CallbackHandler.auth_code,
        "redirect_uri": REDIRECT_URI,
        "code_verifier": code_verifier,
        "client_id": client_id,
    }

    auth = None
    if client_secret:
        auth = (client_id, client_secret)

    resp = requests.post(
        TWITTER_TOKEN_URL,
        data=token_data,
        auth=auth,
        timeout=15,
    )
    tokens = resp.json()

    if "access_token" not in tokens:
        print(f"Error: Token exchange failed: {tokens}")
        sys.exit(1)

    # Save tokens
    TOKEN_FILE.write_text(json.dumps(tokens, indent=2), encoding="utf-8")
    print(f"Tokens saved to {TOKEN_FILE}")
    print(f"Access token type: {tokens.get('token_type')}")
    print(f"Scopes: {tokens.get('scope')}")
    if tokens.get("refresh_token"):
        print("Refresh token saved (for token renewal)")
    print("\nSetup complete! You can now use twitter_poster.py")


if __name__ == "__main__":
    main()

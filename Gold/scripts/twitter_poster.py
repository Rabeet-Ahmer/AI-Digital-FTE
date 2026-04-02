"""
Twitter/X Poster — Posts tweets and threads via Twitter API v2.

Usage:
    uv run python twitter_poster.py --content "Tweet text"
    uv run python twitter_poster.py --thread "Tweet 1|||Tweet 2|||Tweet 3"
    uv run python twitter_poster.py --dry-run --content "Test tweet"
    uv run python twitter_poster.py --check-auth

Environment variables required:
    TWITTER_BEARER_TOKEN — For app-only auth (read operations)

OAuth 2.0 User Context (for posting):
    Requires completing OAuth flow via twitter_auth.py first.
    Stores tokens in .twitter_session/tokens.json
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests

TWITTER_API_BASE = "https://api.twitter.com/2"
SESSION_DIR = Path(__file__).parent / ".twitter_session"
TOKEN_FILE = SESSION_DIR / "tokens.json"

MAX_TWEET_LENGTH = 280


def load_user_token() -> str | None:
    """Load OAuth 2.0 user access token from session file."""
    if TOKEN_FILE.exists():
        try:
            data = json.loads(TOKEN_FILE.read_text(encoding="utf-8"))
            return data.get("access_token")
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def get_auth_header() -> dict:
    """Get authorization header — prefer user token, fall back to bearer."""
    user_token = load_user_token()
    if user_token:
        return {"Authorization": f"Bearer {user_token}"}

    bearer = os.environ.get("TWITTER_BEARER_TOKEN", "").strip()
    if bearer:
        return {"Authorization": f"Bearer {bearer}"}

    print(json.dumps({"status": "error", "error": "No auth available. Run twitter_auth.py or set TWITTER_BEARER_TOKEN"}))
    sys.exit(1)


def check_auth() -> dict:
    """Verify authentication by fetching the authenticated user."""
    headers = get_auth_header()
    resp = requests.get(
        f"{TWITTER_API_BASE}/users/me",
        headers=headers,
        timeout=15,
    )
    data = resp.json()

    if "data" in data:
        user = data["data"]
        return {
            "status": "ok",
            "user_id": user.get("id"),
            "username": user.get("username"),
            "name": user.get("name"),
            "has_user_token": load_user_token() is not None,
        }
    return {
        "status": "error",
        "error": data.get("detail", data.get("errors", [{}])[0].get("message", str(data))),
    }


def validate_tweet(content: str) -> str | None:
    """Validate tweet content. Returns error message or None if valid."""
    if not content.strip():
        return "Tweet content is empty"
    if len(content) > MAX_TWEET_LENGTH:
        return f"Tweet exceeds {MAX_TWEET_LENGTH} chars ({len(content)} chars)"
    return None


def post_tweet(content: str, reply_to: str | None = None, dry_run: bool = False) -> dict:
    """Post a single tweet."""
    error = validate_tweet(content)
    if error:
        return {"status": "error", "error": error}

    if dry_run:
        result = {
            "status": "dry_run",
            "content_length": len(content),
            "preview": content,
        }
        if reply_to:
            result["reply_to"] = reply_to
        return result

    headers = get_auth_header()
    headers["Content-Type"] = "application/json"

    payload = {"text": content}
    if reply_to:
        payload["reply"] = {"in_reply_to_tweet_id": reply_to}

    resp = requests.post(
        f"{TWITTER_API_BASE}/tweets",
        headers=headers,
        json=payload,
        timeout=30,
    )
    data = resp.json()

    if "data" in data:
        return {
            "status": "ok",
            "tweet_id": data["data"]["id"],
            "text": data["data"].get("text", content),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    return {
        "status": "error",
        "error": data.get("detail", data.get("errors", [{}])[0].get("message", str(data))),
    }


def post_thread(tweets: list[str], dry_run: bool = False) -> dict:
    """Post a thread of tweets, chaining via reply_to."""
    if len(tweets) < 2:
        return {"status": "error", "error": "Thread requires at least 2 tweets"}
    if len(tweets) > 10:
        return {"status": "error", "error": "Thread maximum is 10 tweets"}

    # Validate all tweets first
    for i, tweet in enumerate(tweets):
        error = validate_tweet(tweet)
        if error:
            return {"status": "error", "error": f"Tweet {i+1}: {error}"}

    if dry_run:
        return {
            "status": "dry_run",
            "thread_length": len(tweets),
            "tweets": [{"index": i+1, "length": len(t), "preview": t} for i, t in enumerate(tweets)],
        }

    results = []
    reply_to = None

    for i, tweet in enumerate(tweets):
        result = post_tweet(tweet, reply_to=reply_to)
        if result["status"] != "ok":
            return {
                "status": "error",
                "error": f"Thread failed at tweet {i+1}: {result.get('error')}",
                "posted": results,
            }
        results.append(result)
        reply_to = result["tweet_id"]

    return {
        "status": "ok",
        "thread_length": len(results),
        "tweets": results,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="Twitter/X Poster (API v2)")
    parser.add_argument("--content", help="Tweet text (max 280 chars)")
    parser.add_argument("--thread", help="Thread tweets separated by |||")
    parser.add_argument("--content-file", help="Read content from file")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--check-auth", action="store_true", help="Verify authentication")

    args = parser.parse_args()

    if args.check_auth:
        print(json.dumps(check_auth(), indent=2))
        return

    content = args.content
    if args.content_file:
        content = open(args.content_file, encoding="utf-8").read().strip()

    if args.thread:
        tweets = [t.strip() for t in args.thread.split("|||") if t.strip()]
        result = post_thread(tweets, dry_run=args.dry_run)
    elif content:
        result = post_tweet(content, dry_run=args.dry_run)
    else:
        print(json.dumps({"status": "error", "error": "Provide --content, --content-file, or --thread"}))
        sys.exit(1)

    print(json.dumps(result, indent=2))
    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()

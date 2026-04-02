"""
Meta (Facebook & Instagram) Poster — Posts content via Graph API.

Usage:
    uv run python meta_poster.py --content "Post text" --platform facebook
    uv run python meta_poster.py --content "Caption" --platform instagram --image-url "https://..."
    uv run python meta_poster.py --dry-run --content "Test" --platform facebook
    uv run python meta_poster.py --check-token
    uv run python meta_poster.py --refresh-token

Environment variables required:
    META_PAGE_ACCESS_TOKEN — Long-lived Page Access Token
    META_PAGE_ID — Facebook Page ID
    META_IG_USER_ID — Instagram Business Account ID
    META_APP_ID — Facebook App ID (for token refresh)
    META_APP_SECRET — Facebook App Secret (for token refresh)
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import requests

GRAPH_API_BASE = "https://graph.facebook.com/v22.0"


def get_env(name: str) -> str:
    """Get required environment variable or exit."""
    val = os.environ.get(name, "").strip()
    if not val:
        print(json.dumps({"status": "error", "error": f"Missing env var: {name}"}))
        sys.exit(1)
    return val


def check_token() -> dict:
    """Verify the Page Access Token is valid and show expiry info."""
    token = get_env("META_PAGE_ACCESS_TOKEN")
    resp = requests.get(
        f"{GRAPH_API_BASE}/debug_token",
        params={"input_token": token, "access_token": token},
        timeout=15,
    )
    data = resp.json()
    if "error" in data:
        return {"status": "error", "error": data["error"].get("message", str(data))}

    token_data = data.get("data", {})
    return {
        "status": "ok",
        "app_id": token_data.get("app_id"),
        "type": token_data.get("type"),
        "is_valid": token_data.get("is_valid"),
        "expires_at": token_data.get("expires_at", 0),
        "scopes": token_data.get("scopes", []),
    }


def refresh_token() -> dict:
    """Exchange a valid token for a new long-lived token."""
    token = get_env("META_PAGE_ACCESS_TOKEN")
    app_id = get_env("META_APP_ID")
    app_secret = get_env("META_APP_SECRET")

    resp = requests.get(
        f"{GRAPH_API_BASE}/oauth/access_token",
        params={
            "grant_type": "fb_exchange_token",
            "client_id": app_id,
            "client_secret": app_secret,
            "fb_exchange_token": token,
        },
        timeout=15,
    )
    data = resp.json()
    if "access_token" in data:
        return {
            "status": "ok",
            "new_token": data["access_token"],
            "token_type": data.get("token_type"),
            "expires_in": data.get("expires_in"),
            "message": "Update META_PAGE_ACCESS_TOKEN in your .env with the new_token value",
        }
    return {"status": "error", "error": data.get("error", {}).get("message", str(data))}


def post_facebook(content: str, dry_run: bool = False) -> dict:
    """Post a text update to Facebook Page."""
    token = get_env("META_PAGE_ACCESS_TOKEN")
    page_id = get_env("META_PAGE_ID")

    if dry_run:
        return {
            "status": "dry_run",
            "platform": "facebook",
            "page_id": page_id,
            "content_length": len(content),
            "preview": content[:200],
        }

    resp = requests.post(
        f"{GRAPH_API_BASE}/{page_id}/feed",
        data={"message": content, "access_token": token},
        timeout=30,
    )
    data = resp.json()

    if "id" in data:
        return {
            "status": "ok",
            "platform": "facebook",
            "post_id": data["id"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    return {
        "status": "error",
        "platform": "facebook",
        "error": data.get("error", {}).get("message", str(data)),
    }


def post_instagram(caption: str, image_url: str, dry_run: bool = False) -> dict:
    """Post an image with caption to Instagram (2-step: create container → publish)."""
    token = get_env("META_PAGE_ACCESS_TOKEN")
    ig_user_id = get_env("META_IG_USER_ID")

    if not image_url:
        return {"status": "error", "platform": "instagram", "error": "Instagram requires --image-url (must be a public URL)"}

    if dry_run:
        return {
            "status": "dry_run",
            "platform": "instagram",
            "ig_user_id": ig_user_id,
            "caption_length": len(caption),
            "image_url": image_url,
            "preview": caption[:200],
        }

    # Step 1: Create media container
    resp = requests.post(
        f"{GRAPH_API_BASE}/{ig_user_id}/media",
        data={
            "image_url": image_url,
            "caption": caption,
            "access_token": token,
        },
        timeout=30,
    )
    container_data = resp.json()

    if "id" not in container_data:
        return {
            "status": "error",
            "platform": "instagram",
            "step": "create_container",
            "error": container_data.get("error", {}).get("message", str(container_data)),
        }

    container_id = container_data["id"]

    # Step 2: Publish the container
    resp = requests.post(
        f"{GRAPH_API_BASE}/{ig_user_id}/media_publish",
        data={
            "creation_id": container_id,
            "access_token": token,
        },
        timeout=30,
    )
    publish_data = resp.json()

    if "id" in publish_data:
        return {
            "status": "ok",
            "platform": "instagram",
            "media_id": publish_data["id"],
            "container_id": container_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    return {
        "status": "error",
        "platform": "instagram",
        "step": "publish",
        "error": publish_data.get("error", {}).get("message", str(publish_data)),
    }


def main():
    parser = argparse.ArgumentParser(description="Meta (Facebook/Instagram) Poster")
    parser.add_argument("--content", help="Post content / caption text")
    parser.add_argument("--platform", choices=["facebook", "instagram"], help="Target platform")
    parser.add_argument("--image-url", help="Public image URL (required for Instagram)")
    parser.add_argument("--content-file", help="Read content from file instead of --content")
    parser.add_argument("--dry-run", action="store_true", help="Preview without posting")
    parser.add_argument("--check-token", action="store_true", help="Verify token validity")
    parser.add_argument("--refresh-token", action="store_true", help="Exchange for new long-lived token")

    args = parser.parse_args()

    if args.check_token:
        print(json.dumps(check_token(), indent=2))
        return

    if args.refresh_token:
        print(json.dumps(refresh_token(), indent=2))
        return

    # Get content
    content = args.content
    if args.content_file:
        content = open(args.content_file, encoding="utf-8").read().strip()

    if not content:
        print(json.dumps({"status": "error", "error": "No content provided. Use --content or --content-file"}))
        sys.exit(1)

    if not args.platform:
        print(json.dumps({"status": "error", "error": "No --platform specified (facebook or instagram)"}))
        sys.exit(1)

    if args.platform == "facebook":
        result = post_facebook(content, dry_run=args.dry_run)
    else:
        result = post_instagram(content, args.image_url or "", dry_run=args.dry_run)

    print(json.dumps(result, indent=2))

    if result.get("status") == "error":
        sys.exit(1)


if __name__ == "__main__":
    main()

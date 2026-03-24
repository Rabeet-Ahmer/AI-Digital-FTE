"""
LinkedIn Poster - Automated LinkedIn posting via Playwright.

Uses a persistent browser context (session reuse) to post content
to LinkedIn without requiring login each time. Session must be
set up first via linkedin_setup.py.

Usage:
    uv run python linkedin_poster.py --content "Your post text here"
    uv run python linkedin_poster.py --content "Test post" --dry-run
    uv run python linkedin_poster.py --content-file /path/to/post.txt
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Playwright is imported inside functions to allow the module to be
# imported even when playwright isn't installed (for testing/inspection).

# Session storage directory (relative to this script)
SESSION_DIR = Path(__file__).resolve().parent / ".linkedin_session"


def get_session_dir() -> Path:
    """Return the session storage directory path."""
    return SESSION_DIR


def check_session() -> bool:
    """Check if a valid LinkedIn session exists."""
    session_dir = get_session_dir()
    if not session_dir.exists():
        return False
    # Check for Chromium state files
    state_files = list(session_dir.glob("*"))
    return len(state_files) > 0


def post_to_linkedin(content: str, dry_run: bool = False) -> dict:
    """
    Post content to LinkedIn using Playwright with persistent session.

    Args:
        content: The post text to publish.
        dry_run: If True, simulate the posting without actually submitting.

    Returns:
        dict with keys: success (bool), message (str), timestamp (str),
        content_preview (str), dry_run (bool)
    """
    from playwright.sync_api import sync_playwright

    result = {
        "success": False,
        "message": "",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "content_preview": content[:200],
        "dry_run": dry_run,
    }

    session_dir = get_session_dir()
    if not check_session():
        result["message"] = (
            "No LinkedIn session found. Run linkedin_setup.py first to log in."
        )
        return result

    try:
        with sync_playwright() as p:
            # Launch with persistent context (reuses saved session)
            browser = p.chromium.launch_persistent_context(
                user_data_dir=str(session_dir),
                headless=True,
                viewport={"width": 1280, "height": 800},
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Navigate to LinkedIn feed
            page.goto("https://www.linkedin.com/feed/", wait_until="domcontentloaded")
            time.sleep(3)

            # Check if we're logged in by looking for the feed
            if "login" in page.url.lower() or "signin" in page.url.lower():
                result["message"] = (
                    "LinkedIn session expired. Run linkedin_setup.py to log in again."
                )
                browser.close()
                return result

            # Debug: save screenshot and page HTML for selector analysis
            debug_dir = Path(__file__).resolve().parent / ".debug"
            debug_dir.mkdir(exist_ok=True)
            page.screenshot(path=str(debug_dir / "feed_page.png"))
            (debug_dir / "feed_page.html").write_text(page.content(), encoding="utf-8")

            if dry_run:
                result["success"] = True
                result["message"] = (
                    f"DRY RUN: Would post {len(content)} chars to LinkedIn. "
                    f"Session is valid. Page loaded successfully."
                )
                browser.close()
                return result

            # Click "Start a post" — target the outer role="button" container
            # The aria-label is on an inner div; the actual clickable element
            # is the parent div[role="button"][tabindex="0"].
            start_post_selectors = [
                "div[role='button']:has(div[aria-label='Start a post'])",
                "div[role='button']:has-text('Start a post')",
                "[aria-label='Start a post']",
            ]
            start_post = None
            for selector in start_post_selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.is_visible(timeout=5000):
                        start_post = loc
                        break
                except Exception:
                    continue
            if start_post is None:
                page.screenshot(path=str(debug_dir / "no_start_post.png"))
                raise Exception(
                    "Could not find 'Start a post' button on the feed page."
                )

            start_post.click(timeout=10000)

            # Wait for the post composition modal to load
            # LinkedIn lazy-loads the editor — wait for contenteditable or dialog
            modal_selectors = [
                "[contenteditable='true']",
                "[role='dialog'] [contenteditable='true']",
                "[role='textbox']",
                "div[role='dialog']",
            ]
            modal_appeared = False
            for selector in modal_selectors:
                try:
                    page.wait_for_selector(selector, timeout=10000)
                    modal_appeared = True
                    break
                except Exception:
                    continue

            if not modal_appeared:
                page.screenshot(path=str(debug_dir / "no_modal.png"))
                (debug_dir / "no_modal.html").write_text(
                    page.content(), encoding="utf-8"
                )
                raise Exception(
                    "Post modal did not appear after clicking 'Start a post'."
                )

            time.sleep(2)  # Let modal fully render

            # Save debug screenshot after modal opens
            page.screenshot(path=str(debug_dir / "modal_opened.png"))
            (debug_dir / "modal_opened.html").write_text(
                page.content(), encoding="utf-8"
            )

            # Type the content into the post editor
            editor_selectors = [
                "[role='dialog'] [contenteditable='true']",
                "[role='textbox'][contenteditable='true']",
                "div[contenteditable='true'][aria-label]",
                "div.ql-editor[data-placeholder]",
                "[contenteditable='true']",
                ".ql-editor",
            ]
            editor = None
            for selector in editor_selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.is_visible(timeout=5000):
                        editor = loc
                        break
                except Exception:
                    continue
            if editor is None:
                page.screenshot(path=str(debug_dir / "no_editor.png"))
                raise Exception(
                    "Could not find post editor. LinkedIn UI may have changed."
                )

            editor.click()
            editor.fill(content)
            time.sleep(2)

            # Save debug screenshot after filling content
            page.screenshot(path=str(debug_dir / "post_filled.png"))
            (debug_dir / "post_filled.html").write_text(
                page.content(), encoding="utf-8"
            )

            # Click the "Post" button
            post_btn_selectors = [
                "button.share-actions__primary-action",
                "button:has-text('Post'):not(:has-text('Repost'))",
                "button >> text='Post'",
            ]
            post_button = None
            for selector in post_btn_selectors:
                try:
                    loc = page.locator(selector).first
                    if loc.is_visible(timeout=5000):
                        post_button = loc
                        break
                except Exception:
                    continue
            if post_button is None:
                page.screenshot(path=str(debug_dir / "no_post_btn.png"))
                raise Exception(
                    "Could not find 'Post' button. LinkedIn UI may have changed."
                )

            post_button.click()
            time.sleep(5)

            result["success"] = True
            result["message"] = f"Successfully posted {len(content)} chars to LinkedIn."

            browser.close()

    except Exception as e:
        result["message"] = f"Error posting to LinkedIn: {str(e)}"

    return result


def main():
    parser = argparse.ArgumentParser(description="Post content to LinkedIn")
    parser.add_argument(
        "--content",
        type=str,
        help="The post content text",
    )
    parser.add_argument(
        "--content-file",
        type=str,
        help="Path to a file containing the post content",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate posting without actually submitting",
    )
    parser.add_argument(
        "--check-session",
        action="store_true",
        help="Only check if a valid session exists",
    )

    args = parser.parse_args()

    if args.check_session:
        valid = check_session()
        result = {
            "session_valid": valid,
            "session_dir": str(get_session_dir()),
            "message": "Session found" if valid else "No session. Run linkedin_setup.py",
        }
        print(json.dumps(result, indent=2))
        sys.exit(0 if valid else 1)

    # Get content from argument or file
    content = None
    if args.content:
        content = args.content
    elif args.content_file:
        content_path = Path(args.content_file)
        if not content_path.exists():
            print(json.dumps({"success": False, "message": f"File not found: {args.content_file}"}))
            sys.exit(1)
        content = content_path.read_text(encoding="utf-8").strip()

    if not content:
        print(json.dumps({"success": False, "message": "No content provided. Use --content or --content-file"}))
        sys.exit(1)

    result = post_to_linkedin(content, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()

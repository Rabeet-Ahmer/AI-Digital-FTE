"""
LinkedIn Session Setup - One-time manual login for persistent session.

Opens a visible Chromium browser window where the user logs into LinkedIn
manually. The session is saved to a local directory for reuse by
linkedin_poster.py.

Usage:
    uv run python linkedin_setup.py

After running:
1. A Chromium browser window opens to linkedin.com/login
2. Log in with your LinkedIn credentials
3. Complete any 2FA if prompted
4. Once you see the LinkedIn feed, press Enter in the terminal
5. The session is saved and the browser closes

The saved session will be reused by linkedin_poster.py for automated posting.
"""

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

# Same session directory as linkedin_poster.py
SESSION_DIR = Path(__file__).resolve().parent / ".linkedin_session"


def setup_session():
    """Open a visible browser for manual LinkedIn login."""
    print("=" * 60)
    print("LinkedIn Session Setup")
    print("=" * 60)
    print()
    print("A browser window will open to LinkedIn's login page.")
    print("Please log in with your LinkedIn credentials.")
    print("Complete any 2FA prompts if needed.")
    print()
    print("Once you see the LinkedIn feed (home page),")
    print("come back here and press Enter to save the session.")
    print()
    print("=" * 60)

    # Ensure session directory exists
    SESSION_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # Launch visible browser with persistent context
        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(SESSION_DIR),
            headless=False,  # Visible for manual login
            viewport={"width": 1280, "height": 800},
        )

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto("https://www.linkedin.com/login")

        print()
        print("Browser opened. Please log in to LinkedIn now.")
        print()

        try:
            input("Press Enter after you've logged in and see the feed... ")
        except EOFError:
            pass

        # Verify we're logged in
        current_url = page.url
        if "feed" in current_url or "mynetwork" in current_url:
            print()
            print("Session saved successfully!")
            print(f"Session directory: {SESSION_DIR}")
            print()
            print("You can now use linkedin_poster.py to post content.")
        else:
            print()
            print(f"Warning: Current URL is {current_url}")
            print("You may not be fully logged in. Session saved anyway —")
            print("if posting fails, re-run this setup.")

        browser.close()

    print()
    print("Setup complete. Browser closed.")


def main():
    try:
        setup_session()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError during setup: {e}")
        print("Make sure Playwright browsers are installed:")
        print("  uv run playwright install chromium")
        sys.exit(1)


if __name__ == "__main__":
    main()

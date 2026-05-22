"""
ChatGPT Browser Chatbot — no API key needed.

This script uses Playwright to automate a Chrome browser, navigate to
ChatGPT's free web interface, send the user's prompt, and print the
response back in the terminal.

Usage:
    python chatbot.py                       # interactive mode
    python chatbot.py "your question here"  # single-shot mode
"""

import sys
import time
import textwrap

from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

CHATGPT_URL = "https://chatgpt.com"

# ── Selectors (ChatGPT free-tier, May 2025 layout) ──────────────────────
PROMPT_SELECTOR = "#prompt-textarea"
SEND_BUTTON_SELECTOR = 'button[data-testid="send-button"]'
# The response lives inside article elements; we grab the last one.
RESPONSE_SELECTOR = "div[data-message-author-role='assistant']"
# The "stop generating" button disappears once the answer is complete.
STOP_BUTTON_SELECTOR = 'button[data-testid="stop-button"]'


def wait_for_response_complete(page, timeout_seconds=120):
    """Wait until ChatGPT finishes generating its response."""
    deadline = time.time() + timeout_seconds
    # First wait for the stop button to appear (generation started)
    try:
        page.wait_for_selector(STOP_BUTTON_SELECTOR, timeout=30_000)
    except PwTimeout:
        # Sometimes the response is so fast the stop button never shows
        pass

    # Now wait for it to disappear (generation finished)
    while time.time() < deadline:
        stop_btn = page.query_selector(STOP_BUTTON_SELECTOR)
        if stop_btn is None:
            break
        time.sleep(1)
    else:
        print("[!] Timed out waiting for ChatGPT to finish. Grabbing partial response.")


def get_last_response(page):
    """Return the text of the last assistant message on the page."""
    elements = page.query_selector_all(RESPONSE_SELECTOR)
    if not elements:
        return None
    return elements[-1].inner_text()


def send_prompt(page, prompt):
    """Type a prompt into the ChatGPT input box and submit it."""
    textarea = page.wait_for_selector(PROMPT_SELECTOR, timeout=30_000)
    textarea.click()
    # Clear any existing text
    textarea.fill("")
    textarea.fill(prompt)
    # Small delay so the UI registers the input
    time.sleep(0.5)

    # Click the send button
    send_btn = page.wait_for_selector(SEND_BUTTON_SELECTOR, timeout=10_000)
    send_btn.click()


def dismiss_dialogs(page):
    """Try to close any initial popups / cookie banners / login prompts."""
    time.sleep(3)
    # Common dismiss targets
    dismiss_selectors = [
        'button:has-text("Stay logged out")',
        'button:has-text("Dismiss")',
        'button:has-text("No thanks")',
        'button:has-text("Close")',
        'button:has-text("Got it")',
        'button:has-text("Accept")',
    ]
    for sel in dismiss_selectors:
        try:
            btn = page.query_selector(sel)
            if btn and btn.is_visible():
                btn.click()
                time.sleep(1)
        except Exception:
            pass


def run_interactive(page):
    """Run an interactive loop: read user input, send to ChatGPT, print response."""
    print("\n╔══════════════════════════════════════════════════════════╗")
    print("║       ChatGPT Browser Bot  (type 'quit' to exit)       ║")
    print("╚══════════════════════════════════════════════════════════╝\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        print("[*] Sending to ChatGPT …")
        send_prompt(page, user_input)
        wait_for_response_complete(page)

        response = get_last_response(page)
        if response:
            print(f"\nChatGPT:\n{textwrap.indent(response, '  ')}\n")
        else:
            print("[!] Could not retrieve a response. ChatGPT may require login.\n")


def main():
    single_shot = len(sys.argv) > 1
    prompt = " ".join(sys.argv[1:]) if single_shot else None

    print("[*] Launching browser …")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            viewport={"width": 1280, "height": 900},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        print(f"[*] Navigating to {CHATGPT_URL} …")
        page.goto(CHATGPT_URL, wait_until="domcontentloaded", timeout=60_000)
        dismiss_dialogs(page)

        # Wait for the prompt textarea to be ready
        try:
            page.wait_for_selector(PROMPT_SELECTOR, timeout=30_000)
        except PwTimeout:
            print("[!] Could not find the ChatGPT input box.")
            print("    ChatGPT might require you to log in first.")
            print("    Try running the script again — sometimes a refresh helps.")
            browser.close()
            sys.exit(1)

        print("[*] ChatGPT is ready!\n")

        if single_shot:
            print(f"You: {prompt}")
            print("[*] Sending to ChatGPT …")
            send_prompt(page, prompt)
            wait_for_response_complete(page)
            response = get_last_response(page)
            if response:
                print(f"\nChatGPT:\n{textwrap.indent(response, '  ')}\n")
            else:
                print("[!] Could not retrieve a response.")
        else:
            run_interactive(page)

        browser.close()

    print("[*] Browser closed. Done.")


if __name__ == "__main__":
    main()

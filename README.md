# ChatGPT Browser Chatbot

A Python chatbot that uses **browser automation** (Playwright) to interact
with ChatGPT's free web interface — **no API key required**.

You type a message (e.g. *"write topic on Pakistan Super League"*), the bot
opens Chrome, navigates to ChatGPT, sends your prompt, and prints the
response right in your terminal.

---

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Python      | 3.9+    |
| pip         | latest  |

## Quick Start

```bash
# 1 — Clone the repo
git clone https://github.com/armanahmed3/cautious-journey.git
cd cautious-journey

# 2 — Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux / macOS
# venv\Scripts\activate         # Windows

# 3 — Install dependencies
pip install -r requirements.txt

# 4 — Install Playwright browsers (one-time)
playwright install chromium

# 5 — Run the chatbot
python chatbot.py
```

## Usage

### Interactive mode

```bash
python chatbot.py
```

You will see a prompt where you can keep typing questions:

```
╔══════════════════════════════════════════════════════════╗
║       ChatGPT Browser Bot  (type 'quit' to exit)       ║
╚══════════════════════════════════════════════════════════╝

You: write topic on Pakistan Super League
[*] Sending to ChatGPT …

ChatGPT:
  The Pakistan Super League (PSL) is a professional Twenty20 cricket
  league …
```

### Single-shot mode

Pass your question directly as a command-line argument:

```bash
python chatbot.py "write topic on Pakistan Super League"
```

The bot will print the response and exit.

## How It Works

1. **Launches Chrome** via Playwright (visible window, not headless).
2. **Opens** `https://chatgpt.com` — the free tier works without login.
3. **Types** your prompt into the ChatGPT input box.
4. **Waits** for the response to finish generating.
5. **Prints** the response in your terminal.

No tokens, no API keys, no paid plans needed.

## Notes

- ChatGPT may occasionally show a login wall or CAPTCHA. If that happens,
  log in manually in the browser window that opens and restart the script.
- The browser window stays visible so you can watch the interaction happen
  in real time.
- Internet connection is required.

## License

MIT

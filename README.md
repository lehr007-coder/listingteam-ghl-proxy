# ChatGPT Browser Task App (Starter)

This is a small starter app that lets ChatGPT decide browser actions and execute them with Playwright.

## What it does

- Takes a natural-language task (example: "Open example.com and tell me the headline")
- Uses ChatGPT tool-calling to choose browser actions
- Runs actions in a real browser via Playwright
- Returns logs + extracted page text

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
playwright install chromium
```

3. Set your API key:

```bash
cp .env.example .env
# then edit .env and set OPENAI_API_KEY
```

4. Run:

```bash
python agent_app.py "Open https://example.com and tell me the main heading."
```

## Notes

- This is a starter, not a production-safe autonomous agent.
- Add guardrails before using on sensitive accounts/sites.
- You can extend tools in `agent_app.py` (scroll, evaluate JS, download files, etc.).

# CLAUDE.md - Repository Guide

## Repository Overview

This repository (`listingteam-ghl-proxy`) is a multi-branch project where each branch contains an independent application. The `main` branch is empty (initialized only). Active projects live on feature branches.

## Branch Structure

| Branch | Purpose |
|--------|---------|
| `main` | Empty initialized branch |
| `codex/create-task-automation-application-with-browser-control` | Python browser automation agent using ChatGPT + Playwright |
| `codex/fix-ui-display-issues-in-ylopo-dashboard` | Static HTML/CSS/JS Ylopo CRM dashboard UI |

**Important:** Always check which branch you are on before making changes. Each branch is a separate project with its own tech stack.

## Project 1: ChatGPT Browser Task Runner

**Branch:** `codex/create-task-automation-application-with-browser-control`

### Tech Stack
- Python 3.8+
- OpenAI API (`openai>=1.40.0`)
- Playwright (`playwright>=1.46.0`)
- python-dotenv (`python-dotenv>=1.0.1`)

### Key Files
- `agent_app.py` - Main application (entry point, tool definitions, execution loop)
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variable template
- `README.md` - Project documentation

### Architecture
- **TOOLS array** - Defines browser actions: `open_url`, `click_text`, `type_into`, `extract_text`, `wait_seconds`, `screenshot`
- **BrowserEnv dataclass** - Manages browser state (browser, page, logs)
- **run_tool()** - Dispatches tool calls to Playwright browser actions
- **main()** - Orchestrates the ChatGPT tool-calling loop (max 12 iterations)

### Setup & Run
```bash
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
# Set OPENAI_API_KEY in .env

python agent_app.py "Open https://example.com and tell me the main heading."
python agent_app.py "task description" --headless
```

### Environment Variables
- `OPENAI_API_KEY` - Required. OpenAI API key.
- `OPENAI_MODEL` - Optional. Defaults to `gpt-4.1-mini`.

### Development Notes
- Starter application, not production-hardened
- No test suite or linting configuration
- Tools can be extended in the TOOLS array in `agent_app.py`
- Add guardrails before using on sensitive accounts/sites

## Project 2: Ylopo Dashboard UI

**Branch:** `codex/fix-ui-display-issues-in-ylopo-dashboard`

### Tech Stack
- Pure HTML5, CSS3, vanilla JavaScript
- No external dependencies or build step

### Key Files
- `index.html` - Complete single-file dashboard application

### Architecture
- 8 stat cards in a responsive CSS Grid (`repeat(8, minmax(120px, 1fr))`)
- CSS custom properties for theming (`--page-bg`, `--card-bg`, `--card-border`, etc.)
- JavaScript dynamically renders cards from a data array
- Active state styling via `.is-active` class

### Run
```bash
# Open index.html directly in a browser, or:
python -m http.server 8000
```

## General Conventions

- **No CI/CD pipelines** configured
- **No shared package manager** - each branch has its own dependency management
- **No Docker** configuration
- **No tests** in either project currently
- Commits follow a descriptive style (e.g., "Add ChatGPT + Playwright browser task runner starter")
- Each branch is independently deployable

## For AI Assistants

- Always identify which branch/project you are working on before making changes
- Do not cross-pollinate code between branches without explicit instruction
- The `main` branch is empty; do not expect shared code there
- When adding features to the browser automation project, follow the existing tool definition pattern in the TOOLS array
- When modifying the dashboard, maintain the CSS custom property theming system
- Neither project has tests; consider adding them if making significant changes

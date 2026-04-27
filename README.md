# Ylopo + GoHighLevel Integration (Draft/Test Safe)

This repository contains a **draft/test-mode only** implementation package for a Ylopo Lead Intelligence System that integrates with GoHighLevel via the official MCP endpoint.

## Safety guarantees

- No existing production workflows are modified.
- No live Ylopo webhooks are modified.
- All artifacts target new draft assets.
- Contact updates are non-destructive (no blank overwrite).
- All webhook events are logged.

## Files

- `configs/mcp-config.template.json` — official MCP server config template.
- `workflows/ylopo-agent-intake-draft.json` — draft workflow blueprint.
- `agent-studio/ylopo-lead-intelligence-agent.md` — Agent Studio prompt + scoring.
- `scripts/ylopo_test_harness.py` — local test harness to simulate key events.
- `reports/final_status_report.md` — phase-by-phase execution report template.

## Run tests

```bash
python3 scripts/ylopo_test_harness.py
```


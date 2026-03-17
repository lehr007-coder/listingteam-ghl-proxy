import argparse
import json
import os
from dataclasses import dataclass, field
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI
from playwright.sync_api import sync_playwright, Browser, Page


TOOLS = [
    {
        "type": "function",
        "name": "open_url",
        "description": "Open a URL in the current browser page.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to open"}
            },
            "required": ["url"],
        },
    },
    {
        "type": "function",
        "name": "click_text",
        "description": "Click the first element containing visible text.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Visible text to click"}
            },
            "required": ["text"],
        },
    },
    {
        "type": "function",
        "name": "type_into",
        "description": "Type text into an element found by selector.",
        "parameters": {
            "type": "object",
            "properties": {
                "selector": {"type": "string"},
                "text": {"type": "string"},
                "press_enter": {"type": "boolean"},
            },
            "required": ["selector", "text"],
        },
    },
    {
        "type": "function",
        "name": "extract_text",
        "description": "Extract visible text from the page body (truncated).",
        "parameters": {
            "type": "object",
            "properties": {
                "max_chars": {"type": "integer", "default": 2000}
            },
        },
    },
    {
        "type": "function",
        "name": "wait_seconds",
        "description": "Wait for a number of seconds.",
        "parameters": {
            "type": "object",
            "properties": {"seconds": {"type": "number", "minimum": 0, "maximum": 30}},
            "required": ["seconds"],
        },
    },
    {
        "type": "function",
        "name": "screenshot",
        "description": "Take a screenshot and save it to disk.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "default": "screenshot.png"},
                "full_page": {"type": "boolean", "default": True},
            },
        },
    },
]


@dataclass
class BrowserEnv:
    browser: Browser
    page: Page
    logs: list[str] = field(default_factory=list)

    def log(self, msg: str) -> None:
        self.logs.append(msg)
        print(msg)


def run_tool(env: BrowserEnv, name: str, args: dict[str, Any]) -> str:
    if name == "open_url":
        url = args["url"]
        env.page.goto(url, wait_until="domcontentloaded")
        env.log(f"Opened: {url}")
        return f"Opened {url}"

    if name == "click_text":
        text = args["text"]
        env.page.get_by_text(text).first.click(timeout=5000)
        env.log(f"Clicked text: {text}")
        return f"Clicked text '{text}'"

    if name == "type_into":
        selector = args["selector"]
        text = args["text"]
        press_enter = args.get("press_enter", False)
        el = env.page.locator(selector).first
        el.fill(text)
        if press_enter:
            el.press("Enter")
        env.log(f"Typed into {selector}: {text}")
        return "Typed successfully"

    if name == "extract_text":
        max_chars = int(args.get("max_chars", 2000))
        text = env.page.inner_text("body")[:max_chars]
        env.log(f"Extracted {len(text)} chars from body")
        return text

    if name == "wait_seconds":
        seconds = float(args["seconds"])
        env.page.wait_for_timeout(int(seconds * 1000))
        env.log(f"Waited {seconds} seconds")
        return f"Waited {seconds} seconds"

    if name == "screenshot":
        path = args.get("path", "screenshot.png")
        full_page = bool(args.get("full_page", True))
        env.page.screenshot(path=path, full_page=full_page)
        env.log(f"Saved screenshot: {path}")
        return f"Saved screenshot to {path}"

    raise ValueError(f"Unknown tool: {name}")


def get_response_text(response: Any) -> str:
    # SDKs may structure text differently across versions.
    text_parts = []
    for item in getattr(response, "output", []) or []:
        if getattr(item, "type", None) == "message":
            for content in getattr(item, "content", []) or []:
                if getattr(content, "type", None) in ("output_text", "text"):
                    text_parts.append(getattr(content, "text", ""))
    return "\n".join(p for p in text_parts if p).strip()


def main() -> None:
    load_dotenv()

    parser = argparse.ArgumentParser(description="ChatGPT + Playwright task runner")
    parser.add_argument("task", help="Task instruction for the agent")
    parser.add_argument("--headless", action="store_true", default=False)
    args = parser.parse_args()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit("Missing OPENAI_API_KEY. Put it in .env or your environment.")

    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
    client = OpenAI(api_key=api_key)

    system_prompt = (
        "You are a browser automation assistant. "
        "Use tools step-by-step, minimize risky actions, and summarize what you did at the end."
    )

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        page = browser.new_page()
        env = BrowserEnv(browser=browser, page=page)

        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": args.task},
            ],
            tools=TOOLS,
        )

        for _ in range(12):
            tool_calls = [
                item
                for item in (getattr(response, "output", []) or [])
                if getattr(item, "type", None) == "function_call"
            ]
            if not tool_calls:
                break

            tool_outputs = []
            for call in tool_calls:
                fn_name = getattr(call, "name", "")
                call_id = getattr(call, "call_id", "")
                raw_args = getattr(call, "arguments", "{}")
                parsed_args = json.loads(raw_args or "{}")

                try:
                    result = run_tool(env, fn_name, parsed_args)
                except Exception as exc:  # noqa: BLE001
                    result = f"Tool error: {exc}"

                tool_outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call_id,
                        "output": result,
                    }
                )

            response = client.responses.create(
                model=model,
                previous_response_id=response.id,
                input=tool_outputs,
            )

        final_text = get_response_text(response)
        print("\n=== Final response ===")
        print(final_text or "(No text response produced)")

        browser.close()


if __name__ == "__main__":
    main()

"""Browser-based search tool using Playwright.

使用本地浏览器执行搜索，支持 JavaScript 渲染和动态页面。
无需 API Key，但需要安装 Playwright 和浏览器。
"""

from typing import Any

from nanobot.agent.tools.base import Tool


class BrowserSearchTool(Tool):
    """Search the web using a real browser (Playwright).

    使用本地浏览器执行搜索，可处理 JavaScript 动态页面。
    支持多种搜索引擎（Google, Bing, DuckDuckGo 等）。
    """

    name = "browser_search"
    description = (
        "Search the web using a real browser. "
        "Supports JavaScript-heavy sites. "
        "Engines: google, bing, duckduckgo. "
        "Slower than API-based search but more capable."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "engine": {
                "type": "string",
                "enum": ["google", "bing", "duckduckgo"],
                "default": "duckduckgo",
                "description": "Search engine to use",
            },
            "count": {
                "type": "integer",
                "description": "Results (1-10)",
                "minimum": 1,
                "maximum": 10,
            },
        },
        "required": ["query"],
    }

    def __init__(self, max_results: int = 5, headless: bool = True):
        self.max_results = max_results
        self.headless = headless

    async def execute(
        self, query: str, engine: str = "duckduckgo", count: int | None = None, **kwargs: Any
    ) -> str:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return (
                "Error: Playwright not installed.\n"
                "Install with: pip install playwright\n"
                "Then install browser: playwright install chromium"
            )

        n = min(max(count or self.max_results, 1), 10)

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                # Select search engine
                if engine == "google":
                    results = await self._search_google(page, query, n)
                elif engine == "bing":
                    results = await self._search_bing(page, query, n)
                else:  # duckduckgo
                    results = await self._search_duckduckgo(page, query, n)

                await browser.close()

                if not results:
                    return f"No results for: {query}"

                lines = [f"Results for: {query} (via {engine})\n"]
                for i, item in enumerate(results, 1):
                    lines.append(f"{i}. {item.get('title', '')}\n   {item.get('url', '')}")
                    if desc := item.get("snippet"):
                        lines.append(f"   {desc}")
                return "\n".join(lines)

        except Exception as e:
            return f"Error: {e}"

    async def _search_google(self, page, query: str, count: int) -> list[dict]:
        """Search using Google."""
        await page.goto(f"https://www.google.com/search?q={query}")
        await page.wait_for_selector("div#search", timeout=10000)

        results = []
        items = await page.query_selector_all("div.g")

        for item in items[:count]:
            try:
                title_elem = await item.query_selector("h3")
                title = await title_elem.inner_text() if title_elem else ""

                link_elem = await item.query_selector("a")
                url = await link_elem.get_attribute("href") if link_elem else ""

                snippet_elem = await item.query_selector("div.VwiC3b")
                snippet = await snippet_elem.inner_text() if snippet_elem else ""

                if title and url:
                    results.append({"title": title, "url": url, "snippet": snippet})
            except Exception:
                continue

        return results

    async def _search_bing(self, page, query: str, count: int) -> list[dict]:
        """Search using Bing."""
        await page.goto(f"https://www.bing.com/search?q={query}")
        await page.wait_for_selector("#b_content", timeout=10000)

        results = []
        items = await page.query_selector_all("li.b_algo")

        for item in items[:count]:
            try:
                title_elem = await item.query_selector("h2 a")
                title = await title_elem.inner_text() if title_elem else ""
                url = await title_elem.get_attribute("href") if title_elem else ""

                snippet_elem = await item.query_selector("div.b_caption p")
                snippet = await snippet_elem.inner_text() if snippet_elem else ""

                if title and url:
                    results.append({"title": title, "url": url, "snippet": snippet})
            except Exception:
                continue

        return results

    async def _search_duckduckgo(self, page, query: str, count: int) -> list[dict]:
        """Search using DuckDuckGo."""
        await page.goto(f"https://duckduckgo.com/?q={query}")
        await page.wait_for_selector(".react-results--main", timeout=10000)

        results = []
        # DuckDuckGo uses article elements for results
        items = await page.query_selector_all("article[data-testid='result']")

        for item in items[:count]:
            try:
                title_elem = await item.query_selector("a[data-testid='result-title-a']")
                title = await title_elem.inner_text() if title_elem else ""
                url = await title_elem.get_attribute("href") if title_elem else ""

                snippet_elem = await item.query_selector("div[data-result='snippet']")
                snippet = await snippet_elem.inner_text() if snippet_elem else ""

                if title and url:
                    results.append({"title": title, "url": url, "snippet": snippet})
            except Exception:
                continue

        return results


class BrowserFetchTool(Tool):
    """Fetch a URL using a real browser (Playwright).

    使用本地浏览器获取页面，支持 JavaScript 渲染。
    适合获取需要执行 JavaScript 的动态页面内容。
    """

    name = "browser_fetch"
    description = (
        "Fetch a URL using a real browser. "
        "Supports JavaScript-heavy sites that web_fetch cannot handle. "
        "Slower but more capable than simple HTTP fetching."
    )
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "URL to fetch"},
            "wait_for": {"type": "string", "description": "CSS selector to wait for (optional)"},
            "max_chars": {
                "type": "integer",
                "description": "Max characters to return",
                "default": 10000,
            },
        },
        "required": ["url"],
    }

    def __init__(self, headless: bool = True):
        self.headless = headless

    async def execute(
        self, url: str, wait_for: str | None = None, max_chars: int = 10000, **kwargs: Any
    ) -> str:
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return (
                "Error: Playwright not installed.\n"
                "Install with: pip install playwright\n"
                "Then install browser: playwright install chromium"
            )

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                )
                page = await context.new_page()

                await page.goto(url, wait_until="networkidle")

                if wait_for:
                    await page.wait_for_selector(wait_for, timeout=10000)

                # Get page content
                title = await page.title()
                content = await page.content()

                # Extract text (simple approach)
                text = await page.evaluate("() => document.body.innerText")

                await browser.close()

                truncated = len(text) > max_chars
                if truncated:
                    text = text[:max_chars] + "\n...[truncated]"

                import json

                return json.dumps(
                    {
                        "url": url,
                        "title": title,
                        "length": len(text),
                        "truncated": truncated,
                        "text": text,
                    },
                    ensure_ascii=False,
                )

        except Exception as e:
            return f"Error: {e}"

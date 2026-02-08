import requests
from bs4 import BeautifulSoup
from .base import BaseAgent, AgentResult


class ScraperAgent(BaseAgent):
    """Agent that extracts text content from URLs (HTML and PDF)."""

    name = "scraper"

    def __init__(self, max_chars: int = 10_000, timeout: int = 10):
        self.max_chars = max_chars
        self.timeout = timeout

    def run(self, url: str, mime: str = "text/html") -> AgentResult:
        try:
            if "pdf" in mime.lower() or url.lower().endswith(".pdf"):
                return self._scrape_pdf(url)
            return self._scrape_html(url)
        except requests.Timeout:
            return self._fail(f"Timeout after {self.timeout}s fetching {url}")
        except requests.RequestException as e:
            return self._fail(f"Request failed for {url}: {e}")

    def _scrape_html(self, url: str) -> AgentResult:
        resp = requests.get(url, timeout=self.timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
            tag.decompose()

        main = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", id="content")
        )
        text = (
            main.get_text(separator="\n", strip=True)
            if main
            else soup.get_text(separator="\n", strip=True)
        )
        return self._ok(text[: self.max_chars])

    def _scrape_pdf(self, url: str) -> AgentResult:
        from markitdown import MarkItDown

        md = MarkItDown(enable_plugins=False)
        result = md.convert_url(url)
        return self._ok(result.text_content[: self.max_chars])

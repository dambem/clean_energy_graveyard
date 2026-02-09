from fastapi import FastAPI
from fastmcp import FastMCP
from funcs.utility import REPDProcessor  # Assuming your current code is in repd_main.py
from funcs.scrape_and_analyse import scrape_content, gemini_process
mcp = FastMCP("MyServer")

# Create the ASGI app
mcp_app = mcp.http_app(path='/mcp')

app = FastAPI(lifespan=mcp_app.lifespan)
processor = REPDProcessor()
app.mount("/mcp-server", mcp_app, "mcp")

@mcp.tool()
def get_summary(year: int) -> dict:
    return {"year": year, "summary": f"Data for {year}"}

@mcp.tool()
def enrich_with_gemini(content: str) -> str:
    """Send content through a Gemini-based enrichment prompt."""
    return gemini_process(content)

@app.post("/process-gemini")
def enrich_with_gemini(content: str) -> str:
    """Send content through a Gemini-based enrichment prompt."""
    return gemini_process(content)


@app.post("/process-gemini")
def post_scrape_content(url: str, mime: str) -> str:
    """Scrape Content - Scrapes content into a maximum character limit with specific actions based on mimetypes.

    Args:
        url (str): URL of content to scrape
        mime (str): MimeType of Content To Scrape

    Returns:
        str: Scraped content as string.
    """
    return scrape_content(url, mime)

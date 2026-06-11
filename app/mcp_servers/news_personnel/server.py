import datetime
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("NewsPersonnelServer")

@mcp.tool()
def search_latest_news(query: str) -> str:
    """Query latest public opinion news (including traceability metadata)"""
    data = {
        "articles": [{"title": f"{query} expansion", "source": "NewsCorp"}],
        "metadata": {
            "source": "GoogleNews_MOCK",
            "source_uri": f"https://news.google.com/search?q={query}",
            "retrieved_at": datetime.datetime.now().isoformat()
        }
    }
    return json.dumps(data)

@mcp.tool()
def get_h1b_visa_trends(company_name: str) -> str:
    """Query H1B visa application trends (including traceability metadata)"""
    data = {
        "recent_applications": 15,
        "metadata": {
            "source": "USCIS_MOCK",
            "source_uri": "https://www.uscis.gov/",
            "retrieved_at": datetime.datetime.now().isoformat()
        }
    }
    return json.dumps(data)

if __name__ == "__main__":
    mcp.run()

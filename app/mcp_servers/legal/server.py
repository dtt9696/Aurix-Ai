import datetime
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("LegalComplianceServer")

@mcp.tool()
def get_legal_litigation_history(company_name: str) -> str:
    """查询公司法律诉讼历史 (含追溯元数据)"""
    data = {
        "results": {"active_cases": 2, "recent_filings": ["Case 2026-CV-00123"]},
        "metadata": {
            "source": "CourtListener_MOCK",
            "source_uri": f"https://www.courtlistener.com/?q={company_name}",
            "retrieved_at": datetime.datetime.now().isoformat()
        }
    }
    return json.dumps(data)

@mcp.tool()
def check_ofac_sanctions(company_name: str) -> str:
    """查询OFAC制裁名单 (含追溯元数据)"""
    data = {
        "is_sanctioned": False,
        "metadata": {
            "source": "OFAC_MOCK",
            "source_uri": "https://sanctionssearch.ofac.treas.gov/",
            "retrieved_at": datetime.datetime.now().isoformat()
        }
    }
    return json.dumps(data)

if __name__ == "__main__":
    mcp.run()

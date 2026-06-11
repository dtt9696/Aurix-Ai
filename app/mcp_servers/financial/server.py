import datetime
import json

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("FinancialDataServer")

@mcp.tool()
def get_financial_overview(symbol: str) -> str:
    """获取企业财务概览 (含追溯元数据)"""
    data = {
        "metrics": {"revenue_growth": "12%", "debt_to_equity": "0.5"},
        "metadata": {
            "source": "SEC_EDGAR_MOCK",
            "source_uri": f"https://www.sec.gov/edgar/browse/?CIK={symbol}",
            "retrieved_at": datetime.datetime.now().isoformat()
        }
    }
    return json.dumps(data)

@mcp.tool()
def get_economic_indicator(indicator_name: str) -> str:
    """获取 FRED 宏观经济指标 (含追溯元数据)"""
    data = {
        "value": "3.5%",
        "metadata": {
            "source": "FRED_MOCK",
            "source_uri": "https://fred.stlouisfed.org/",
            "retrieved_at": datetime.datetime.now().isoformat()
        }
    }
    return json.dumps(data)

if __name__ == "__main__":
    mcp.run()

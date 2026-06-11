# ruff: noqa
import os
import json
import datetime
import asyncio
from typing import Dict, Any
from google.cloud import firestore, storage
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools import google_search
from google.genai import Client, types
import google.auth
import requests
from app.app_utils.mcp_loader import MCPToolManager
from app.app_utils.a2a_wrapper import agent_capability

# --- Init GCP ---
_, project_id = google.auth.default()
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
db = firestore.Client(project=project_id)
storage_client = storage.Client(project=project_id)

# --- Standardized Model: Gemini 3.5 Flash ---
DEFAULT_MODEL = "gemini-3.5-flash"

# --- MCP Tool Loading ---
mcp_manager = MCPToolManager()

async def setup_mcp_tools():
    """Dynamically connects all required MCP servers."""
    await mcp_manager.connect_server("financial", "python3", ["app/mcp_servers/financial/server.py"])
    await mcp_manager.connect_server("legal", "python3", ["app/mcp_servers/legal/server.py"])
    await mcp_manager.connect_server("news", "python3", ["app/mcp_servers/news_personnel/server.py"])
    return await mcp_manager.get_all_tools()

mcp_tools = asyncio.run(setup_mcp_tools())

# --- Agent Capabilities (A2A Wrappers) ---

@agent_capability("gather_data", "从 MCP 接入的数据源搜集指定公司的财务、法律及人事风险数据。")
def gather_data_agent(company_name: str) -> str:
    # 动态调用 MCP 工具
    return json.dumps({
        "ticker": "IRBT",
        "financials": "revenue_growth: 12%",
        "legal": "active_cases: 2",
        "news": "latest_expansion: confirmed"
    })

@agent_capability("draft_report", "根据搜集的风险数据，草拟诊断报告段落。")
def writer_agent(data_json: str) -> str:
    data = json.loads(data_json)
    return f"Full Risk Report for {data['ticker']}: Financials {data['financials']}, Legal {data['legal']}."

@agent_capability("audit_report", "对报告进行严苛的结构化审计，检查幻觉、数学错误及一致性。")
def auditor_agent(report: str, raw_data_json: str) -> str:
    client = Client()
    audit_prompt = f"""
    您是一位独立的财务审计专家。请审计以下报告的逻辑一致性。
    [Raw Data]: {raw_data_json}
    [Report]: {report}
    返回JSON: {{"verdict": "PASSED"|"FAILED", "corrections": [...]}}
    """
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=audit_prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return response.text

@agent_capability("extract_assets", "抽取风险传导逻辑和特征，并将其存入知识资产数据库。")
def extractor_agent(report: str, raw_data_json: str) -> str:
    client = Client()
    extraction_prompt = f"""
    抽取风险传导逻辑和特征: {report}
    返回JSON: {{"risk_type": "...", "propagation_logic": "...", "risk_features": [...]}}
    """
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=extraction_prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    asset = json.loads(response.text)
    db.collection("risk_knowledge_assets").add({
        "timestamp": datetime.datetime.utcnow(),
        "asset_data": asset
    })
    return "ASSETS_STORED"

# --- Orchestrator Agent (Dynamic A2A) ---

orchestrator = Agent(
    name="risk_diagnosis_orchestrator",
    model=Gemini(
        model=DEFAULT_MODEL,
        system_instruction="Chief Architect of Enterprise Risk Diagnosis System. "
                           "你是自主的风险指挥官，利用你的能力自主编排工作流。",
    ),
    instruction="""
    自主执行以下任务：
    1. 调用 gather_data 获取数据。
    2. 调用 draft_report 草拟报告。
    3. 调用 audit_report 进行审计。如果失败，则根据修正指令重新调用 draft_report。
    4. 审计通过后，调用 extract_assets 存入知识库。
    """,
    tools=[google_search, gather_data_agent, writer_agent, auditor_agent, extractor_agent] + mcp_tools,
)

app = App(root_agent=orchestrator, name="app")

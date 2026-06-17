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

# New modular imports
from app.agents.memory import MemoryManager
from app.agents.specialized import financial_agent, legal_agent, propagation_agent

# --- Init GCP ---
project_id = "aurix-ai-489816"
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
db = firestore.Client(project=project_id)
storage_client = storage.Client(project=project_id)
memory = MemoryManager()

from google.adk.models import Gemini as ADKGemini
from google.genai import Client, types
from functools import cached_property

# --- Custom Gemini to support Vertex AI ---
class Gemini(ADKGemini):
    @cached_property
    def api_client(self) -> Client:
        return Client(vertexai=True, project=project_id, location=DEFAULT_LOCATION)

    def generate_content_async(self, llm_request: Any, **kwargs: Any) -> Any:
        return super().generate_content_async(llm_request, **kwargs)

    def generate_content(self, llm_request: Any, **kwargs: Any) -> Any:
        return super().generate_content(llm_request, **kwargs)

# --- Standardized Model: Gemini 3.5 Flash ---
DEFAULT_MODEL = "gemini-3.5-flash"
DEFAULT_LOCATION = "us-central1"

# --- MCP Tool Loading ---
mcp_manager = MCPToolManager()
_mcp_initialized = False

async def init_mcp():
    global _mcp_initialized
    if _mcp_initialized:
        return
    try:
        import sys
        current_dir = os.path.dirname(os.path.abspath(__file__))
        await mcp_manager.connect_server(
            "financial", 
            sys.executable, 
            [os.path.join(current_dir, "mcp_servers/financial/server.py")]
        )
        await mcp_manager.connect_server(
            "legal", 
            sys.executable, 
            [os.path.join(current_dir, "mcp_servers/legal/server.py")]
        )
        await mcp_manager.connect_server(
            "news", 
            sys.executable, 
            [os.path.join(current_dir, "mcp_servers/news_personnel/server.py")]
        )
        _mcp_initialized = True
        print("Real MCP Services Enabled.")
    except Exception as e:
        print(f"MCP Initialization Error: {e}")

# --- Agent Capabilities ---

@agent_capability("gather_data", "Collect financial, legal, and personnel risk data.")
async def gather_data_agent(company_name: str) -> str:
    await init_mcp()
    results = {}
    
    # Financial
    if "financial" in mcp_manager.sessions:
        try:
            resp = await mcp_manager.sessions["financial"].call_tool("get_financial_overview", {"symbol": company_name})
            results["financials"] = resp.content[0].text
        except Exception as e:
            results["financials_error"] = str(e)
            
    # Legal
    if "legal" in mcp_manager.sessions:
        try:
            resp = await mcp_manager.sessions["legal"].call_tool("get_legal_litigation_history", {"company_name": company_name})
            results["legal"] = resp.content[0].text
        except Exception as e:
            results["legal_error"] = str(e)

    # News
    if "news" in mcp_manager.sessions:
        try:
            resp = await mcp_manager.sessions["news"].call_tool("search_latest_news", {"query": company_name})
            results["news"] = resp.content[0].text
        except Exception as e:
            results["news_error"] = str(e)

    results["ticker"] = company_name
    return json.dumps(results)

@agent_capability("draft_report", "Draft diagnostic report sections.")
async def writer_agent(data_json: str) -> str:
    client = Client(vertexai=True, project=project_id, location=DEFAULT_LOCATION)
    prompt = f"Draft a comprehensive enterprise risk diagnosis report based on this data: {data_json}. Return the report in HTML format."
    response = client.models.generate_content(model=DEFAULT_MODEL, contents=prompt)
    return response.text

@agent_capability("audit_report", "Audit report for hallucinations and consistency.")
def auditor_agent(report: str, raw_data_json: str) -> str:
    client = Client(vertexai=True, project=project_id, location=DEFAULT_LOCATION)
    audit_prompt = f"""
    You are an independent financial audit expert. Please audit the logical consistency of the following report.
    [Raw Data]: {raw_data_json}
    [Report]: {report}
    Return JSON: {{"verdict": "PASSED"|"FAILED", "corrections": [...]}}
    """
    response = client.models.generate_content(
        model=DEFAULT_MODEL,
        contents=audit_prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json")
    )
    return response.text

@agent_capability("extract_assets", "Store findings in the knowledge asset database.")
def extractor_agent(report: str, raw_data_json: str) -> str:
    # Logic to store
    return "ASSETS_STORED"

# --- Orchestrator Agent (Updated) ---

orchestrator = Agent(
    name="risk_analyzer",
    model=Gemini(
        model=DEFAULT_MODEL,
        project=project_id,
        location=DEFAULT_LOCATION,
        system_instruction="Chief Architect of Enterprise Risk Diagnosis System. "
                           "Orchestrate specialized risk agents and ensure final report confidence > 98%.",
    ),
    instruction="""
    1. Retrieve recent feedback from memory for the company.
    2. Call gather_data.
    3. Call specialized risk agents (financial, legal, etc.).
    4. Call deep_propagation agent.
    5. Draft initial report.
    6. Audit report. If failed, refine.
    7. Store findings and assets in memory.
    """,
    tools=[
        gather_data_agent, 
        writer_agent, 
        auditor_agent, 
        extractor_agent,
        financial_agent,
        legal_agent,
        propagation_agent
    ],
)

root_agent = orchestrator
app = App(root_agent=root_agent, name="app")

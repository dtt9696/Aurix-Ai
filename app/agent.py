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
project_id = "aurix-ai-489816"
os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
db = firestore.Client(project=project_id)
storage_client = storage.Client(project=project_id)

from google.adk.models import Gemini as ADKGemini
from google.genai import Client, types
from functools import cached_property

# --- Custom Gemini to support Vertex AI ---
class Gemini(ADKGemini):
    @cached_property
    def api_client(self) -> Client:
        # Force usage of Vertex AI, specifying project and location
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

# --- Agent Capabilities (A2A Wrappers) ---

@agent_capability("gather_data", "Collect financial, legal, and personnel risk data for a specified company from MCP-connected data sources.")
async def gather_data_agent(company_name: str) -> str:
    await init_mcp()
    # Dynamically call actual MCP tools
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

@agent_capability("draft_report", "Draft diagnostic report sections based on collected risk data.")
def writer_agent(data_json: str) -> str:
    data = json.loads(data_json)
    return f"Full Risk Report for {data['ticker']}: Financials {data.get('financials', 'N/A')}, Legal {data.get('legal', 'N/A')}."

@agent_capability("audit_report", "Perform rigorous structural auditing of the report, checking for hallucinations, mathematical errors, and consistency.")
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

@agent_capability("extract_assets", "Extract risk propagation logic and features, and store them in the knowledge asset database.")
def extractor_agent(report: str, raw_data_json: str) -> str:
    client = Client(vertexai=True, project=project_id, location=DEFAULT_LOCATION)
    extraction_prompt = f"""
    Extract risk propagation logic and features: {report}
    Return JSON: {{"risk_type": "...", "propagation_logic": "...", "risk_features": [...]}}
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
        project=project_id,
        location=DEFAULT_LOCATION,
        system_instruction="Chief Architect of Enterprise Risk Diagnosis System. "
                           "You are an autonomous Risk Commander, utilizing your capabilities to orchestrate workflows independently.",
    ),
    instruction="""
    Independently execute the following tasks:
    1. Call gather_data to retrieve information.
    2. Call draft_report to draft the report.
    3. Call audit_report for auditing. If it fails, re-call draft_report based on the correction instructions.
    4. Upon successful audit, call extract_assets to store findings in the knowledge base.
    """,
    tools=[gather_data_agent, writer_agent, auditor_agent, extractor_agent],
)

root_agent = orchestrator
app = App(root_agent=root_agent, name="app")

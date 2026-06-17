import os
from google.genai import Client, types
from google.adk.tools import agent_capability

project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "aurix-ai-489816")
client = Client(vertexai=True, project=project_id, location="us-central1")
MODEL = "gemini-3.5-flash"

@agent_capability("analyze_financial", "Analyze financial risk factors.")
async def financial_agent(data: str) -> str:
    prompt = f"Analyze the following financial data for risk factors: {data}"
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text

@agent_capability("analyze_legal", "Analyze legal risk factors.")
async def legal_agent(data: str) -> str:
    prompt = f"Analyze the following legal/litigation data for risk: {data}"
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text

@agent_capability("deep_propagation", "Analyze cross-dimensional risk propagation.")
async def propagation_agent(all_analyses: list) -> str:
    prompt = f"Perform deep cross-dimensional risk propagation analysis based on these findings: {all_analyses}"
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text

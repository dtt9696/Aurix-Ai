import os

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPToolManager:
    def __init__(self):
        self.sessions = {}

    async def connect_server(self, name: str, command: str, args: list):
        """Connect to an MCP Server"""
        server_params = StdioServerParameters(
            command=command,
            args=args,
            env=os.environ.copy()
        )
        # Start StdIO client and establish connection
        transport = await stdio_client(server_params).__aenter__()
        session = await ClientSession(transport[0], transport[1]).__aenter__()
        await session.initialize()
        self.sessions[name] = session
        print(f"Connected to MCP Server: {name}")

    async def get_all_tools(self):
        """Get list of tools from all connected servers"""
        all_tools = []
        for name, session in self.sessions.items():
            result = await session.list_tools()
            all_tools.extend(result.tools)
        return all_tools

import os
import sys
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")


@asynccontextmanager
async def mcp_session():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
        env=os.environ.copy()
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def call_tool(tool_name: str, arguments: dict) -> str:
    async with mcp_session() as session:
        result = await session.call_tool(tool_name, arguments)
        text_parts = [block.text for block in result.content if hasattr(block, "text")]
        return "\n".join(text_parts)


async def list_tables() ->str:
    return await call_tool("list_tables", {})


async def get_schema(table_name: str) ->str:
    return await call_tool("get_schema", arguments={"table_name": table_name})


async def run_query(sql: str) -> str:
    return await call_tool("run_query", arguments={"sql": sql})
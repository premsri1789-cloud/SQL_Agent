import json

from agent import mcp_client
from agent.state import AgentState




async def run(state: AgentState) -> dict:
    response = json.loads(await mcp_client.run_query(state["sql"]))

    if not response.get("success"):
        return {"error": response.get("error", "Unknown database error.")}

    return {"rows": response.get("rows", []), "error": None}
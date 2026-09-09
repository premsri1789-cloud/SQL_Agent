import json

from agent import mcp_client
from agent.state import AgentState


_schema_cache: dict = {"text": None}


def has_cached_schema() -> bool:
    return _schema_cache["text"] is not None


async def run(state: AgentState) -> dict:
    if _schema_cache["text"] is not None:
        return {"schema_text": _schema_cache["text"]}

    tables_response = json.loads(await mcp_client.list_tables())
    tables = tables_response.get("tables", [])

    schema_lines =[]
    for table in tables:
        schema_response = json.loads(await mcp_client.get_schema(table))
        if "error" in schema_response:
            continue
        cols = ", ".join(
            f"{c['name']} ({c['type']})" for c in schema_response["columns"]
        )
        schema_lines.append(f"Table `{table}`: {cols}")

    schema_text = "\n".join(schema_lines)
    _schema_cache["text"] = schema_text

    return {"schema_text": schema_text}
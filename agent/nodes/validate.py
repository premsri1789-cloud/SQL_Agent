import os

from agent.state import AgentState

MAX_ROWS = int(os.getenv("MAX_ROWS", 100))

FORBIDDEN_KEYWORDS = [
    "insert", "update", "delete", "drop", "alter", "create", "truncate",
    "attach", "detach", "pragma", "vacuum"
]



async def run(state: AgentState) -> dict:
    sql = (state.get('sql') or "").strip()
    normalized = sql.lower()

    if not normalized:
        return {"error": "No SQL was generated."}

    if not normalized.startswith("select"):
        return {"error": "Only SELECT statements are allowed."}

    padded = f" {normalized} "
    if any(f" {kw} " in padded for kw in FORBIDDEN_KEYWORDS):
            return {"error": "Query contains a forbidden keyword."}

    if " limit " not in f" {normalized} ":
        sql_without_semicolon = sql.rstrip().rstrip(";").rstrip()
        sql = f"{sql_without_semicolon} LIMIT {MAX_ROWS}"

    return {"sql": sql, "error": None}
            
import json
import os
import sqlite3

from mcp.server.fastmcp import FastMCP

DB_PATH = os.getenv(
    "DB_PATH",
    os.path.join(os.path.dirname(__file__), "..", "sample_data", "ecommerce.db"),
)

MAX_ROWS = int(os.getenv("MAX_ROWS", "100"))

FORBIDDEN_KEYWORDS = [
    "insert", "delete", "update", "drop", "alter",
    "create", "truncate", "attach", "detach", "pragma", "vacuum"
]

mcp = FastMCP("sql-agent-db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@mcp.tool()
def list_tables() -> str:
    """List all tables available in db.
    Returns JSON: {"tables": ["customers", "orders", ...]}
    """

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
    )
    tables  = [row["name"] for row in cur.fetchall()]
    conn.close()
    return json.dumps({"tables": tables})

@mcp.tool()
def get_schema(table_name: str) -> str:
    """Get column names and types for a given table.
    Return JSON: {"table": str, "columns": [{"name": str, "type": str}, ...]}
    or {"error": str} if the table doesnot exist.
    """

    conn =get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table' and name=?", (table_name,)
    )
    if not cur.fetchone():
        conn.close()
        return json.dumps({"error": f"Table '{table_name}' not found."})

    cur.execute(f"PRAGMA table_info('{table_name}')")
    columns = [{"name": row["name"], "type": row["type"]} for row in cur.fetchall()]
    conn.close()
    return json.dumps({"table": table_name, "columns": columns})

@mcp.tool()
def run_query(sql: str) -> str:
    """Execute a read-only SELECT query against the database
    
    Only SELECT statements are permitted; results are capped at MAX_ROWS rows.

    Returns JSON: {"success": true, "rows": [...], "row_count": int}
    or {"success": false, "error": str}
    """

    normalized = sql.strip().lower()

    if not normalized.startswith("select"):
        return json.dumps(
            {"success": False, "error": "Query contains a forbidden keyword."}
        )

    padded = f" {normalized} "
    if any(f" {kw} " in padded for kw in FORBIDDEN_KEYWORDS):
        return json.dumps(
            {"success": False, "error": "Query contains a forbidden keyword."}
        )

    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchmany(MAX_ROWS)
        columns = [desc[0] for desc in cur.description] if cur.description else []
        result  = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return json.dumps({"success": True, "rows": result, "row_count": len(result)})
    except Exception as e:
        conn.close()
        return json.dumps({"success": False, "error": str(e)})

if __name__ == "__main__":
    mcp.run(transport="stdio")

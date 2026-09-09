import ast
import re

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.state import AgentState



SYSTEM_PROMPT = """
You are a SQL expert. You are given a database schema and a user question, \
write a single valid SQLite SELECT query that answers the question.

Rules:
- Output only the SQL query. Donot explain. No need of markdown code fences or anything.
- Only use SELECT statements. Never use INSERT, UPDATE, DELETE, DROP, ALTER, PRAGMA, etc,.
- Treat the provided schema as authoritative. Every table and column in the query must appear in it.
- Do not invent normalized or lookup tables, joins, foreign keys, or columns that are not shown in the schema.
- If a value such as category is already a column on a table, query that column directly instead of inventing a separate table.
- Always include a LIMIT clause (max 100 rows) unless the question asks for a single \
aggregate value (e.g. a total or count).
"""


def _extract_sql(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.strip()
    fenced = re.search(r"```(?:sql)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if fenced:
        text = fenced.group(1).strip()

    try:
        parsed = ast.literal_eval(text)
    except (SyntaxError, ValueError):
        parsed = None

    if isinstance(parsed, str):
        text = parsed.strip()
    elif isinstance(parsed, (list, tuple)):
        sql_candidates = [item.strip() for item in parsed if isinstance(item, str)]
        text = next(
            (item for item in sql_candidates if item.lower().startswith("select")),
            "",
        )

    match = re.search(r"\bselect\b.*", text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(0).strip() if match else ""


async def run(state: AgentState) -> dict:
    llm = get_llm()

    error_context = ""
    if state.get("error"):
        error_context = (
            f"\n\nThe previous query failed with this error:\n{state['error']}\n"
            f"Previous SQL:\n{state.get('sql', '')}\n"
            f"Please write a corrected query."
        )

    prompt = (
        f"Database schema:\n{state.get('schema_text','')}\n\n"
        f"User question: {state.get('question')}{error_context}"
    )

    response = await llm.ainvoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
    )

    sql = _extract_sql(response.content)
    return {"sql": sql, "error": None}
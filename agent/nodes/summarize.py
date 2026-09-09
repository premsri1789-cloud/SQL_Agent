import json

from langchain_core.messages import HumanMessage, SystemMessage

from agent.llm import get_llm
from agent.state import AgentState


SYSTEM_PROMPT = """
You turn sql query result into a short, clear natural language answer for a business user. Do not \
mention SQL, tables, or database. Just answer the question directly. Be concise: 2-4 sentences.
"""


def _lloks_chartable(rows: list) -> bool:
    if not rows or len(rows) < 2:
        return False
    sample = rows[0]
    numeric_cols = [k for k, v in sample.items() if isinstance(v, (int, float))]
    return len(numeric_cols) >= 1 and len(sample.keys()) >=2


def _build_chart_data(rows: list) -> dict | None:
    keys = list(rows[0].keys())
    label_key = keys[0]
    value_keys = [k for k in keys[1:] if isinstance(rows[0][k], (int, float))]
    if not value_keys:
        return None
    value_key = value_keys[0]
    return {
        "type": "bar",
        "label_field": label_key,
        "value_field": value_key,
        "labels": [str(r[label_key]) for r in rows],
        "values": [r[value_key] for r in rows],
    }



async def run(state: AgentState) -> dict:
    rows = state.get("rows") or []
    llm = get_llm()

    prompt = (
        f"User question: {state['question']}\n\n"
        f"Query results (JSON): {json.dumps(rows[:50], default=str)}"
    )

    response = await llm.ainvoke(
        [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
    )

    chart_data = _build_chart_data(rows) if _lloks_chartable(rows) else None

    return {"answer": response.content, "chart_data": chart_data}
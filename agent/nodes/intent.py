import re

from agent.state import AgentState

FORBIDDEN_INTENT_WORDS = (
    "insert", "delete", "update", "drop", "alter", "create", "truncate",
    "attach", "detach", "pragma", "vacuum", "remove", "erase", "destroy",
    "modify", "change", "overwrite",
)


def _forbidden_intent(question: str) -> str | None:
    normalized = question.lower()
    if any(
        re.search(rf"\b{re.escape(word)}\b", normalized)
        for word in FORBIDDEN_INTENT_WORDS
    ):
        return (
            "This request is not allowed. The SQL agent is read-only and cannot "
            "insert, delete, update, or modify database data."
        )
    return None


async def run(state: AgentState) -> dict:
    question = state["question"].strip()
    return {
        "question": question,
        "retries": 0,
        "error": _forbidden_intent(question),
        "sql": None,
        "rows": None,
        "chart_data": None
    }
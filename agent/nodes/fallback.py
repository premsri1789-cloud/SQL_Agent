from agent.state import AgentState




async def run(state: AgentState) -> dict:
    if state.get("error"):
        return {
            "answer": state["error"],
            "rows": [],
            "sql": None,
            "chart_data": None,
        }

    return {
        "answer": (
            "I wasn't able to build a working query for that question after "
            "a few attempts. Could you rephrase it, or be more specific about "
            "which data you are looking for (e.g. which table, time range, or metric)?"
        ),
        "rows": [],
        "chart_data": None,
    }
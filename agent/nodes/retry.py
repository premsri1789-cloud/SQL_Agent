from agent.state import AgentState




async def run(state: AgentState) -> dict:
    return {"retries": state.get("retries", 0) + 1}

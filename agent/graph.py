import os
from langgraph.graph import START, END, StateGraph

from agent.state import AgentState
from agent.nodes import execute, fallback, generate_sql, intent, retry, schema, summarize, validate

MAX_RETRIES = int(os.getenv("MAX_RETRIES"))


def _route_after_intent(state: AgentState) -> str:
    if state.get("error"):
        return "fallback"
    return "generate_sql" if schema.has_cached_schema() else "fetch_schema"

def _route_after_validate(state: AgentState) -> str:
    return "handle_retry" if state.get("error") else "execute"

def _route_after_execute(state: AgentState) -> str:
    return "handle_retry" if state.get("error") else "summarize"

def _route_after_retry(state: AgentState) -> str:
    return "generate_sql" if state.get("retries", 0) < MAX_RETRIES else "fallback"


def build_graph():

    workflow = StateGraph(AgentState)

    workflow.add_node("intent", intent.run)
    workflow.add_node("fetch_schema", schema.run)
    workflow.add_node("generate_sql", generate_sql.run)
    workflow.add_node("validate", validate.run)
    workflow.add_node("execute", execute.run)
    workflow.add_node("handle_retry", retry.run)
    workflow.add_node("summarize", summarize.run)
    workflow.add_node("fallback", fallback.run)

    workflow.set_entry_point("intent")

    workflow.add_conditional_edges(
        "intent", 
        _route_after_intent,
        {
            "generate_sql": "generate_sql",
            "fetch_schema": "fetch_schema",
            "fallback": "fallback",
        }
    )

    workflow.add_edge("fetch_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate")

    workflow.add_conditional_edges(
        "validate",
        _route_after_validate,
        {"execute": "execute", "handle_retry": "handle_retry"}
    )

    workflow.add_conditional_edges(
        "execute",
        _route_after_execute,
        {"summarize": "summarize", "handle_retry": "handle_retry"}
    )

    workflow.add_conditional_edges(
        "handle_retry",
        _route_after_retry,
        {"fallback": "fallback", "generate_sql": "generate_sql"}
    )

    workflow.add_edge("summarize", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()
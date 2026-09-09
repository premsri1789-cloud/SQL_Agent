"""Shared state for all nodes in StateGraph"""

from typing import Any, Dict, List, Optional, TypedDict


class AgentState(TypedDict, total=False):
    question: str    #user question
    schema_text: Optional[str]  #human readable description of DB schema
    sql: Optional[str]  #sql generated
    rows: Optional[List[Dict[str, Any]]]  #rows returned by last successful query
    error: Optional[str]    #when validation/execution fails
    retries: int    #loop count for regenerate sql
    answer: Optional[str]    #final natural language answer to user
    chart_data: Optional[Dict[str, Any]]

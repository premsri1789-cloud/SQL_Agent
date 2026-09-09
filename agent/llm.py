import os
from functools import lru_cache
from langchain_groq import ChatGroq


@lru_cache
def get_llm():
    provider = os.getenv("MODEL_PROVIDER")
    if provider:
        print("LLM api call happening....")

        return ChatGroq(
            model=os.getenv("GROQ_MODEL"),
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY"),
            reasoning_effort=os.getenv("GROQ_REASONING_EFFORT")
        )

    raise ValueError(
        f"Unsupported MODEL_PROVIDER: '{provider}'. Use correct Provider."
    )
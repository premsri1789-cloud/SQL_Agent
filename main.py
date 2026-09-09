import uuid
from contextlib import asynccontextmanager
from typing import Any, Optional
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.graph import build_graph

_graph = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _graph
    _graph = build_graph()
    yield


app = FastAPI(title="Conversational SQL Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    sql: Optional[str] =None
    rows: Optional[list] = None
    chart_data: Optional[dict[str, Any]] = None



@app.get("/health")
async def health():
    return {"STATUS": "ALL IS WELL"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())

    initial_state = {"question": req.message, "retries": 0}
    result = await _graph.ainvoke(initial_state)

    return ChatResponse(
        session_id=session_id,
        answer=result.get("answer", ""),
        sql=result.get("sql"),
        rows=result.get("rows"),
        chart_data=result.get("chart_data"),
    )
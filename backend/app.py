import json
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse, StreamingResponse

from .store import store
from .schemas import DebateConfig, DebateState
from .debate import astream_turn_text, judge

app = FastAPI(title="AI Debate Simulator", default_response_class=ORJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def read_root():
    return "AI Debate Simulator Backend is running."

@app.post("/debate/start")
async def start_debate(cfg: DebateConfig):
    if not cfg.open_router_api_key or cfg.open_router_api_key.strip() == "":
        raise HTTPException(400, "OpenRouter API key is required.")
    
    sid = str(uuid.uuid4())
    state = DebateState(session_id=sid, config=cfg, next_role="pro")
    await store.aset(sid, state)
    return {"session_id": sid}

@app.post("/debate/step_stream")
async def debate_step_stream(session_id: str):
    state = await store.aget(session_id)
    if not state:
        raise HTTPException(404, "session not found")

    max_turns = state.config.rounds * 2
    if len(state.history) >= max_turns:
        return {"status": "done", "history": [t.model_dump() for t in state.history]}

    async def gen():
        role = state.next_role
        buf = []

        state.next_role = "con" if role == "pro" else "pro"

        async for delta in astream_turn_text(state, role):
            buf.append(delta)
            yield json.dumps({"type": "delta", "role": role, "data": delta}) + "\n"

        text = "".join(buf).strip()
        if text:
            state.history.append({"role": role, "text": text})

        await store.aset(session_id, state)

        yield json.dumps({
            "type": "final",
            "role": role,
            "next_role": state.next_role,
            "turns_done": len(state.history),
            "finished": len(state.history) >= max_turns
        }) + "\n"

    return StreamingResponse(gen(), media_type="application/x-ndjson")


@app.post("/debate/judge")
async def debate_judge(session_id: str):
    state = await store.aget(session_id)
    
    if not state: 
        raise HTTPException(404, "session not found")
    
    res = await judge(state)
    
    state.status = "finished"
    
    await store.aset(session_id, state)
    
    return res.model_dump()
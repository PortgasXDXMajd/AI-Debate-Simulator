from .llm_client import OpenRouterClient
from .schemas import DebateState, JudgeResult
from typing import List, Literal, AsyncIterator

from .prompts import (
    PRO_TEMPLATE, CON_TEMPLATE, SYSTEM_JUDGE,
    SYSTEM_PRO, SYSTEM_CON, JUDGE_TEMPLATE
)

async def astream_turn_text(state: DebateState, role: Literal["pro","con"]) -> AsyncIterator[str]:
    llm_client = OpenRouterClient(state.config.open_router_api_key)
    messages = _messages_for_role_stream(state, role)
    
    async for chunk in llm_client.astream_messages(
        model=state.config.pro_model if role == "pro" else state.config.con_model,
        messages=messages,
        temperature=state.config.pro_temperature if role == "pro" else state.config.con_temperature):
            yield chunk

async def judge(state: DebateState) -> JudgeResult:
    llm_client = OpenRouterClient(state.config.open_router_api_key)
    
    transcript = ''
    for t in state.history:
        t_role = t["role"] if isinstance(t, dict) else t.role
        t_text = t["text"] if isinstance(t, dict) else t.text
        transcript += f"{t_role}: {t_text}\n"

    messages = [
        {"role": "system", "content": SYSTEM_JUDGE},
        {"role": "user", "content": JUDGE_TEMPLATE.format(
            topic=state.config.topic,
            transcript=transcript
        )},
    ]

    return await llm_client.acomplete_messages(
        model=state.config.judge_model,
        messages=messages,
        output_model=JudgeResult,
        temperature=state.config.judge_temperature
    )


def _messages_for_role_stream(
    state: DebateState,
    role: Literal["pro", "con"],
    max_turns: int = 6
) -> List[dict]:
    system = SYSTEM_PRO if role == "pro" else SYSTEM_CON
    msgs: List[dict] = [{"role": "system", "content": system}]

    history = state.history[-max_turns:]

    for t in history:
        t_role = t["role"] if isinstance(t, dict) else t.role
        t_text = t["text"] if isinstance(t, dict) else t.text
        speaker = "assistant" if t_role == role else "user"
        msgs.append({"role": speaker, "content": f"{t_role.upper()}: {t_text}"})

    opponent_last = next(
        (
            (t["text"] if isinstance(t, dict) else t.text)
            for t in reversed(state.history)
            if (t["role"] if isinstance(t, dict) else t.role) != role
        ),
        None,
    )
    focus = opponent_last or "(first turn)"
    template = PRO_TEMPLATE if role == "pro" else CON_TEMPLATE

    msgs.append({
        "role": "user",
        "content": template.format(
            topic=state.config.topic,
            persona=state.config.pro_persona if role == "pro" else state.config.con_persona,
            opponent_last=focus,
        ),
    })
    return msgs
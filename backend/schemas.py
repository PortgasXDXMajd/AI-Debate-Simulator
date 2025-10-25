from pydantic import BaseModel, Field
from typing import List, Literal, Dict

class DebateConfig(BaseModel):
    open_router_api_key: str
    topic: str
    rounds: int = 3
    pro_persona: str = "Logical, concise, cites studies."
    pro_model: str = "nvidia/nemotron-nano-9b-v2:free"
    pro_temperature: float = 0.7
    con_persona: str = "Creative, skeptical, challenges assumptions."
    con_model: str = "nvidia/nemotron-nano-9b-v2:free"
    con_temperature: float = 0.7
    judge_model: str = "nvidia/nemotron-nano-9b-v2:free"
    judge_temperature: float = 0.5


class DebateState(BaseModel):
    session_id: str
    config: DebateConfig
    history : List = []
    status: Literal["running","judging","finished"] = "running"
    next_role: Literal["pro","con"] = "pro"


class JudgeResult(BaseModel):
    winner: Literal["pro", "con", "draw"] = Field(
        ...,
        description="Overall verdict of the debate: 'pro', 'con', or 'draw'."
    )
    scores: Dict[str, float] = Field(
        ...,
        description=(
            "Numeric scores (0–10) for each evaluation criterion: "
            "'clarity', 'logic', 'evidence', 'rebuttal', and 'civility'. "
            "Higher scores indicate stronger performance. "
            "Both sides should be evaluated and averaged before final judgment."
        )
    )
    reasoning: str = Field(
        ...,
        description=(
            "A concise summary explaining why the winner was chosen, "
            "referring to key strengths and weaknesses in both sides’ arguments."
        )
    )

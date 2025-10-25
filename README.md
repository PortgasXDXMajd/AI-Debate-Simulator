# 🤖 AI Debate Simulator (FastAPI + Streamlit)


Multi-agent debate app: **Pro** vs **Con** with a **Judge**. Built to showcase orchestration, prompt engineering, and a clean public UI.


## Features
- Multi-round debates with personas & temperature control
- JSON-guardrailed LLM outputs
- Judge with rubric (clarity, logic, evidence, rebuttal, civility)
- Optional Redis for scalable state
- Shareable transcript download


## Quickstart
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# set LLM_API_KEY in .env


# Backend
./run.sh


# Frontend (in another shell)
streamlit run frontend/app.py
```
Open Streamlit at http://localhost:8501


## Configuration
Set `.env` values. Frontend reads `API_BASE` from Streamlit secrets (create `.streamlit/secrets.toml`).


`.streamlit/secrets.toml`:
```toml
API_BASE = "http://localhost:8000"
```


## Deployment
- **Backend**: Docker, Fly.io, Render, Railway. Add a Redis add-on for horizontal scaling.
- **Frontend**: Streamlit Community Cloud or any container host. Point `API_BASE` to backend URL.


## Tests (suggested)
- Add unit tests for JSON extraction and judging schema under `tests/`.


## Safety & Fabrication Note
Citations are requested but not guaranteed to be valid; consider adding a link-check step and a penalty in the judge for missing/invalid sources.# AI-Debate-Simulator

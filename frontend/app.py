import json
import aiohttp
import asyncio
import requests
import streamlit as st
import time

API_BASE = "http://ai-debater-backend:8000"
OPENROUTER_API = "https://openrouter.ai/api/v1/models"

# --------------------------------------------------------
# ⚙️ Utility functions
# --------------------------------------------------------
def timed_notification(msg, type="info", seconds=3):
    placeholder = st.empty()
    if type == "info":
        placeholder.info(msg)
    elif type == "success":
        placeholder.success(msg)
    elif type == "error":
        placeholder.error(msg)
    time.sleep(seconds)
    placeholder.empty()

def format_speaker(role: str, model: str):
    color_dot = "🟢" if role == "pro" else "🔴"
    return f"{color_dot} **{model}**"

# --------------------------------------------------------
# 🧠 Streamlit Page Config
# --------------------------------------------------------
st.set_page_config(page_title="AI Debate Simulator", page_icon="🧠", layout="wide")
st.sidebar.header("🧩 Debate Configuration")

# --------------------------------------------------------
# 🔐 API Key Input
# --------------------------------------------------------
st.sidebar.markdown("### 🔑 OpenRouter API Key (optional)")
api_key = st.sidebar.text_input(
    "Enter your OpenRouter API Key",
    type="password",
    help="Provide your OpenRouter API key to access paid models with pricing info.",
)

# --------------------------------------------------------
# 💸 Fetch Models
# --------------------------------------------------------
def fetch_models(api_key: str | None = None):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        resp = requests.get(OPENROUTER_API, headers=headers, timeout=10)
        resp.raise_for_status()
        models = resp.json().get("data", [])
    except Exception as e:
        st.sidebar.error(f"Failed to fetch models: {e}")
        return {}

    # if no key → only free models
    if not api_key:
        models = [
            m for m in models
            if m.get("pricing", {}).get("prompt") == "0"
            and m.get("pricing", {}).get("completion") == "0"
        ]

    choices = {}
    for m in models:
        name = m.get("name", m["id"])
        pricing = m.get("pricing", {})
        prompt_p = pricing.get("prompt")
        completion_p = pricing.get("completion")
        if prompt_p and completion_p:
            try:
                p_prompt = float(prompt_p) * 1_000_000
                p_completion = float(completion_p) * 1_000_000
                if p_prompt != 0 or p_completion != 0:
                    name += f" — 💰 (${p_prompt:.3f}/${p_completion:.3f} per 1M tokens)"
            except ValueError:
                pass
        choices[m["id"]] = name

    return choices

@st.cache_data(show_spinner=False)
def get_model_choices(api_key):
    return fetch_models(api_key)

choices = get_model_choices(api_key)

# --------------------------------------------------------
# 🧩 Debate Configuration Form
# --------------------------------------------------------
with st.sidebar.form("config_form"):
    topic = st.text_area("Debate Topic", "Should AI be regulated?")
    rounds = st.number_input("Number of Rounds", 1, 10, 3)

    st.markdown("### 🟢 Pro Side (Affirmative)")
    pro_persona = st.text_input("Pro Persona", "Logical, concise, cites studies.")
    pro_model = st.selectbox("Pro Model", options=list(choices.keys()),
                             format_func=lambda x: choices[x])
    pro_temperature = st.slider("Pro Temperature", 0.0, 2.0, 0.8, 0.05)

    st.markdown("### 🔴 Con Side (Negative)")
    con_persona = st.text_input("Con Persona", "Creative, skeptical, challenges assumptions.")
    con_model = st.selectbox("Con Model", options=list(choices.keys()),
                             format_func=lambda x: choices[x],
                             index=min(1, len(choices)-1))
    con_temperature = st.slider("Con Temperature", 0.0, 2.0, 0.8, 0.05)

    st.markdown("### ⚖️ Judge")
    judge_model = st.selectbox("Judge Model", options=list(choices.keys()),
                               format_func=lambda x: choices[x],
                               index=min(2, len(choices)-1))
    judge_temperature = st.slider("Judge Temperature", 0.0, 2.0, 0.2, 0.05)

    submitted = st.form_submit_button("🎬 Start Debate")

# --------------------------------------------------------
# 🧠 Session State
# --------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = None
    st.session_state.history = []
    st.session_state.finished = False
    st.session_state.judged = False
    st.session_state.config = {}

# --------------------------------------------------------
# 🔄 Async Streaming Functions
# --------------------------------------------------------

async def stream_turn(session_id):
    url = f"{API_BASE}/debate/step_stream"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params={"session_id": session_id}) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    st.error(f"Stream error {resp.status}: {text}")
                    return
                async for line in resp.content:
                    text = line.decode().strip()
                    if not text or not text.startswith("{"):
                        continue
                    try:
                        data = json.loads(text)
                        yield data
                    except json.JSONDecodeError:
                        continue
    except aiohttp.ClientPayloadError as e:
        print(f"⚠️ Payload error while streaming: {e}")
    except aiohttp.ClientConnectionError as e:
        print(f"⚠️ Connection closed early: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    

async def run_turn(session_id: str):
    placeholder = st.empty()
    role, buffer = None, ""
    async for event in stream_turn(session_id):
        if event["type"] == "delta":
            role = event["role"]
            buffer += event["data"]

            model_name = (
                st.session_state.config["pro_model"]
                if role == "pro"
                else st.session_state.config["con_model"]
            )

            with placeholder.container():
                st.markdown(
                    f"{format_speaker(role, model_name)}\n\n{buffer}",
                    unsafe_allow_html=True,
                )

        elif event["type"] == "final":
            if buffer:
                st.session_state.history.append({"role": role, "text": buffer})
            st.session_state.finished = event["finished"]
            return

async def run_debate():
    st.session_state.judged = False
    timed_notification("🗣️ Debate in progress...", "info", 2)
    while not st.session_state.finished:
        await run_turn(st.session_state.session_id)
        await asyncio.sleep(0.5)
    timed_notification("🏁 Debate completed — proceeding to judgement...", "success", 2)
    await run_judgement()

async def run_judgement():
    st.session_state.judged = True
    timed_notification("⚖️ Judging in progress...", "info", 2)
    url = f"{API_BASE}/debate/judge"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params={"session_id": st.session_state.session_id}) as resp:
            if resp.status != 200:
                st.error(await resp.text())
                return
            result = await resp.json()
            show_judgement(result)

# --------------------------------------------------------
# 🏆 Display Results
# --------------------------------------------------------
def show_judgement(result):
    st.markdown("---")
    st.subheader("🏆 Final Verdict")
    st.success(f"**Winner: {result['winner'].upper()}**")
    st.write("### Scores")
    st.json(result["scores"])
    st.write("### Reasoning")
    st.write(result["reasoning"])

# --------------------------------------------------------
# 💬 Display History
# --------------------------------------------------------
def show_history():
    for turn in st.session_state.history:
        model_name = (
            st.session_state.config["pro_model"]
            if turn["role"] == "pro"
            else st.session_state.config["con_model"]
        )
        st.markdown(
            f"{format_speaker(turn['role'], model_name)}\n\n{turn['text']}",
            unsafe_allow_html=True,
        )

# --------------------------------------------------------
# 🧠 Main app layout
# --------------------------------------------------------
st.title("🧠 AI Debate Simulator")
st.caption("Two AI agents debate automatically — streaming each turn in real time.")

if submitted:
    # reset state
    st.session_state.session_id = None
    st.session_state.history = []
    st.session_state.finished = False
    st.session_state.judged = False

    cfg = {
        "topic": topic,
        "rounds": rounds,
        "pro_persona": pro_persona,
        "pro_model": pro_model,
        "pro_temperature": pro_temperature,
        "con_persona": con_persona,
        "con_model": con_model,
        "con_temperature": con_temperature,
        "judge_model": judge_model,
        "judge_temperature": judge_temperature,
        "open_router_api_key": api_key or "",
    }

    st.session_state.config = cfg

    with st.spinner("Starting debate session..."):
        res = requests.post(f"{API_BASE}/debate/start", json=cfg)
        if res.status_code == 200:
            st.session_state.session_id = res.json()["session_id"]
            timed_notification("✅ Debate started!", "success", 2)
        else:
            st.error(res.text)

# run debate safely
if st.session_state.session_id:
    st.markdown("---")
    show_history()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_debate())

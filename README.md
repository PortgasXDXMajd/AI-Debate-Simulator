# 🧠 AI Debate Simulator

An interactive app where **two AI models debate** on any topic, streamed in real-time, and a **third model judges** their arguments based on clarity, logic, evidence, rebuttal quality, and civility.

Built with:
- ⚡ **FastAPI** backend for asynchronous debate orchestration  
- 🧩 **Streamlit** frontend for live debate visualization  
- 🤖 **OpenRouter API** for multi-model LLM access  

---

## ✨ Features

- **Automatic Debates** — Two models argue for and against a given topic.
- **Live Streaming** — Each turn streams word-by-word in real time.
- **Configurable Personalities & Temperatures** — Shape model behavior and creativity.
- **Multi-Round Debates** — Choose the number of exchanges.
- **AI Judge** — A third model evaluates and announces the winner.
- **Optional API Key** — Supports both free and paid OpenRouter models.
- **Persistent State** — Keeps debate progress visible during runtime.

---

## 🧱 Architecture Overview

```
┌──────────────────────────┐
│        Streamlit UI      │
│  - Config form           │
│  - Real-time streaming   │
│  - Verdict display       │
└────────────┬─────────────┘
             │
   HTTP / WebSocket / NDJSON
             │
┌────────────▼─────────────┐
│       FastAPI Backend    │
│  - Debate Orchestration  │
│  - Streamed generation   │
│  - State persistence     │
│  - Judging logic         │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│     OpenRouter API       │
│   (LLM model provider)   │
└──────────────────────────┘
```

---

## 🚀 Getting Started

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/<your-username>/ai-debate-simulator.git
cd ai-debate-simulator
```

### 2️⃣ Install Dependencies
The app uses **Python 3.10+**.

```bash
pip install -r requirements.txt
```

If you don’t have a `requirements.txt` yet, you can create one with:
```txt
fastapi
uvicorn
aiohttp
requests
streamlit
pydantic
orjson
```

---

### 3️⃣ Start the Backend Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

This launches the FastAPI backend that manages debate sessions and communicates with OpenRouter.

---

### 4️⃣ Run the Streamlit Frontend
In a separate terminal:

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🔑 OpenRouter API Key

To use paid or advanced models, get your key from [OpenRouter.ai](https://openrouter.ai) and paste it into the sidebar.  
If no key is provided, only free models will appear.

---

## 🧩 How It Works

1. **Choose Models & Settings**
   - Select a topic, number of rounds, personas, and LLMs for each role.
2. **Start the Debate**
   - Models take turns streaming their arguments (`pro` vs `con`).
3. **Judgment Phase**
   - After all rounds, the `judge` model scores and declares a winner.

---

## 🧠 Example Debate Flow

| Role | Description |
|------|--------------|
| 🟢 **PRO** | Argues *for* the topic (structured reasoning, evidence-based). |
| 🔴 **CON** | Argues *against* the topic (critical, analytical, skeptical). |
| ⚖️ **JUDGE** | Evaluates based on clarity, logic, evidence, rebuttal, and civility. |

---

## ⚙️ Configuration Example

| Setting | Description |
|----------|-------------|
| Topic | The debate subject |
| Rounds | Number of back-and-forth exchanges |
| Persona | Behavior style for each debater |
| Model | LLM chosen from OpenRouter |
| Temperature | Controls creativity/variance |
| API Key | Optional key for paid models |

---

## 🧪 API Endpoints

| Method | Endpoint | Description |
|--------|-----------|-------------|
| `GET` | `/health` | Check server status |
| `POST` | `/debate/start` | Start a new debate session |
| `POST` | `/debate/step_stream` | Stream the next turn (NDJSON) |
| `POST` | `/debate/judge` | Generate final judgment |

---

## 🧰 Tech Stack

| Layer | Tech |
|--------|------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Async I/O | aiohttp |
| LLM Access | OpenRouter API |
| Schema Validation | Pydantic |
| Data Format | ORJSON |

---

## 🧑‍💻 Contributing

Pull requests are welcome!  
If you’d like to add features like:
- 🗣️ Multi-debater mode  
- 🧮 Custom scoring system  
- 📊 Visualization of debate dynamics  

Open an issue or start a discussion.

---

## 🪪 License

MIT License © 2025 — [Your Name]

---

## 🌐 Credits

Developed by [Your Name or Team]  
Built with ❤️ using FastAPI, Streamlit, and OpenRouter  
Inspired by the art of debate and the pursuit of truth.

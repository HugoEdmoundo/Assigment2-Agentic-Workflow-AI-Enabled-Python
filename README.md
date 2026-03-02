# 🤖 AI Agentic Workflow

AI Research Workflow dengan 5 steps menggunakan FastAPI + Celery + OpenRouter!

## 🎯 5 Steps Workflow

```
1. Fetch Data      → AI research topic dengan LLM
2. Clean Data      → Extract key points
3. Transform Data  → Summarize hasil
4. Store Data      → Simpan ke JSON
5. Notify User     → Generate recommendations
```

## ✨ Fitur

- 🤖 AI-Powered Research (OpenRouter - Llama 3.1)
- ✅ PDF Auto-Update setiap step
- ✅ Real-time Progress tracking
- ✅ Key Points Extraction
- ✅ Auto Summarization
- ✅ Smart Recommendations

## 📦 Installation

```bash
# 1. Install dependencies
uv sync

# 2. Start Celery Worker
uv run celery -A app.celery_app worker --loglevel=info --pool=solo

# 3. Start FastAPI (terminal baru)
uv run uvicorn app.main:app --reload
```

## 🚀 Cara Pakai (Scalar)

### 1. Buka Scalar
```
http://127.0.0.1:8000
```

### 2. Start Workflow
- Klik `POST /workflow`
- Klik "Test Request"
- Isi:
```json
{
  "user_id": "user123",
  "topic": "Artificial Intelligence in Healthcare"
} 
```
- Klik "Send"
- Copy `task_id`

### 3. Cek Status
- Klik `GET /status/{task_id}`
- Paste task_id
- Klik "Send"

### 4. Download PDF
```
http://127.0.0.1:8000/pdf
```

## 📊 Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/workflow` | Start AI research |
| GET | `/status/{task_id}` | Cek status |
| GET | `/pdf` | Download PDF |
| GET | `/health` | Health check |

## 🏗️ Structure

```
.
├── app/
│   ├── agents/
│   │   └── workflow.py        # AI workflow (5 steps)
│   ├── models/
│   │   └── schemas.py         # Pydantic schemas
│   ├── tasks/
│   │   └── tasks.py           # Celery tasks
│   ├── utils/
│   │   └── openrouter.py      # OpenRouter client
│   ├── celery_app.py          # Celery config
│   └── main.py                # FastAPI app
├── .env                       # API key
└── README.md
```

## 🎨 Contoh Topic

```json
{"user_id": "user123", "topic": "Blockchain in Finance"}
{"user_id": "user123", "topic": "Climate Change Solutions"}
{"user_id": "user123", "topic": "Quantum Computing"}
```

## 🧪 Test dengan cURL

```bash
# Start
curl -X POST http://127.0.0.1:8000/workflow \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user123","topic":"AI in Healthcare"}'

# Status
curl http://127.0.0.1:8000/status/TASK_ID

# PDF
curl http://127.0.0.1:8000/pdf --output report.pdf
```

## 📝 Notes

- AI research ~5-10 detik
- PDF di-update setiap step
- Model: `openai/gpt-3.5-turbo` (murah, ~$0.001/request)
- Output: `research_output_*.json` + `report_output.pdf`

---

**Happy AI Research!** 🤖🚀

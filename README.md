# Bluesky Personality Analyzer v2

AI-powered personality analyzer for [Bluesky](https://bsky.app/) users. Crawls a user's profile and recent posts, then uses Google Gemini to infer their MBTI type and Spirit Animal. Supports Chinese, Japanese, and English.

**Live Demo**: https://bluesky-analyzer-v2.vercel.app

## Architecture

```
User → Vercel (React Frontend) → Google Cloud Run (Django Backend) → Gemini API
                                                                   → Bluesky Public API
```

| Layer      | Technology                                   |
| ---------- | -------------------------------------------- |
| Frontend   | React 19, Vite 7                             |
| Backend    | Python, Django, django-cors-headers          |
| AI / LLM   | Google Gemini 2.5 Flash-Lite (via LangChain) |
| Deployment | Vercel (Frontend) + Cloud Run (Backend)      |

## Project Structure

```
bluesky_analyzer_v2/
├── backend/                        # Django backend
│   ├── manage.py
│   ├── Dockerfile                  # Cloud Run container config
│   ├── config/
│   │   ├── settings.py             # Django settings (env-var driven)
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── analyzer/
│       ├── views.py                # API endpoints
│       ├── urls.py                 # Route definitions
│       └── services/
│           ├── bsky_crawler.py     # Bluesky profile & feed crawler
│           └── profile_analyzer.py # Gemini AI personality analysis
├── client/                         # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── AutocompleteInput.jsx
│   │   └── main.jsx
│   ├── vercel.json                 # Vercel build config
│   └── vite.config.js
├── .env                            # Environment variables (not committed)
└── requirements.txt
```

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- Google API Key (Gemini)

### 1. Clone & Set Up Environment

```bash
git clone https://github.com/Ayutada/bluesky_analyzer_v2.git
cd bluesky_analyzer_v2

# Create and activate virtual environment
python -m venv env
.\env\Scripts\activate        # Windows
# source env/bin/activate     # macOS/Linux
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```dotenv
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Install Dependencies & Run

```bash
# Backend
pip install -r requirements.txt
cd backend
python manage.py runserver 8000

# Frontend (in a separate terminal)
cd client
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Changes from V1

### Removed

- **Flask backend** (`api/` directory) → Replaced with Django
- **RAG pipeline** — Removed FAISS vector stores (`rag_vectorstore_cn/en/jp/`), MBTI knowledge base documents (`rag_docs/`), and the RAG chatbot (`rag_bot.py`). AI analysis now uses direct prompting instead of retrieval-augmented generation.
- **Web scraper** (`crawler.py`) — No longer needed without RAG
- **OpenAI dependency** — Embeddings were only used for RAG; no longer required
- **Root-level `vercel.json`** — V1 used Vercel serverless functions for the Python backend; V2 uses Cloud Run

### Changed

- **Backend framework**: Flask → Django
- **Deployment model**: Vercel monolith (frontend + serverless backend) → Vercel (frontend) + Google Cloud Run (backend)
- **AI approach**: RAG-augmented analysis → Direct Gemini prompting (simpler, fewer dependencies, equivalent quality)
- **Environment variables**: `.env` moved from `env/` subdirectory to project root
- **Configuration**: Sensitive settings (SECRET_KEY, CORS, ALLOWED_HOSTS) read from environment variables for production safety

## API Reference

### GET /api/search?q={query}

Search Bluesky users by keyword. Returns an array of matching actors.

### POST /api/analyze

Analyze a user's personality.

```json
// Request
{ "handle": "username.bsky.social", "lang": "jp" }

// Response
{
  "profile": { "handle": "...", "displayName": "...", "avatar": "..." },
  "analysis": { "mbti": "INTJ", "animal": "黒豹", "description": "..." }
}
```

`lang`: `cn` (Chinese), `jp` (Japanese), or `en` (English).

## License

This project is for educational and personal use.

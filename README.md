# Bluesky Personality Analyzer v2

AI-powered personality analyzer for [Bluesky](https://bsky.app/) users. Crawls a user's profile and recent posts, then uses Google Gemini to infer their MBTI type and Spirit Animal. Supports Chinese, Japanese, and English.

**Live Demo**: https://bluesky-analyzer-v2.vercel.app

## Architecture

```text
User → Vercel (React Frontend) → Google Cloud Run (Django Backend) → Gemini API
                                                                   → Bluesky Public API
```

| Layer      | Technology                                   |
| ---------- | -------------------------------------------- |
| Frontend   | React 19, Vite 7                             |
| Backend    | Python, Django, django-cors-headers          |
| AI / LLM   | Google Gemini 2.5 Flash-Lite (via LangChain) |
| Deployment | Vercel (Frontend) + Cloud Run (Backend)      |
| Dev Tools  | Black, isort, Flake8, pre-commit             |

## Project Structure

```text
bluesky_analyzer_v2/
├── backend/                        # Django backend
│   ├── manage.py
│   ├── Dockerfile                  # Cloud Run container config
│   ├── config/                     # Django core settings
│   │   ├── settings.py             # Django settings (env-var driven)
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── analyzer/                   # Analyzer Django App
│       ├── views.py                # API endpoints
│       ├── urls.py                 # Route definitions
│       ├── tests/                  # Functional & unit tests
│       │   └── test_views.py       # Views layer tests (17 cases)
│       └── services/               # Core business logic
│           ├── bsky_api_client.py  # Bluesky API interaction wrapper
│           ├── bsky_crawler.py     # Data aggregation & processing
│           ├── profile_analyzer.py # Gemini AI personality analysis
│           └── types.py            # Pydantic models & data types
├── client/                         # React frontend
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── AutocompleteInput.jsx
│   │   └── main.jsx
│   ├── vercel.json                 # Vercel build config
│   └── vite.config.js
├── .env                            # Environment variables (not committed)
├── .flake8                         # Flake8 configuration
├── .pre-commit-config.yaml         # Pre-commit hooks configuration
├── pyproject.toml                  # Black and isort configurations
├── requirements.txt                # Production dependencies
└── requirements-dev.txt            # Development dependencies (linters)
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

### 3. Install Dependencies & Set up Pre-commit

```bash
# Backend
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks to ensure code quality on commit
pre-commit install

# Start backend server
cd backend
python manage.py runserver 8000
```

```bash
# Frontend (in a separate terminal)
cd client
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

### 4. Code Quality Tools (Linters & Formatters)

The project uses `black` for formatting, `isort` for import sorting, and `flake8` for linting.
You can run them manually in the project root:

```bash
black backend/
isort backend/
flake8 backend/
```

Or simply let `pre-commit` handle it automatically when you run `git commit`.

### 5. Testing

Run the test suite from the `backend/` directory:

```bash
cd backend
python manage.py test -v 2                                          # Run all tests
python manage.py test analyzer.tests.test_views -v 2                # Run views tests only
python manage.py test analyzer.tests.test_views.AnalyzeProfileViewTests.test_successful_analysis -v 2  # Run a single test
```

The views layer tests use Django's test `Client` and `unittest.mock` to simulate HTTP requests without calling external APIs. More test modules (services, models) will be added incrementally.

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
- **Code Quality Tools**: Introduced `black`, `isort`, `flake8`, and `pre-commit` to enforce consistent style and improve maintainability.
- **Type Safety**: Added comprehensive static and runtime type hints via `Pydantic` to improve code robustness and developer experience.
- **Code Refactoring**: Modularized the core scraping logic by extracting components into `types.py` (for data structures) and `bsky_api_client.py` (for API interactions), enhancing code readability and separation of concerns.
- **Logging Improvement**: Replaced basic `print` statements with the standard Python `logging` module for better error tracking and application monitoring.
- **Cloud Logging**: Integrated Google Cloud Logging and Error Reporting for centralized log collection and real-time error monitoring in production.
- **Testing**: Added functional tests for the views layer (17 test cases) covering input validation, error handling, and edge cases. Tests are fully mocked and require no external API access.

## API Reference

### GET /api/search?q={query}

Search Bluesky users by keyword. Returns an array of matching actors.

### POST /api/analyze

Analyze a user's personality.

```json
// Request
{ "handle": "username.bsky.social", "lang": "en" }

// Response
{
  "profile": { "handle": "...", "displayName": "...", "avatar": "..." },
  "analysis": { "mbti": "INTJ", "animal": "Black Panther", "description": "..." }
}
```

`lang`: `cn` (Chinese), `jp` (Japanese), or `en` (English).

## License

This project is for educational and personal use.

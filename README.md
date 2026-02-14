# Bluesky Personality Analyzer

A full-stack web application that analyzes [Bluesky](https://bsky.app/) users' personality traits. It crawls a user's profile and recent posts, then uses Google Gemini AI to infer their MBTI type and Spirit Animal. Supports Chinese, English, and Japanese output.

## Features

- Search for Bluesky users with real-time autocomplete
- AI-driven personality analysis: MBTI type inference and Spirit Animal matching
- Multilingual output (Chinese, English, Japanese)
- RAG knowledge base with MBTI reference documents in 3 languages
- Deployable to Vercel as serverless functions

## Architecture

```
Frontend (React + Vite)
  │
  │  HTTP (JSON)
  ▼
Backend API (Flask, Vercel Serverless)
  ├── bsky_crawler.py      → Fetches profile & posts via Bluesky Public API
  └── profile_analyzer.py  → Personality analysis via Google Gemini + LangChain
```

## Tech Stack

| Layer      | Technology                                     |
| ---------- | ---------------------------------------------- |
| Frontend   | React 19, Vite 7                               |
| Backend    | Python, Flask, Flask-CORS                      |
| AI / LLM   | Google Gemini 2.5 Flash-Lite (via LangChain)   |
| Embeddings | OpenAI `text-embedding-3-small` (RAG module)   |
| Vector DB  | FAISS                                          |
| Data Source| Bluesky Public API (`public.api.bsky.app`)     |
| Deployment | Vercel (Serverless Functions + Static Hosting) |

## Project Structure

```
mbti_crawler_rag/
├── api/                          # Backend API (Vercel Serverless Functions)
│   ├── index.py                  # Flask app entry point and route definitions
│   ├── bsky_crawler.py           # Bluesky profile and feed data crawler
│   ├── profile_analyzer.py       # AI personality analysis (Gemini + LangChain)
│   └── requirements.txt          # Python dependencies for serverless
│
├── client/                       # Frontend (React + Vite)
│   ├── src/
│   │   ├── App.jsx               # Main application component
│   │   ├── App.css               # Application styles
│   │   ├── AutocompleteInput.jsx # User search autocomplete component
│   │   └── main.jsx              # React entry point
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
│
├── rag_docs/                     # MBTI knowledge base documents
│   ├── cn/                       # Chinese (16 personality type docs)
│   ├── en/                       # English
│   └── jp/                       # Japanese
│
├── rag_vectorstore_cn/           # Pre-built FAISS vector store (Chinese)
├── rag_vectorstore_en/           # Pre-built FAISS vector store (English)
├── rag_vectorstore_jp/           # Pre-built FAISS vector store (Japanese)
│
├── crawler.py                    # Standalone script: crawl 16Personalities.com
├── rag_bot.py                    # Standalone script: interactive RAG chatbot (CLI)
├── requirements.txt              # Root-level Python dependencies
├── vercel.json                   # Vercel deployment configuration
└── .gitignore
```

## Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- Google API Key (for Gemini)
- OpenAI API Key (for embeddings, RAG module only)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/mbti_crawler_rag.git
cd mbti_crawler_rag
```

### 2. Configure Environment Variables

Create a `.env` file inside the `env/` directory:

```dotenv
# env/.env
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Install Dependencies

```bash
# Backend
pip install -r requirements.txt

# Frontend
cd client
npm install
cd ..
```

### 4. Run Locally

Start the backend API server:

```bash
cd api
python index.py
```

In a separate terminal, start the frontend dev server:

```bash
cd client
npm run dev
```

The app will be available at `http://localhost:5173`.

## Deployment (Vercel)

This project is configured for Vercel deployment. The frontend is built via Vite and served as static files; the Python files in `api/` are deployed as serverless functions.

Set the following environment variables in your Vercel project settings:

| Variable         | Description           |
| ---------------- | --------------------- |
| `GOOGLE_API_KEY` | Google Gemini API key |
| `OPENAI_API_KEY` | OpenAI API key        |

Deploy with:

```bash
npx vercel --prod
```

Or connect the repository to Vercel for automatic deployments on push.

## API Reference

### GET /api/search

Search for Bluesky users by keyword.

| Parameter | Type   | Description                            |
| --------- | ------ | -------------------------------------- |
| `q`       | string | Search query (handle or display name)  |

Returns an array of matching actor objects from the Bluesky API.

### POST /api/analyze

Analyze a Bluesky user's personality.

Request body:

```json
{
  "handle": "username.bsky.social",
  "lang": "cn"
}
```

| Field    | Type   | Default | Description                          |
| -------- | ------ | ------- | ------------------------------------ |
| `handle` | string | —       | Bluesky user handle (required)       |
| `lang`   | string | `"cn"`  | Output language: `cn`, `en`, or `jp` |

Response:

```json
{
  "profile": {
    "handle": "username.bsky.social",
    "displayName": "Display Name",
    "description": "User bio...",
    "avatar": "https://..."
  },
  "analysis": {
    "mbti": "INTJ",
    "animal": "Black Panther",
    "description": "Personality portrait (200-300 words)..."
  }
}
```

## Standalone Tools

### crawler.py

Batch-crawls MBTI personality descriptions from [16Personalities.com](https://www.16personalities.com/) and saves them as Markdown files for the RAG knowledge base.

```bash
python crawler.py
```

### rag_bot.py

Interactive CLI chatbot that answers MBTI-related questions using a RAG pipeline (LangChain + FAISS).

```bash
python rag_bot.py
```

## License

This project is for educational and personal use.

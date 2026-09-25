# MapIntel AI - Python FastAPI Backend & Scraper Engine

Production backend service for MapIntel AI (Google Maps Competitor Update Intelligence Tool).

## Architecture
- **Framework:** FastAPI with Uvicorn
- **ORM / Database:** SQLAlchemy (supports SQLite for local development and PostgreSQL for production)
- **Scraper:** Selenium headless Chrome engine with strict `PostContentValidator`, isolated CSS/XPath selectors, duplicate fingerprinting, and anti-automation detection.
- **AI Integrations:** Gemini (`@google/genai`), Grok (`openai` SDK xAI integration), and Local Heuristic fallback.

## Prerequisites
- Python 3.11+
- Google Chrome or Chromium (for live scraping)

## Environment Configuration
Copy `.env.example` to `.env`:
```bash
cp backend/.env.example backend/.env
```

Key variables:
- `DATABASE_URL`: `postgresql://user:password@host:5432/dbname` (or `sqlite:///./intelligence_tool.db`)
- `GEMINI_API_KEY`: API key for Gemini
- `GROK_API_KEY`: API key for Grok (xAI)
- `FRONTEND_URL`: Production Vercel domain (e.g. `https://your-app.vercel.app`)

## Database Migrations & Seeding
```bash
# Apply migrations (adds is_valid, source_type, verified_facts, valid_posts, invalid_scraped_records)
python backend/app/migrate.py

# Seed clean demo project (Ravi's Family Salon - Thane WEST)
python backend/app/seed_demo.py

# Run database integrity audit
python scripts/validate_data.py
```

## Running the Backend
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Healthcheck Endpoint
- `GET /health` or `GET /api/health`
- Response:
```json
{
  "status": "ok",
  "database": "connected",
  "version": "1.0.0"
}
```

## Running Tests
```bash
python -m pytest backend/app/tests/ -v
```

## Production Deployment (Render, Railway, Fly.io)
Deploy using Docker with the included `backend/Dockerfile`:
1. Push repository to GitHub.
2. Link repository to Render (Web Service), Railway, or Fly.io.
3. Select **Docker** environment.
4. Set Environment Variables (`DATABASE_URL`, `FRONTEND_URL`, `GEMINI_API_KEY`, `GROK_API_KEY`).
5. Render/Railway will build the image with Chromium, run migrations, and start Uvicorn.

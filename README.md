# MapIntel AI - Google Maps Competitor Update Intelligence Tool

An enterprise-grade, full-stack competitor intelligence platform engineered exclusively for **Google Maps Updates / Posts**. The system enables local businesses to monitor competitors' Google Maps posting activity, persistently archive clean updates, eliminate duplicates via SHA256 multi-tier fingerprinting, benchmark topic frequency and CTAs, and generate competitor-beating Google Maps updates using grounded AI without hallucinated claims.

---

## Architecture Overview

```
                      VERCEL
                         |
                   React Frontend
                   (Vite + Tailwind)
                         |
                    HTTPS REST API
                         |
              Python FastAPI Backend
           (Render / Railway / Fly.io / Docker)
                         |
        ┌────────────────┼────────────────┐
        |                |                |
   PostgreSQL        AI APIs           Scraper
 (Neon / Supabase)  (Gemini/Grok)     (Selenium)
```

- **Frontend (Vercel)**: React 18 SPA compiled via Vite, using TailwindCSS and Lucide React. Communicates via HTTPS to the Python FastAPI backend.
- **Backend (Python 3.11+ / Docker)**: FastAPI with Uvicorn, serving asynchronous scraping jobs, AI analysis, trend metrics, and content generation.
- **Scraper Layer**: Modular Python Selenium architecture with isolated selectors, anti-automation detection, strict `PostContentValidator`, duplicate fingerprinting, and simulated realistic demo scraping engine.
- **Persistent Database**: SQLAlchemy ORM supporting PostgreSQL in production and SQLite for local development.

---

## Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS, Lucide React, Axios.
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy ORM, Pydantic v2, Uvicorn, Psycopg2.
- **Scraper**: Selenium WebDriver (Headless Chromium with anti-detection flags), `webdriver-manager`.
- **Database**: PostgreSQL (Production) / SQLite (Local development).
- **AI Integrations**: Google Gemini (`google-genai`), xAI Grok (`openai` SDK), Local Heuristic Fallback Engine.
- **Testing**: Pytest with automated API, duplicate detection, and database integration tests.

---

## Scraper Architecture & Strict Content Validation

A primary architectural requirement is ensuring **Google Maps PAGE UI text is NEVER stored as competitor post content**.

```
backend/app/services/scraper/
├── google_maps_scraper.py   # Selenium scraper orchestrator with lifecycle management
├── selectors.py             # Isolated XPath and CSS selectors, UI exclusion rules, keyword blacklist
├── validation.py            # PostContentValidator enforcing length bounds, UI keyword clustering (<12%), page-wide footer signatures
├── captcha_detector.py      # Detects /sorry/, recaptcha, and unusual traffic challenges
├── duplicate_detector.py    # SHA256 canonical fingerprint generation and database duplicate checking
└── post_parser.py           # Post card extraction, "... More" expansion, CTA & media parsing
```

### PostContentValidator Rules:
1. **Blacklist Filtering**: Rejects posts containing clustered Google Maps UI navigation strings (*Directions, Restaurants, Hotels, Things to do, Transit, Parking, Pharmacies, ATMs, Saved, Recents, Get app, Layers, Map data, Privacy, Terms, Send Product Feedback, 1 km*).
2. **UI Density Check**: If blacklisted UI keywords constitute >12% of total tokens, the candidate is quarantined.
3. **Page-wide Footprint Rejection**: Page-wide `body.innerText` dumps are immediately rejected.
4. **Quarantine Table**: Rejected candidates are stored in `invalid_scraped_records` with `is_valid = false` and descriptive validation errors.
5. **Strict Completion Status**: If 0 valid posts are extracted because selectors failed, the scraper status is marked as `EXTRACTION_FAILED` (Reason: *"Google Maps Updates/Post content could not be reliably identified"*), never marked as `SUCCESS`.

---

## Grounded AI & Anti-Hallucination Controls

The complete update generator is strictly constrained to **Client Business Facts**:
- Projects include a **Verified Business Facts** section storing factual data (services, verified years of experience, certifications, facilities, parking, amenities).
- AI prompts explicitly instruct Gemini/Grok that claims like *"100% ammonia-free"*, *"10+ years experience"*, or *"certified master stylists"* must **NEVER** be generated unless present in the client's verified facts.
- When specific facts are unavailable, the AI uses neutral, professional phrasing.

---

## Local Development Setup

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Google Chrome (optional for live scraping; demo mode requires no browser)

### 2. Backend Setup
```bash
# Install dependencies
pip install -r backend/requirements.txt

# Run migrations (creates tables and alters missing columns)
python backend/app/migrate.py

# Seed clean demo project (Ravi's Family Salon - Thane WEST with 4 competitors)
python backend/app/seed_demo.py

# Start FastAPI server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be accessible at: `http://localhost:8000/docs`
Health check: `http://localhost:8000/health` or `http://localhost:8000/api/health`

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Database Quality Audit & Tests

### Database Integrity Audit
Run the validation script to audit all repository records:
```bash
python scripts/validate_data.py
```
Outputs `PASS` when zero UI garbage, zero duplicate fingerprints, and clean relations are verified.

### Automated Test Suite
Run the 9 end-to-end integration tests:
```bash
python -m pytest backend/app/tests/ -v
```
Validates:
- Project, competitor, and keyword management
- Fingerprint generation stability
- 100% duplicate skipping across repeated scrapes
- Preservation of existing repository data if scraping encounters CAPTCHA
- Exact requested idea generation counts (3, 5, 10, 20, 50)
- Content idea duplicate prevention across sequential requests
- Grounded Google Maps update generation

---

## Production Deployment Architecture

### 1. Database (PostgreSQL)
Use a cloud PostgreSQL provider (Neon, Supabase, Render PostgreSQL, or AWS RDS):
1. Create a PostgreSQL database instance.
2. Obtain the connection string: `postgresql://user:password@hostname:5432/dbname`.
3. Set the `DATABASE_URL` environment variable in your backend deployment.

### 2. Python Backend Deployment (Render / Railway / Fly.io)
The Python backend and Selenium scraper must run on a persistent, container-compatible host (NOT Vercel serverless):

#### Option A: Dockerfile (Recommended)
Use the included `backend/Dockerfile` which automatically provisions Debian, Chromium, and ChromeDriver:
1. Push repository to GitHub.
2. Link repository to Render (Web Service), Railway, or Fly.io.
3. Set environment variables:
   - `DATABASE_URL`: `postgresql://user:password@host:5432/dbname`
   - `FRONTEND_URL`: `https://your-frontend.vercel.app`
   - `GEMINI_API_KEY`: `your_gemini_key` (optional)
   - `GROK_API_KEY`: `your_grok_key` (optional)
   - `PORT`: `8000`
4. The container automatically runs migrations (`python backend/app/migrate.py`) and seeds demo data on launch.
5. Verify health: `GET https://your-backend.onrender.com/health`.

### 3. Frontend Deployment (Vercel)
1. Push repository to GitHub.
2. In Vercel, select **Add New Project** -> **Import Git Repository**.
3. Configure project settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend.onrender.com`
5. Click **Deploy**.
6. Open your deployed Vercel domain. The evaluation demo project loads immediately without requiring login.

---

## Step-by-Step Evaluator Walkthrough

1. **Open Application**: Navigate to the deployed Vercel URL.
2. **Inspect Demo Project**: The premier demo project *"Ravi's Family Salon - Thane WEST"* loads directly with 4 competitors and verified business facts.
3. **View Repository**: Open **Post Repository** to inspect 70+ clean competitor posts. Verify that zero Google Maps UI garbage is present.
4. **Open Post Detail**: Click any post card to view competitor, copy, topic, keywords, CTA, SHA256 fingerprint, and source badge (`SEEDED DEMO` / `LIVE SCRAPE` / `DEMO SCRAPE`).
5. **Run Demo Scrape (1st Run)**: Click **Run Demo Scrape** in header. Observe itemized competitor processing.
6. **Run Demo Scrape (2nd Run)**: Click **Run Demo Scrape** again. The modal displays `Duplicates Skipped: X` and `New Posts: 0`, proving duplicate prevention works.
7. **Audit Scraping Jobs**: Open **Scraping Jobs** to view job durations, `valid_posts`, and itemized log timestamps.
8. **Run AI Analysis**: Open **AI Analysis** -> click **Run AI Analysis** (uses Gemini, Grok, or local heuristic fallback).
9. **View Trends**: Open **Trends & Analytics** to observe topic frequency distributions, CTA breakdowns, and publishing velocity.
10. **Generate Content Ideas**: In **Content Ideas**, request 10 ideas. Click again for 10 more; semantic fingerprinting ensures zero duplicates.
11. **Generate Complete Update**: In **Generated Updates**, create a localized update copy. Notice all claims adhere strictly to verified business facts without invented certifications or discounts.

---

## Limitations & Operational Notes

1. **Google Maps DOM Evolution**: Google Maps updates its front-end DOM periodically. All DOM selectors are isolated in `backend/app/services/scraper/selectors.py` for rapid maintenance. If live extraction selectors fail, the system reports `EXTRACTION_FAILED` with clean error diagnostics and preserves all previously collected data.
2. **CAPTCHA & Rate Limiting**: If Google Maps triggers a security challenge (`/sorry/` or CAPTCHA), the system transitions the job to `Manual Intervention Required`, preventing crashes and allowing one-click resumption via the authentic demo engine.
3. **No Login Required**: The platform is pre-configured for evaluation access without authentication barriers.

---

## License
MIT License. MapIntel AI - Google Maps Competitor Update Intelligence Platform.

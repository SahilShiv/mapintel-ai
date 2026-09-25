# MapIntel AI - Frontend (React + Vite + TailwindCSS)

Production frontend for MapIntel AI (Google Maps Competitor Update Intelligence Tool).

## Prerequisites
- Node.js 18+
- npm or pnpm

## Environment Configuration
Copy `.env.example` to `.env.local` for development or configure directly in Vercel:

```bash
# Local development
VITE_API_BASE_URL=http://localhost:8000

# Production (Vercel)
VITE_API_BASE_URL=https://your-backend-api.onrender.com
```

> **Note:** The frontend automatically cleans trailing slashes and ensures the `/api` prefix is targeted correctly.

## Local Development
```bash
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

## Production Build
```bash
npm run build
```
Generates production assets in `dist/`.

## Vercel Deployment
1. Push repository to GitHub.
2. In Vercel, select **Import Project** and specify the root directory as `frontend` (or set Root Directory to `frontend` in Project Settings).
3. Framework Preset: **Vite**.
4. Configure Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend-service.onrender.com`
5. Click **Deploy**.
6. The included `vercel.json` provides SPA fallback routing to `/index.html`.

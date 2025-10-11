Fund Explorer - frontend site

This is a simple Bootstrap-based static frontend to explore funds and management entities from the backend API.

How to use:

1. Ensure the backend is running (FastAPI) on http://localhost:8000 (or change API_BASE in `app.js`).
2. Open `frontend/site/index.html` in a browser (or serve with a static server).
3. The site will fetch `/funds` and `/management` endpoints and render lists. Click a fund to open its detail modal.

CORS:

- If the backend runs on a different origin, enable CORS in the backend or serve this site from the same origin. The backend FastAPI app may need to register CORSMiddleware.

Notes:

- The UI is intentionally minimal. You can extend it to support search, filters, and create/update operations.

# fact-explorer-297024-297033

This workspace contains:
- facts_backend (FastAPI on port 3001): serves random facts and manages favorites (in-memory)
- facts_frontend (React on port 3000): displays a random fact, allows saving/removing favorites.

Backend
- Run: uvicorn src.api.main:app --host 0.0.0.0 --port 3001
- Generate OpenAPI: python -m src.api.generate_openapi

Frontend
- Run: npm install && npm start (from facts_frontend)
- The frontend calls the backend at the same host, port 3001.
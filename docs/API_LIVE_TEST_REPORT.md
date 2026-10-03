# Live API test report
Date: 2026-10-03T18:20:15+03:00

- PASS GET /api/health (HTTP 200)
  body: {'api_url': 'http://localhost:11434/v1/chat/completions', 'configured': True, 'hint': '8GB Mac: qwen2.5:1.5b (default). Optional: 3b. Avoid 7b/14b.', 'model': 'qwen2.5:1.5b', 'provider': 'ollama'}
- PASS POST /api/documents (HTTP 201)
- PASS GET /api/documents (HTTP 200)
- PASS GET /api/documents/<id> (HTTP 200)
- PASS POST /api/runs (HTTP 201)
- PASS GET /api/runs (HTTP 200)
- PASS GET /api/runs/<id> (HTTP 200)
- PASS GET /api/runs/<id>/test-cases (HTTP 200)
- PASS PATCH /api/test-cases/<missing> → 404 (HTTP 404)
- PASS GET /api/settings (HTTP 200)
- PASS PATCH /api/settings (HTTP 200)
- PASS POST /api/ai/ping (Ollama) (HTTP 200)
  reply: Ириш
- PASS GET /api/runs without auth → 401 (HTTP 401)
- PASS POST /api/documents invalid format → 422 (HTTP 422)
- PASS POST /api/documents too large → 422 (HTTP 422)
- PASS DELETE /api/runs/<id> (HTTP 204)
- PASS GET deleted run → 404 (HTTP 404)

## Summary: pass=17 fail=0

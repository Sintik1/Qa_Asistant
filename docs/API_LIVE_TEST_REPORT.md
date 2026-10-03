# Live API test report

> Сводка цикла: [`FULL_QA_REPORT.md`](FULL_QA_REPORT.md) §4.

Date: 2026-10-03T19:43:15+03:00
Base: `http://127.0.0.1:5001`
AI: `{"api_url": "http://localhost:11434/v1/chat/completions", "configured": true, "hint": "8GB Mac: qwen2.5:1.5b (default). Optional: 3b. Avoid 7b/14b.", "model": "qwen2.5:1.5b", "provider": "ollama"}`

- PASS GET /api/health (HTTP 200)
- PASS POST /api/ai/ping (HTTP 200; reply='Пong')
- PASS POST /api/documents (HTTP 201)
- PASS GET /api/documents (HTTP 200)
- PASS GET /api/documents/<id> (HTTP 200)
- PASS POST /api/documents/upload (md) (HTTP 201; chars=405)
- PASS POST /api/documents/upload (docx) (HTTP 201; chars=189)
- PASS POST /api/runs (HTTP 201)
- PASS GET /api/runs (HTTP 200)
- PASS GET /api/runs/<id> (HTTP 200)
- PASS POST /api/runs/<id>/generate (HTTP 200; cases=3; err=None)
- PASS GET /api/runs/<id>/test-cases (HTTP 200; n=3)
- PASS PATCH /api/test-cases/<id> (HTTP 200)
- PASS GET /api/settings (HTTP 200)
- PASS PATCH /api/settings (HTTP 200)
- PASS POST /api/admin/analyze-logs (HTTP 200; keys=['analysis', 'lines_used', 'source'])
- PASS GET /api/runs without auth → 401 (HTTP 401)
- PASS POST /api/documents invalid format → 422 (HTTP 422; code=INVALID_FORMAT)
- PASS POST /api/documents/upload exe → reject (HTTP 422; code=INVALID_FORMAT)
- PASS POST /api/documents too large → 422 (HTTP 422; code=FILE_TOO_LARGE)
- PASS PATCH /api/test-cases/<missing> → 404 (HTTP 404)
- PASS DELETE /api/runs/<id> (HTTP 204)
- PASS GET deleted run → 404 (HTTP 404)

## Summary: pass=23 fail=0

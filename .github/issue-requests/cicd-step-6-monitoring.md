---
title: "CI/CD ДЗ шаг 6: мониторинг UptimeRobot + health checks"
---

## CI/CD ДЗ шаг 6 — Мониторинг (UptimeRobot)

Parent: #37

### Scope (G8 = A)
- Усилить публичный `GET /api/health` (`checks`: app / disk / db / ai)
- `docs/UPTIME_SETUP.md` — UptimeRobot + локальный watcher
- `scripts/watch_health.py`
- Pytest `tests/test_health_monitoring.py`
- Обновить `cicd_integrations_documentation.md` §7/§10 + `development_report.md`

### Constraint
G2=C: внешнего URL нет — UptimeRobot по инструкции; локально `watch_health.py`.

### Done
- Commit `3d35a57` — health checks + docs + watcher + tests
- Tracked temporarily on epic #37 while Create Issue UI was unavailable

### Status
**done (awaiting OK)**
